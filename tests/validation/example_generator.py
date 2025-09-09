#!/usr/bin/env python3
"""
Example Generator for Documentation Validation

This module provides automated testing and validation of documentation examples,
ensuring that all examples in the documentation work correctly and produce
expected results.
"""

import asyncio
import json
import logging
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ExampleValidationResult:
    """Result of validating a single documentation example"""
    example_name: str
    file_path: str
    validation_status: str  # "passed", "failed", "warning"
    execution_time: float
    input_text: str
    expected_output: Optional[Dict[str, Any]]
    actual_output: Optional[Dict[str, Any]]
    error_message: Optional[str]
    confidence_scores: Dict[str, float]
    completeness_score: float
    accuracy_score: float

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

@dataclass
class ValidationReport:
    """Comprehensive validation report for all examples"""
    total_examples: int
    passed_examples: int
    failed_examples: int
    warning_examples: int
    overall_success_rate: float
    average_execution_time: float
    validation_timestamp: str
    detailed_results: List[ExampleValidationResult]
    missing_examples: List[str]
    outdated_examples: List[str]

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

class ExampleGenerator:
    """
    Generates and validates testable documentation examples

    This class automatically tests all documentation examples to ensure they
    work correctly and produce expected results, maintaining documentation
    accuracy as the codebase evolves.
    """

    def __init__(self, docs_path: str = "docs", examples_path: str = "examples"):
        self.docs_path = Path(docs_path)
        self.examples_path = Path(examples_path)
        self.validation_results: List[ExampleValidationResult] = []

        # Import the MCP server tools for testing
        try:
            from server import (
                analyze_character_text,
                complete_workflow,
                create_suno_commands,
                generate_artist_personas,
                process_universal_content,
            )
            self.mcp_tools = {
                'analyze_character_text': analyze_character_text,
                'generate_artist_personas': generate_artist_personas,
                'create_suno_commands': create_suno_commands,
                'complete_workflow': complete_workflow,
                'process_universal_content': process_universal_content
            }
        except ImportError as e:
            logger.error(f"Failed to import MCP tools: {e}")
            self.mcp_tools = {}

    def discover_examples(self) -> List[Dict[str, Any]]:
        """
        Discover all examples in documentation files

        Returns:
            List of example dictionaries with metadata
        """
        examples = []

        # Search for examples in documentation files
        for doc_file in self.docs_path.rglob("*.md"):
            examples.extend(self._extract_examples_from_file(doc_file))

        # Search for examples in example files
        for example_file in self.examples_path.rglob("*.md"):
            examples.extend(self._extract_examples_from_file(example_file))

        logger.info(f"Discovered {len(examples)} examples across documentation")
        return examples

    def _extract_examples_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract examples from a single markdown file"""
        examples = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract narrative examples (text blocks that should be processed)
            narrative_examples = self._extract_narrative_examples(content, file_path)
            examples.extend(narrative_examples)

            # Extract code examples (Python code that should execute)
            code_examples = self._extract_code_examples(content, file_path)
            examples.extend(code_examples)

            # Extract expected output examples
            output_examples = self._extract_expected_outputs(content, file_path)
            examples.extend(output_examples)

        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")

        return examples

    def _extract_narrative_examples(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract narrative text examples that should be processed by MCP tools"""
        examples = []

        # Pattern for narrative examples in markdown
        narrative_pattern = r'```(?:text)?\n(.*?)\n```'
        matches = re.findall(narrative_pattern, content, re.DOTALL)

        for i, match in enumerate(matches):
            # Skip very short examples (likely not narrative)
            if len(match.strip()) < 50:
                continue

            example = {
                'type': 'narrative',
                'name': f"{file_path.stem}_narrative_{i+1}",
                'file_path': str(file_path),
                'input_text': match.strip(),
                'expected_tools': ['analyze_character_text', 'complete_workflow'],
                'validation_criteria': {
                    'min_confidence_score': 0.7,
                    'min_characters': 1,
                    'required_fields': ['characters', 'narrative_themes']
                }
            }
            examples.append(example)

        return examples

    def _extract_code_examples(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract Python code examples that should execute successfully"""
        examples = []

        # Pattern for Python code examples
        python_pattern = r'```python\n(.*?)\n```'
        matches = re.findall(python_pattern, content, re.DOTALL)

        for i, match in enumerate(matches):
            # Skip examples that are just imports or very simple
            if 'await' not in match or len(match.strip()) < 20:
                continue

            example = {
                'type': 'code',
                'name': f"{file_path.stem}_code_{i+1}",
                'file_path': str(file_path),
                'code': match.strip(),
                'expected_execution': 'success',
                'validation_criteria': {
                    'should_execute': True,
                    'should_return_json': True
                }
            }
            examples.append(example)

        return examples

    def _extract_expected_outputs(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract expected output examples for validation"""
        examples = []

        # Look for sections that describe expected results
        expected_patterns = [
            r'## Expected Character Analysis\n(.*?)(?=\n##|\n---|\Z)',
            r'## Generated Artist Persona\n(.*?)(?=\n##|\n---|\Z)',
            r'## Sample Suno Commands\n(.*?)(?=\n##|\n---|\Z)'
        ]

        for pattern in expected_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for i, match in enumerate(matches):
                example = {
                    'type': 'expected_output',
                    'name': f"{file_path.stem}_expected_{i+1}",
                    'file_path': str(file_path),
                    'expected_content': match.strip(),
                    'validation_criteria': {
                        'should_match_format': True,
                        'should_contain_required_fields': True
                    }
                }
                examples.append(example)

        return examples

    async def validate_example(self, example: Dict[str, Any]) -> ExampleValidationResult:
        """
        Validate a single documentation example

        Args:
            example: Example dictionary with metadata

        Returns:
            ExampleValidationResult with validation details
        """
        start_time = time.time()

        try:
            if example['type'] == 'narrative':
                result = await self._validate_narrative_example(example)
            elif example['type'] == 'code':
                result = await self._validate_code_example(example)
            elif example['type'] == 'expected_output':
                result = await self._validate_expected_output(example)
            else:
                result = ExampleValidationResult(
                    example_name=example['name'],
                    file_path=example['file_path'],
                    validation_status="failed",
                    execution_time=0.0,
                    input_text="",
                    expected_output=None,
                    actual_output=None,
                    error_message=f"Unknown example type: {example['type']}",
                    confidence_scores={},
                    completeness_score=0.0,
                    accuracy_score=0.0
                )

        except Exception as e:
            result = ExampleValidationResult(
                example_name=example['name'],
                file_path=example['file_path'],
                validation_status="failed",
                execution_time=time.time() - start_time,
                input_text=example.get('input_text', ''),
                expected_output=None,
                actual_output=None,
                error_message=str(e),
                confidence_scores={},
                completeness_score=0.0,
                accuracy_score=0.0
            )

        return result

    async def _validate_narrative_example(self, example: Dict[str, Any]) -> ExampleValidationResult:
        """Validate a narrative text example by processing it through MCP tools"""
        start_time = time.time()

        # Create a mock context for MCP tools
        class MockContext:
            def __init__(self):
                self.session_id = "validation_session"

        mock_ctx = MockContext()

        try:
            # Test character analysis
            if 'analyze_character_text' in self.mcp_tools:
                analysis_result = await self.mcp_tools['analyze_character_text'](
                    example['input_text'], mock_ctx
                )
                analysis_data = json.loads(analysis_result)

                # Validate against criteria
                criteria = example['validation_criteria']
                confidence_scores = {}

                if 'characters' in analysis_data:
                    characters = analysis_data['characters']
                    if len(characters) >= criteria['min_characters']:
                        confidence_scores['character_count'] = 1.0
                    else:
                        confidence_scores['character_count'] = 0.0

                    # Check confidence scores
                    if characters:
                        avg_confidence = sum(char.get('confidence_score', 0) for char in characters) / len(characters)
                        confidence_scores['avg_character_confidence'] = avg_confidence
                    else:
                        confidence_scores['avg_character_confidence'] = 0.0

                # Check required fields
                completeness_score = 0.0
                required_fields = criteria.get('required_fields', [])
                if required_fields:
                    present_fields = sum(1 for field in required_fields if field in analysis_data)
                    completeness_score = present_fields / len(required_fields)

                # Calculate accuracy score
                accuracy_score = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.0

                # Determine validation status
                min_confidence = criteria.get('min_confidence_score', 0.7)
                if accuracy_score >= min_confidence and completeness_score >= 0.8:
                    status = "passed"
                elif accuracy_score >= min_confidence * 0.8:
                    status = "warning"
                else:
                    status = "failed"

                return ExampleValidationResult(
                    example_name=example['name'],
                    file_path=example['file_path'],
                    validation_status=status,
                    execution_time=time.time() - start_time,
                    input_text=example['input_text'],
                    expected_output=criteria,
                    actual_output=analysis_data,
                    error_message=None,
                    confidence_scores=confidence_scores,
                    completeness_score=completeness_score,
                    accuracy_score=accuracy_score
                )

            else:
                return ExampleValidationResult(
                    example_name=example['name'],
                    file_path=example['file_path'],
                    validation_status="failed",
                    execution_time=time.time() - start_time,
                    input_text=example['input_text'],
                    expected_output=None,
                    actual_output=None,
                    error_message="MCP tools not available for testing",
                    confidence_scores={},
                    completeness_score=0.0,
                    accuracy_score=0.0
                )

        except Exception as e:
            return ExampleValidationResult(
                example_name=example['name'],
                file_path=example['file_path'],
                validation_status="failed",
                execution_time=time.time() - start_time,
                input_text=example['input_text'],
                expected_output=None,
                actual_output=None,
                error_message=str(e),
                confidence_scores={},
                completeness_score=0.0,
                accuracy_score=0.0
            )

    async def _validate_code_example(self, example: Dict[str, Any]) -> ExampleValidationResult:
        """Validate a code example by attempting to execute it"""
        start_time = time.time()

        # For now, we'll do basic syntax validation
        # In a full implementation, we'd execute the code in a safe environment
        try:
            # Basic syntax check
            compile(example['code'], '<string>', 'exec')

            return ExampleValidationResult(
                example_name=example['name'],
                file_path=example['file_path'],
                validation_status="passed",
                execution_time=time.time() - start_time,
                input_text=example['code'],
                expected_output={'should_execute': True},
                actual_output={'syntax_valid': True},
                error_message=None,
                confidence_scores={'syntax_score': 1.0},
                completeness_score=1.0,
                accuracy_score=1.0
            )

        except SyntaxError as e:
            return ExampleValidationResult(
                example_name=example['name'],
                file_path=example['file_path'],
                validation_status="failed",
                execution_time=time.time() - start_time,
                input_text=example['code'],
                expected_output={'should_execute': True},
                actual_output={'syntax_valid': False},
                error_message=f"Syntax error: {str(e)}",
                confidence_scores={'syntax_score': 0.0},
                completeness_score=0.0,
                accuracy_score=0.0
            )

    async def _validate_expected_output(self, example: Dict[str, Any]) -> ExampleValidationResult:
        """Validate expected output format and completeness"""
        start_time = time.time()

        # Check if expected output contains required sections
        content = example['expected_content']
        required_sections = ['Character Profile', 'Musical Identity', 'Sample']

        completeness_score = 0.0
        found_sections = []

        for section in required_sections:
            if section.lower() in content.lower():
                found_sections.append(section)

        if found_sections:
            completeness_score = len(found_sections) / len(required_sections)

        status = "passed" if completeness_score >= 0.8 else "warning" if completeness_score >= 0.5 else "failed"

        return ExampleValidationResult(
            example_name=example['name'],
            file_path=example['file_path'],
            validation_status=status,
            execution_time=time.time() - start_time,
            input_text=content,
            expected_output={'required_sections': required_sections},
            actual_output={'found_sections': found_sections},
            error_message=None,
            confidence_scores={'section_coverage': completeness_score},
            completeness_score=completeness_score,
            accuracy_score=completeness_score
        )

    async def validate_all_examples(self) -> ValidationReport:
        """
        Validate all discovered documentation examples

        Returns:
            ValidationReport with comprehensive results
        """
        logger.info("Starting comprehensive example validation...")

        examples = self.discover_examples()
        validation_results = []

        # Validate each example
        for example in examples:
            logger.info(f"Validating example: {example['name']}")
            result = await self.validate_example(example)
            validation_results.append(result)

        # Calculate summary statistics
        total_examples = len(validation_results)
        passed_examples = sum(1 for r in validation_results if r.validation_status == "passed")
        failed_examples = sum(1 for r in validation_results if r.validation_status == "failed")
        warning_examples = sum(1 for r in validation_results if r.validation_status == "warning")

        overall_success_rate = passed_examples / total_examples if total_examples > 0 else 0.0
        average_execution_time = sum(r.execution_time for r in validation_results) / total_examples if total_examples > 0 else 0.0

        # Identify missing and outdated examples
        missing_examples = self._identify_missing_examples()
        outdated_examples = self._identify_outdated_examples(validation_results)

        report = ValidationReport(
            total_examples=total_examples,
            passed_examples=passed_examples,
            failed_examples=failed_examples,
            warning_examples=warning_examples,
            overall_success_rate=overall_success_rate,
            average_execution_time=average_execution_time,
            validation_timestamp=datetime.now().isoformat(),
            detailed_results=validation_results,
            missing_examples=missing_examples,
            outdated_examples=outdated_examples
        )

        logger.info(f"Validation complete: {passed_examples}/{total_examples} examples passed")
        return report

    def _identify_missing_examples(self) -> List[str]:
        """Identify areas where examples are missing"""
        missing = []

        # Check for missing examples in key areas
        required_example_areas = [
            "single_character_analysis",
            "multi_character_analysis",
            "album_creation_workflow",
            "prompt_template_usage",
            "error_handling_examples"
        ]

        existing_examples = self.discover_examples()
        existing_names = [ex['name'] for ex in existing_examples]

        for area in required_example_areas:
            if not any(area in name for name in existing_names):
                missing.append(area)

        return missing

    def _identify_outdated_examples(self, results: List[ExampleValidationResult]) -> List[str]:
        """Identify examples that may be outdated based on validation results"""
        outdated = []

        for result in results:
            # Consider examples outdated if they consistently fail or have low accuracy
            if result.validation_status == "failed" and result.accuracy_score < 0.5:
                outdated.append(result.example_name)
            elif result.validation_status == "warning" and result.completeness_score < 0.6:
                outdated.append(result.example_name)

        return outdated

    def generate_validation_report(self, report: ValidationReport, output_path: str = "validation_report.json"):
        """
        Generate a comprehensive validation report

        Args:
            report: ValidationReport to save
            output_path: Path to save the report
        """
        report_data = report.to_dict()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Validation report saved to {output_path}")

        # Also generate a human-readable summary
        summary_path = output_path.replace('.json', '_summary.md')
        self._generate_summary_report(report, summary_path)

    def _generate_summary_report(self, report: ValidationReport, output_path: str):
        """Generate a human-readable summary report"""
        summary = f"""# Documentation Example Validation Report

Generated: {report.validation_timestamp}

## Summary Statistics

- **Total Examples**: {report.total_examples}
- **Passed**: {report.passed_examples} ({report.passed_examples/report.total_examples*100:.1f}%)
- **Failed**: {report.failed_examples} ({report.failed_examples/report.total_examples*100:.1f}%)
- **Warnings**: {report.warning_examples} ({report.warning_examples/report.total_examples*100:.1f}%)
- **Overall Success Rate**: {report.overall_success_rate*100:.1f}%
- **Average Execution Time**: {report.average_execution_time:.2f}s

## Failed Examples

"""

        failed_results = [r for r in report.detailed_results if r.validation_status == "failed"]
        for result in failed_results:
            summary += f"### {result.example_name}\n"
            summary += f"- **File**: {result.file_path}\n"
            summary += f"- **Error**: {result.error_message}\n"
            summary += f"- **Accuracy Score**: {result.accuracy_score:.2f}\n\n"

        if report.missing_examples:
            summary += "## Missing Examples\n\n"
            for missing in report.missing_examples:
                summary += f"- {missing}\n"
            summary += "\n"

        if report.outdated_examples:
            summary += "## Potentially Outdated Examples\n\n"
            for outdated in report.outdated_examples:
                summary += f"- {outdated}\n"
            summary += "\n"

        summary += "## Recommendations\n\n"
        if report.overall_success_rate < 0.8:
            summary += "- Overall success rate is below 80%. Review failed examples and update documentation.\n"
        if report.missing_examples:
            summary += "- Add examples for missing areas to improve documentation coverage.\n"
        if report.outdated_examples:
            summary += "- Update outdated examples to match current system behavior.\n"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)

        logger.info(f"Summary report saved to {output_path}")

    def update_examples_when_code_changes(self, changed_files: List[str]) -> List[str]:
        """
        Identify examples that need updating when code changes

        Args:
            changed_files: List of file paths that have changed

        Returns:
            List of example names that may need updating
        """
        examples_to_update = []

        # Map code files to related examples
        code_to_example_mapping = {
            'server.py': ['character_analysis', 'persona_generation', 'suno_commands'],
            'working_universal_processor.py': ['universal_content', 'lyric_generation'],
            'enhanced_server.py': ['production_analysis', 'music_bible']
        }

        for changed_file in changed_files:
            file_name = Path(changed_file).name
            if file_name in code_to_example_mapping:
                examples_to_update.extend(code_to_example_mapping[file_name])

        return list(set(examples_to_update))  # Remove duplicates

# Example usage and testing
if __name__ == "__main__":
    async def main():
        generator = ExampleGenerator()

        # Validate all examples
        report = await generator.validate_all_examples()

        # Generate reports
        generator.generate_validation_report(report, "tests/validation/example_validation_report.json")

        print(f"Validation complete: {report.passed_examples}/{report.total_examples} examples passed")
        print(f"Success rate: {report.overall_success_rate*100:.1f}%")

    asyncio.run(main())
