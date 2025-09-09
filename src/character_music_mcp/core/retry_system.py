#!/usr/bin/env python3
"""
Retry System for Dynamic Suno Data Integration

This module provides automatic retry logic for failed operations with exponential backoff,
circuit breaker patterns, and comprehensive error monitoring.
"""

import asyncio
import json
import logging
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# ================================================================================================
# ENUMS AND DATA MODELS
# ================================================================================================

class RetryStrategy(Enum):
    """Types of retry strategies"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    JITTERED_BACKOFF = "jittered_backoff"
    CIRCUIT_BREAKER = "circuit_breaker"

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class OperationType(Enum):
    """Types of operations that can be retried"""
    DOWNLOAD = "download"
    PARSE = "parse"
    CACHE_READ = "cache_read"
    CACHE_WRITE = "cache_write"
    DATA_VALIDATION = "data_validation"
    NETWORK_REQUEST = "network_request"

@dataclass
class RetryPolicy:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    base_delay: float = 1.0  # Base delay in seconds
    max_delay: float = 60.0  # Maximum delay in seconds
    backoff_multiplier: float = 2.0
    jitter: bool = True  # Add random jitter to delays
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF

    # Circuit breaker settings
    failure_threshold: int = 5  # Failures before opening circuit
    recovery_timeout: int = 30  # Seconds before trying half-open
    success_threshold: int = 2  # Successes needed to close circuit

    # Retry conditions
    retryable_exceptions: List[str] = field(default_factory=lambda: [
        'ConnectionError', 'TimeoutError', 'HTTPError', 'NetworkError'
    ])
    non_retryable_exceptions: List[str] = field(default_factory=lambda: [
        'AuthenticationError', 'PermissionError', 'ValidationError'
    ])

@dataclass
class RetryAttempt:
    """Record of a single retry attempt"""
    attempt_number: int
    timestamp: datetime
    delay_before: float
    error: Optional[str] = None
    success: bool = False
    response_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'attempt_number': self.attempt_number,
            'timestamp': self.timestamp.isoformat(),
            'delay_before': self.delay_before,
            'error': self.error,
            'success': self.success,
            'response_time': self.response_time
        }

@dataclass
class RetrySession:
    """Complete retry session for an operation"""
    operation_id: str
    operation_type: OperationType
    start_time: datetime
    end_time: Optional[datetime] = None
    total_attempts: int = 0
    final_success: bool = False
    attempts: List[RetryAttempt] = field(default_factory=list)
    policy_used: Optional[RetryPolicy] = None

    @property
    def duration(self) -> Optional[timedelta]:
        """Total duration of retry session"""
        if self.end_time:
            return self.end_time - self.start_time
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'operation_id': self.operation_id,
            'operation_type': self.operation_type.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_attempts': self.total_attempts,
            'final_success': self.final_success,
            'attempts': [attempt.to_dict() for attempt in self.attempts],
            'duration_seconds': self.duration.total_seconds() if self.duration else None
        }

@dataclass
class CircuitBreakerState:
    """State of a circuit breaker"""
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    next_attempt_time: Optional[datetime] = None

# ================================================================================================
# RETRY SYSTEM
# ================================================================================================

class RetrySystem:
    """Comprehensive retry system with circuit breaker and monitoring"""

    def __init__(self, storage_path: str = "./data/retry_system"):
        self.storage_path = Path(storage_path)
        self.retry_policies: Dict[str, RetryPolicy] = {}
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.retry_sessions: List[RetrySession] = []
        self.active_sessions: Dict[str, RetrySession] = {}
        self.initialized = False

        # Setup default policies
        self._setup_default_policies()

    async def initialize(self) -> None:
        """Initialize the retry system"""
        logger.info("Initializing RetrySystem")

        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Load previous state
        await self._load_state()

        # Start background tasks
        asyncio.create_task(self._circuit_breaker_monitor())
        asyncio.create_task(self._cleanup_old_sessions())

        self.initialized = True
        logger.info("RetrySystem initialized successfully")

    async def execute_with_retry(self,
                               operation: Callable[[], Awaitable[Any]],
                               operation_id: str,
                               operation_type: OperationType,
                               policy_name: str = "default") -> Any:
        """
        Execute an operation with retry logic
        
        Args:
            operation: Async function to execute
            operation_id: Unique identifier for the operation
            operation_type: Type of operation being performed
            policy_name: Name of retry policy to use
            
        Returns:
            Result of the operation
            
        Raises:
            Exception: If all retry attempts fail
        """
        if not self.initialized:
            raise RuntimeError("RetrySystem not initialized")

        policy = self.retry_policies.get(policy_name, self.retry_policies["default"])
        circuit_key = f"{operation_type.value}:{operation_id}"

        # Check circuit breaker
        if not self._can_attempt_operation(circuit_key, policy):
            raise Exception(f"Circuit breaker is OPEN for {circuit_key}")

        # Start retry session
        session = RetrySession(
            operation_id=operation_id,
            operation_type=operation_type,
            start_time=datetime.now(),
            policy_used=policy
        )
        self.active_sessions[operation_id] = session

        last_exception = None

        for attempt_num in range(1, policy.max_attempts + 1):
            # Calculate delay for this attempt
            if attempt_num > 1:
                delay = self._calculate_delay(attempt_num - 1, policy)
                logger.debug(f"Waiting {delay:.2f}s before retry attempt {attempt_num}")
                await asyncio.sleep(delay)
            else:
                delay = 0.0

            # Record attempt start
            attempt = RetryAttempt(
                attempt_number=attempt_num,
                timestamp=datetime.now(),
                delay_before=delay
            )

            try:
                # Execute the operation
                start_time = datetime.now()
                result = await operation()
                end_time = datetime.now()

                # Success!
                attempt.success = True
                attempt.response_time = (end_time - start_time).total_seconds()
                session.attempts.append(attempt)
                session.total_attempts = attempt_num
                session.final_success = True
                session.end_time = end_time

                # Update circuit breaker
                self._record_success(circuit_key, policy)

                # Complete session
                self.retry_sessions.append(session)
                del self.active_sessions[operation_id]

                logger.info(f"Operation {operation_id} succeeded on attempt {attempt_num}")
                return result

            except Exception as e:
                last_exception = e
                attempt.error = str(e)
                attempt.response_time = (datetime.now() - start_time).total_seconds()
                session.attempts.append(attempt)

                # Check if this exception is retryable
                if not self._is_retryable_exception(e, policy):
                    logger.warning(f"Non-retryable exception for {operation_id}: {e}")
                    break

                # Record failure for circuit breaker
                self._record_failure(circuit_key, policy)

                logger.warning(f"Attempt {attempt_num} failed for {operation_id}: {e}")

                # Check if circuit breaker should open
                if not self._can_attempt_operation(circuit_key, policy):
                    logger.error(f"Circuit breaker opened for {circuit_key}")
                    break

        # All attempts failed
        session.total_attempts = len(session.attempts)
        session.final_success = False
        session.end_time = datetime.now()

        # Complete session
        self.retry_sessions.append(session)
        del self.active_sessions[operation_id]

        logger.error(f"Operation {operation_id} failed after {session.total_attempts} attempts")

        if last_exception:
            raise last_exception
        else:
            raise Exception(f"Operation {operation_id} failed after {session.total_attempts} attempts")

    def add_retry_policy(self, name: str, policy: RetryPolicy) -> None:
        """Add or update a retry policy"""
        self.retry_policies[name] = policy
        logger.info(f"Added retry policy: {name}")

    def get_circuit_breaker_status(self, operation_key: str) -> CircuitBreakerState:
        """Get current circuit breaker status"""
        return self.circuit_breakers.get(operation_key, CircuitBreakerState())

    def reset_circuit_breaker(self, operation_key: str) -> None:
        """Manually reset a circuit breaker"""
        if operation_key in self.circuit_breakers:
            self.circuit_breakers[operation_key] = CircuitBreakerState()
            logger.info(f"Reset circuit breaker for {operation_key}")

    def get_retry_statistics(self) -> Dict[str, Any]:
        """Get comprehensive retry statistics"""
        if not self.retry_sessions:
            return {'total_sessions': 0}

        stats = {
            'total_sessions': len(self.retry_sessions),
            'success_rate': 0.0,
            'average_attempts': 0.0,
            'average_duration': 0.0,
            'operations_by_type': {},
            'circuit_breaker_states': {},
            'recent_failures': [],
            'retry_patterns': {}
        }

        # Calculate basic statistics
        successful_sessions = [s for s in self.retry_sessions if s.final_success]
        stats['success_rate'] = len(successful_sessions) / len(self.retry_sessions)
        stats['average_attempts'] = sum(s.total_attempts for s in self.retry_sessions) / len(self.retry_sessions)

        # Calculate average duration
        durations = [s.duration.total_seconds() for s in self.retry_sessions if s.duration]
        if durations:
            stats['average_duration'] = sum(durations) / len(durations)

        # Operations by type
        for session in self.retry_sessions:
            op_type = session.operation_type.value
            if op_type not in stats['operations_by_type']:
                stats['operations_by_type'][op_type] = {
                    'total': 0, 'successful': 0, 'failed': 0
                }

            stats['operations_by_type'][op_type]['total'] += 1
            if session.final_success:
                stats['operations_by_type'][op_type]['successful'] += 1
            else:
                stats['operations_by_type'][op_type]['failed'] += 1

        # Circuit breaker states
        for key, state in self.circuit_breakers.items():
            stats['circuit_breaker_states'][key] = {
                'state': state.state.value,
                'failure_count': state.failure_count,
                'success_count': state.success_count,
                'last_failure': state.last_failure_time.isoformat() if state.last_failure_time else None
            }

        # Recent failures
        failed_sessions = [s for s in self.retry_sessions if not s.final_success]
        recent_failures = sorted(failed_sessions, key=lambda x: x.start_time, reverse=True)[:10]
        stats['recent_failures'] = [
            {
                'operation_id': s.operation_id,
                'operation_type': s.operation_type.value,
                'start_time': s.start_time.isoformat(),
                'attempts': s.total_attempts,
                'final_error': s.attempts[-1].error if s.attempts else None
            }
            for s in recent_failures
        ]

        return stats

    async def schedule_retry(self, operation: Callable[[], Awaitable[Any]],
                           operation_id: str,
                           operation_type: OperationType,
                           delay_minutes: int = 5,
                           policy_name: str = "default") -> None:
        """
        Schedule a retry operation for later execution
        
        Args:
            operation: Async function to execute
            operation_id: Unique identifier for the operation
            operation_type: Type of operation being performed
            delay_minutes: Delay before retry in minutes
            policy_name: Name of retry policy to use
        """
        logger.info(f"Scheduling retry for {operation_id} in {delay_minutes} minutes")

        async def delayed_retry():
            await asyncio.sleep(delay_minutes * 60)
            try:
                await self.execute_with_retry(operation, operation_id, operation_type, policy_name)
                logger.info(f"Scheduled retry for {operation_id} completed successfully")
            except Exception as e:
                logger.error(f"Scheduled retry for {operation_id} failed: {e}")

        # Start the delayed retry as a background task
        asyncio.create_task(delayed_retry())

    # Private methods

    def _setup_default_policies(self) -> None:
        """Setup default retry policies"""
        # Default policy - exponential backoff
        self.retry_policies["default"] = RetryPolicy(
            max_attempts=3,
            base_delay=1.0,
            max_delay=30.0,
            backoff_multiplier=2.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF
        )

        # Network operations - more aggressive retry
        self.retry_policies["network"] = RetryPolicy(
            max_attempts=5,
            base_delay=2.0,
            max_delay=60.0,
            backoff_multiplier=2.0,
            strategy=RetryStrategy.JITTERED_BACKOFF,
            failure_threshold=3,
            recovery_timeout=60
        )

        # Parse operations - limited retry
        self.retry_policies["parse"] = RetryPolicy(
            max_attempts=2,
            base_delay=0.5,
            max_delay=5.0,
            backoff_multiplier=2.0,
            strategy=RetryStrategy.FIXED_DELAY
        )

        # Cache operations - quick retry
        self.retry_policies["cache"] = RetryPolicy(
            max_attempts=3,
            base_delay=0.1,
            max_delay=2.0,
            backoff_multiplier=1.5,
            strategy=RetryStrategy.LINEAR_BACKOFF
        )

        # Critical operations - circuit breaker
        self.retry_policies["critical"] = RetryPolicy(
            max_attempts=5,
            base_delay=1.0,
            max_delay=120.0,
            backoff_multiplier=3.0,
            strategy=RetryStrategy.CIRCUIT_BREAKER,
            failure_threshold=2,
            recovery_timeout=300,
            success_threshold=3
        )

    def _calculate_delay(self, attempt_number: int, policy: RetryPolicy) -> float:
        """Calculate delay before next retry attempt"""
        if policy.strategy == RetryStrategy.FIXED_DELAY:
            delay = policy.base_delay

        elif policy.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = policy.base_delay * attempt_number

        elif policy.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = policy.base_delay * (policy.backoff_multiplier ** (attempt_number - 1))

        elif policy.strategy == RetryStrategy.JITTERED_BACKOFF:
            base_delay = policy.base_delay * (policy.backoff_multiplier ** (attempt_number - 1))
            jitter = random.uniform(0.5, 1.5)  # ±50% jitter
            delay = base_delay * jitter

        else:  # Default to exponential backoff
            delay = policy.base_delay * (policy.backoff_multiplier ** (attempt_number - 1))

        # Apply maximum delay limit
        delay = min(delay, policy.max_delay)

        # Add small random jitter if enabled
        if policy.jitter and policy.strategy != RetryStrategy.JITTERED_BACKOFF:
            jitter = random.uniform(0.9, 1.1)  # ±10% jitter
            delay *= jitter

        return delay

    def _is_retryable_exception(self, exception: Exception, policy: RetryPolicy) -> bool:
        """Check if an exception is retryable based on policy"""
        exception_name = type(exception).__name__
        exception_str = str(exception).lower()

        # Check non-retryable exceptions first
        for non_retryable in policy.non_retryable_exceptions:
            if non_retryable.lower() in exception_name.lower() or non_retryable.lower() in exception_str:
                return False

        # Check retryable exceptions
        for retryable in policy.retryable_exceptions:
            if retryable.lower() in exception_name.lower() or retryable.lower() in exception_str:
                return True

        # Default behavior - retry network-related errors
        network_indicators = ['connection', 'timeout', 'network', 'dns', 'socket', 'http']
        if any(indicator in exception_str for indicator in network_indicators):
            return True

        # Don't retry by default for unknown exceptions
        return False

    def _can_attempt_operation(self, circuit_key: str, policy: RetryPolicy) -> bool:
        """Check if operation can be attempted based on circuit breaker state"""
        if policy.strategy != RetryStrategy.CIRCUIT_BREAKER:
            return True  # No circuit breaker for this policy

        if circuit_key not in self.circuit_breakers:
            self.circuit_breakers[circuit_key] = CircuitBreakerState()

        circuit = self.circuit_breakers[circuit_key]
        now = datetime.now()

        if circuit.state == CircuitState.CLOSED:
            return True

        elif circuit.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if (circuit.last_failure_time and
                now - circuit.last_failure_time > timedelta(seconds=policy.recovery_timeout)):
                # Move to half-open state
                circuit.state = CircuitState.HALF_OPEN
                circuit.success_count = 0
                logger.info(f"Circuit breaker for {circuit_key} moved to HALF_OPEN")
                return True
            return False

        elif circuit.state == CircuitState.HALF_OPEN:
            return True  # Allow attempts in half-open state

        return False

    def _record_success(self, circuit_key: str, policy: RetryPolicy) -> None:
        """Record a successful operation for circuit breaker"""
        if policy.strategy != RetryStrategy.CIRCUIT_BREAKER:
            return

        if circuit_key not in self.circuit_breakers:
            self.circuit_breakers[circuit_key] = CircuitBreakerState()

        circuit = self.circuit_breakers[circuit_key]
        circuit.success_count += 1
        circuit.last_success_time = datetime.now()

        if circuit.state == CircuitState.HALF_OPEN:
            if circuit.success_count >= policy.success_threshold:
                # Close the circuit
                circuit.state = CircuitState.CLOSED
                circuit.failure_count = 0
                circuit.success_count = 0
                logger.info(f"Circuit breaker for {circuit_key} CLOSED after successful recovery")

        elif circuit.state == CircuitState.CLOSED:
            # Reset failure count on success
            circuit.failure_count = 0

    def _record_failure(self, circuit_key: str, policy: RetryPolicy) -> None:
        """Record a failed operation for circuit breaker"""
        if policy.strategy != RetryStrategy.CIRCUIT_BREAKER:
            return

        if circuit_key not in self.circuit_breakers:
            self.circuit_breakers[circuit_key] = CircuitBreakerState()

        circuit = self.circuit_breakers[circuit_key]
        circuit.failure_count += 1
        circuit.last_failure_time = datetime.now()

        if circuit.state == CircuitState.HALF_OPEN:
            # Failure in half-open state - go back to open
            circuit.state = CircuitState.OPEN
            circuit.success_count = 0
            logger.warning(f"Circuit breaker for {circuit_key} returned to OPEN state")

        elif circuit.state == CircuitState.CLOSED:
            if circuit.failure_count >= policy.failure_threshold:
                # Open the circuit
                circuit.state = CircuitState.OPEN
                circuit.next_attempt_time = datetime.now() + timedelta(seconds=policy.recovery_timeout)
                logger.error(f"Circuit breaker for {circuit_key} OPENED after {circuit.failure_count} failures")

    async def _circuit_breaker_monitor(self) -> None:
        """Background task to monitor circuit breaker states"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds

                now = datetime.now()
                for circuit_key, circuit in self.circuit_breakers.items():
                    if (circuit.state == CircuitState.OPEN and
                        circuit.next_attempt_time and
                        now >= circuit.next_attempt_time):

                        # Time to try half-open
                        circuit.state = CircuitState.HALF_OPEN
                        circuit.success_count = 0
                        logger.info(f"Circuit breaker for {circuit_key} automatically moved to HALF_OPEN")

            except Exception as e:
                logger.error(f"Error in circuit breaker monitor: {e}")

    async def _cleanup_old_sessions(self) -> None:
        """Background task to cleanup old retry sessions"""
        while True:
            try:
                await asyncio.sleep(3600)  # Cleanup every hour

                # Keep only sessions from last 24 hours
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.retry_sessions = [
                    session for session in self.retry_sessions
                    if session.start_time > cutoff_time
                ]

                logger.debug(f"Cleaned up old retry sessions, {len(self.retry_sessions)} remaining")

            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")

    async def _load_state(self) -> None:
        """Load previous state from disk"""
        # Load circuit breaker states
        circuit_file = self.storage_path / "circuit_breakers.json"
        if circuit_file.exists():
            try:
                with open(circuit_file, 'r') as f:
                    circuit_data = json.load(f)

                for key, data in circuit_data.items():
                    state = CircuitBreakerState(
                        state=CircuitState(data['state']),
                        failure_count=data['failure_count'],
                        success_count=data['success_count'],
                        last_failure_time=datetime.fromisoformat(data['last_failure_time']) if data.get('last_failure_time') else None,
                        last_success_time=datetime.fromisoformat(data['last_success_time']) if data.get('last_success_time') else None,
                        next_attempt_time=datetime.fromisoformat(data['next_attempt_time']) if data.get('next_attempt_time') else None
                    )
                    self.circuit_breakers[key] = state

                logger.debug(f"Loaded {len(self.circuit_breakers)} circuit breaker states")
            except Exception as e:
                logger.warning(f"Failed to load circuit breaker states: {e}")

    async def save_state(self) -> None:
        """Save current state to disk"""
        if not self.initialized:
            return

        # Save circuit breaker states
        circuit_file = self.storage_path / "circuit_breakers.json"
        circuit_data = {}
        for key, state in self.circuit_breakers.items():
            circuit_data[key] = {
                'state': state.state.value,
                'failure_count': state.failure_count,
                'success_count': state.success_count,
                'last_failure_time': state.last_failure_time.isoformat() if state.last_failure_time else None,
                'last_success_time': state.last_success_time.isoformat() if state.last_success_time else None,
                'next_attempt_time': state.next_attempt_time.isoformat() if state.next_attempt_time else None
            }

        with open(circuit_file, 'w') as f:
            json.dump(circuit_data, f, indent=2)

        # Save recent retry sessions
        sessions_file = self.storage_path / "retry_sessions.json"
        recent_sessions = self.retry_sessions[-100:]  # Keep last 100 sessions
        sessions_data = [session.to_dict() for session in recent_sessions]

        with open(sessions_file, 'w') as f:
            json.dump(sessions_data, f, indent=2)

        logger.debug("Saved retry system state to disk")
