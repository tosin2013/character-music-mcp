#!/usr/bin/env python3
"""
Mock Context Classes for Testing

Provides consistent mock context objects for testing MCP server functionality
without requiring actual MCP server initialization.
"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MockMessage:
    """Mock message for context logging"""
    level: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)


class MockContext:
    """Mock MCP context for testing"""
    
    def __init__(self, session_id: str = "test_session"):
        self.session_id = session_id
        self.messages: List[MockMessage] = []
        self.errors: List[MockMessage] = []
        self.warnings: List[MockMessage] = []
        self.info_messages: List[MockMessage] = []
        self.debug_messages: List[MockMessage] = []
        
        # Mock request/response tracking
        self.request_count = 0
        self.response_times: List[float] = []
        self.last_request_time: Optional[datetime] = None
        
        # Mock resource tracking
        self.memory_usage: List[int] = []
        self.processing_times: List[float] = []
        
        # Mock user preferences
        self.user_preferences = {
            "output_format": "detailed",
            "include_debug": False,
            "max_characters": 5,
            "preferred_genres": ["indie", "alternative"]
        }
    
    async def info(self, message: str) -> None:
        """Mock info logging"""
        mock_msg = MockMessage("INFO", message)
        self.messages.append(mock_msg)
        self.info_messages.append(mock_msg)
    
    async def error(self, message: str) -> None:
        """Mock error logging"""
        mock_msg = MockMessage("ERROR", message)
        self.messages.append(mock_msg)
        self.errors.append(mock_msg)
    
    async def warning(self, message: str) -> None:
        """Mock warning logging"""
        mock_msg = MockMessage("WARNING", message)
        self.messages.append(mock_msg)
        self.warnings.append(mock_msg)
    
    async def debug(self, message: str) -> None:
        """Mock debug logging"""
        mock_msg = MockMessage("DEBUG", message)
        self.messages.append(mock_msg)
        self.debug_messages.append(mock_msg)
    
    def get_messages_by_level(self, level: str) -> List[MockMessage]:
        """Get messages filtered by level"""
        return [msg for msg in self.messages if msg.level == level]
    
    def get_all_messages(self) -> List[str]:
        """Get all messages as strings"""
        return [f"{msg.level}: {msg.message}" for msg in self.messages]
    
    def clear_messages(self) -> None:
        """Clear all logged messages"""
        self.messages.clear()
        self.errors.clear()
        self.warnings.clear()
        self.info_messages.clear()
        self.debug_messages.clear()
    
    def simulate_request_start(self) -> None:
        """Simulate start of request processing"""
        self.request_count += 1
        self.last_request_time = datetime.now()
    
    def simulate_request_end(self, processing_time: float = 0.5) -> None:
        """Simulate end of request processing"""
        self.response_times.append(processing_time)
        self.processing_times.append(processing_time)
    
    def simulate_memory_usage(self, memory_mb: int) -> None:
        """Simulate memory usage tracking"""
        self.memory_usage.append(memory_mb)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            "total_requests": self.request_count,
            "average_response_time": sum(self.response_times) / len(self.response_times) if self.response_times else 0,
            "max_response_time": max(self.response_times) if self.response_times else 0,
            "min_response_time": min(self.response_times) if self.response_times else 0,
            "average_memory_usage": sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0,
            "peak_memory_usage": max(self.memory_usage) if self.memory_usage else 0,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }
    
    def has_errors(self) -> bool:
        """Check if any errors were logged"""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if any warnings were logged"""
        return len(self.warnings) > 0
    
    def get_last_error(self) -> Optional[str]:
        """Get the last error message"""
        return self.errors[-1].message if self.errors else None
    
    def get_last_info(self) -> Optional[str]:
        """Get the last info message"""
        return self.info_messages[-1].message if self.info_messages else None


class MockBatchContext(MockContext):
    """Mock context for batch processing tests"""
    
    def __init__(self, batch_size: int = 10, session_id: str = "batch_test_session"):
        super().__init__(session_id)
        self.batch_size = batch_size
        self.batch_results: List[Dict[str, Any]] = []
        self.current_batch = 0
        self.items_processed = 0
    
    async def start_batch(self, batch_id: int) -> None:
        """Start processing a new batch"""
        self.current_batch = batch_id
        await self.info(f"Starting batch {batch_id}")
    
    async def process_batch_item(self, item_id: str, result: Dict[str, Any]) -> None:
        """Process an item in the current batch"""
        self.items_processed += 1
        self.batch_results.append({
            "batch_id": self.current_batch,
            "item_id": item_id,
            "result": result,
            "timestamp": datetime.now()
        })
        await self.debug(f"Processed item {item_id} in batch {self.current_batch}")
    
    async def end_batch(self) -> Dict[str, Any]:
        """End current batch and return summary"""
        batch_items = [r for r in self.batch_results if r["batch_id"] == self.current_batch]
        summary = {
            "batch_id": self.current_batch,
            "items_processed": len(batch_items),
            "success_count": len([r for r in batch_items if "error" not in r["result"]]),
            "error_count": len([r for r in batch_items if "error" in r["result"]])
        }
        await self.info(f"Completed batch {self.current_batch}: {summary}")
        return summary
    
    def get_batch_results(self, batch_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get results for specific batch or all batches"""
        if batch_id is not None:
            return [r for r in self.batch_results if r["batch_id"] == batch_id]
        return self.batch_results


class MockConcurrentContext(MockContext):
    """Mock context for concurrent processing tests"""
    
    def __init__(self, max_concurrent: int = 5, session_id: str = "concurrent_test_session"):
        super().__init__(session_id)
        self.max_concurrent = max_concurrent
        self.active_requests: Dict[str, datetime] = {}
        self.completed_requests: Dict[str, Dict[str, Any]] = {}
        self.concurrent_peak = 0
    
    async def start_concurrent_request(self, request_id: str) -> bool:
        """Start a concurrent request if under limit"""
        if len(self.active_requests) >= self.max_concurrent:
            await self.warning(f"Concurrent limit reached, queuing request {request_id}")
            return False
        
        self.active_requests[request_id] = datetime.now()
        self.concurrent_peak = max(self.concurrent_peak, len(self.active_requests))
        await self.debug(f"Started concurrent request {request_id}")
        return True
    
    async def complete_concurrent_request(self, request_id: str, result: Dict[str, Any]) -> None:
        """Complete a concurrent request"""
        if request_id in self.active_requests:
            start_time = self.active_requests.pop(request_id)
            duration = (datetime.now() - start_time).total_seconds()
            
            self.completed_requests[request_id] = {
                "result": result,
                "duration": duration,
                "completed_at": datetime.now()
            }
            
            await self.debug(f"Completed concurrent request {request_id} in {duration:.2f}s")
    
    def get_concurrent_stats(self) -> Dict[str, Any]:
        """Get concurrent processing statistics"""
        return {
            "max_concurrent": self.max_concurrent,
            "concurrent_peak": self.concurrent_peak,
            "active_requests": len(self.active_requests),
            "completed_requests": len(self.completed_requests),
            "average_duration": sum(r["duration"] for r in self.completed_requests.values()) / len(self.completed_requests) if self.completed_requests else 0
        }


class MockPerformanceContext(MockContext):
    """Mock context for performance testing"""
    
    def __init__(self, session_id: str = "performance_test_session"):
        super().__init__(session_id)
        self.performance_metrics: Dict[str, List[float]] = {
            "character_analysis_time": [],
            "persona_generation_time": [],
            "command_generation_time": [],
            "total_workflow_time": []
        }
        self.resource_usage: Dict[str, List[int]] = {
            "memory_mb": [],
            "cpu_percent": []
        }
        self.throughput_metrics: Dict[str, int] = {
            "characters_per_second": 0,
            "personas_per_second": 0,
            "commands_per_second": 0
        }
    
    async def record_performance_metric(self, metric_name: str, value: float) -> None:
        """Record a performance metric"""
        if metric_name not in self.performance_metrics:
            self.performance_metrics[metric_name] = []
        
        self.performance_metrics[metric_name].append(value)
        await self.debug(f"Recorded {metric_name}: {value:.3f}")
    
    async def record_resource_usage(self, resource_name: str, value: int) -> None:
        """Record resource usage"""
        if resource_name not in self.resource_usage:
            self.resource_usage[resource_name] = []
        
        self.resource_usage[resource_name].append(value)
        await self.debug(f"Recorded {resource_name}: {value}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        summary = {}
        
        for metric_name, values in self.performance_metrics.items():
            if values:
                summary[metric_name] = {
                    "count": len(values),
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "total": sum(values)
                }
        
        for resource_name, values in self.resource_usage.items():
            if values:
                summary[f"{resource_name}_stats"] = {
                    "average": sum(values) / len(values),
                    "peak": max(values),
                    "samples": len(values)
                }
        
        return summary
    
    def check_performance_thresholds(self, thresholds: Dict[str, float]) -> Dict[str, bool]:
        """Check if performance metrics meet specified thresholds"""
        results = {}
        
        for metric_name, threshold in thresholds.items():
            if metric_name in self.performance_metrics:
                values = self.performance_metrics[metric_name]
                if values:
                    average = sum(values) / len(values)
                    results[metric_name] = average <= threshold
                else:
                    results[metric_name] = True  # No data means threshold met
            else:
                results[metric_name] = True  # Unknown metric means threshold met
        
        return results


# Factory functions for easy mock creation
def create_mock_context(context_type: str = "basic", **kwargs) -> MockContext:
    """Factory function to create appropriate mock context"""
    if context_type == "basic":
        return MockContext(**kwargs)
    elif context_type == "batch":
        return MockBatchContext(**kwargs)
    elif context_type == "concurrent":
        return MockConcurrentContext(**kwargs)
    elif context_type == "performance":
        return MockPerformanceContext(**kwargs)
    else:
        raise ValueError(f"Unknown context type: {context_type}")


def create_test_contexts(count: int = 3) -> List[MockContext]:
    """Create multiple mock contexts for parallel testing"""
    return [MockContext(session_id=f"test_session_{i}") for i in range(count)]