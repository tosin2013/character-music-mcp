#!/usr/bin/env python3
"""
Tests for ExampleGenerator class

This module tests the example validation system to ensure it correctly
identifies, validates, and reports on documentation examples.
"""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from example_generator import ExampleGenerator, ExampleValidationResult, ValidationReport


class TestExampleGenerator:
    """Test suite for ExampleGenerator functionality"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.docs_path = Path(self.temp_dir) / "docs"
        self.examples_path = Path(self.temp_dir) / "examples"

        # Create directory structure
        self.docs_path.mkdir(parents=True)
        self.examples_path.mkdir(parents=True)

        self.generator = ExampleGenerator(
            docs_path=str(self.docs_path),
            examples_path=str(self.examples_path)
        )

    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_discover_examples_empty_directories(self):
        """Test example discovery with empty directories"""
        examples = self.generator.discover_examples()
        assert examples == []

    def test_extract_narrative_examples(self):
        """Test extraction of narrative examples from markdown"""
        # Create a test markdown file with narrative examples
        test_content = """
# Test Documentation

Here's a narrative example:

```
Elena grew up in the shadow of the lighthouse, where her father kept watch over ships
that rarely came anymore. She had always been the responsible one, the sister who held
everything together when their parents divorced. At seventeen, she spent her days reading
poetry on the rocky shore, writing in journals that she hid beneath her mattress.
```

And another example:

```text
Marcus stood at the crossroads of his career, torn between the security of his corporate
job and his dream of becoming a full-time musician. His guitar sat in the corner of his
apartment, gathering dust while he worked late nights on spreadsheets and quarterly reports.
```
        """

        test_file = self.docs_path / "test_doc.md"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        examples = self.generator._extract_examples_from_file(test_file)
        narrative_examples = [ex for ex in examples if ex['type'] == 'narrative']

        assert len(narrative_examples) == 2
        assert 'Elena grew up' in narrative_examples[0]['input_text']
        assert 'Marcus stood at' in narrative_examples[1]['input_text']
        assert narrative_examples[0]['expected_tools'] == ['analyze_character_text', 'complete_workflow']

    def test_extract_code_examples(self):
        """Test extraction of code examples from markdown"""
        test_content = """
# API Usage

Here's how to use the character analysis tool:

```python
result = await analyze_character_text('''
Your narrative text here...
''')
```

And here's the complete workflow:

```python
complete_result = await complete_workflow('''
Your narrative text here...
''')
```
        """

        test_file = self.docs_path / "api_doc.md"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        examples = self.generator._extract_examples_from_file(test_file)
        code_examples = [ex for ex in examples if ex['type'] == 'code']

        assert len(code_examples) == 2
        assert 'analyze_character_text' in code_examples[0]['code']
        assert 'complete_workflow' in code_examples[1]['code']

    def test_extract_expected_outputs(self):
        """Test extraction of expected output examples"""
        test_content = """
# Example Results

## Expected Character Analysis

### Character Profile: Elena
- **Confidence Score**: 0.85
- **Importance Score**: 1.0 (primary character)

#### Skin Layer (Observable)
- Introspective and solitary
- Loves reading and writing

## Generated Artist Persona

### Musical Identity
- **Primary Genre**: Indie Folk
- **Secondary Influences**: Alternative, Acoustic
        """

        test_file = self.examples_path / "example_results.md"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        examples = self.generator._extract_examples_from_file(test_file)
        output_examples = [ex for ex in examples if ex['type'] == 'expected_output']

        assert len(output_examples) >= 1
        assert 'Character Profile' in output_examples[0]['expected_content']

    @pytest.mark.asyncio
    async def test_validate_narrative_example_success(self):
        """Test successful validation of narrative example"""
        # Mock the MCP tools
        mock_analysis_result = {
            "characters": [
                {
                    "name": "Elena",
                    "confidence_score": 0.85,
                    "importance_score": 1.0
                }
            ],
            "narrative_themes": ["coming_of_age", "isolation"],
            "processing_time": 2.5
        }

        mock_tool = AsyncMock(return_value=json.dumps(mock_analysis_result))
        self.generator.mcp_tools = {'analyze_character_text': mock_tool}

        example = {
            'type': 'narrative',
            'name': 'test_narrative',
            'file_path': 'test.md',
            'input_text': 'Elena grew up in the shadow of the lighthouse...',
            'expected_tools': ['analyze_character_text'],
            'validation_criteria': {
                'min_confidence_score': 0.7,
                'min_characters': 1,
                'required_fields': ['characters', 'narrative_themes']
            }
        }

        result = await self.generator.validate_example(example)

        assert result.validation_status == "passed"
        assert result.accuracy_score >= 0.7
        assert result.completeness_score >= 0.8
        assert result.error_message is None

    @pytest.mark.asyncio
    async def test_validate_narrative_example_failure(self):
        """Test validation failure for narrative example"""
        # Mock a failed analysis result
        mock_analysis_result = {
            "characters": [],
            "narrative_themes": [],
            "processing_time": 1.0
        }

        mock_tool = AsyncMock(return_value=json.dumps(mock_analysis_result))
        self.generator.mcp_tools = {'analyze_character_text': mock_tool}

        example = {
            'type': 'narrative',
            'name': 'test_narrative_fail',
            'file_path': 'test.md',
            'input_text': 'Short text.',
            'expected_tools': ['analyze_character_text'],
            'validation_criteria': {
                'min_confidence_score': 0.7,
                'min_characters': 1,
                'required_fields': ['characters', 'narrative_themes']
            }
        }

        result = await self.generator.validate_example(example)

        assert result.validation_status == "failed"
        assert result.accuracy_score < 0.7

    @pytest.mark.asyncio
    async def test_validate_code_example_valid_syntax(self):
        """Test validation of code example with valid syntax"""
        example = {
            'type': 'code',
            'name': 'test_code',
            'file_path': 'test.md',
            'code': 'result = await analyze_character_text("test text")',
            'expected_execution': 'success',
            'validation_criteria': {
                'should_execute': True,
                'should_return_json': True
            }
        }

        result = await self.generator.validate_example(example)

        assert result.validation_status == "passed"
        assert result.confidence_scores['syntax_score'] == 1.0

    @pytest.mark.asyncio
    async def test_validate_code_example_invalid_syntax(self):
        """Test validation of code example with invalid syntax"""
        example = {
            'type': 'code',
            'name': 'test_code_invalid',
            'file_path': 'test.md',
            'code': 'result = await analyze_character_text("unclosed string',
            'expected_execution': 'success',
            'validation_criteria': {
                'should_execute': True,
                'should_return_json': True
            }
        }

        result = await self.generator.validate_example(example)

        assert result.validation_status == "failed"
        assert result.confidence_scores['syntax_score'] == 0.0
        assert "Syntax error" in result.error_message

    @pytest.mark.asyncio
    async def test_validate_expected_output_complete(self):
        """Test validation of expected output with complete sections"""
        example = {
            'type': 'expected_output',
            'name': 'test_output',
            'file_path': 'test.md',
            'expected_content': '''
            Character Profile: Elena
            Musical Identity: Indie Folk
            Sample Commands: Here are some examples
            ''',
            'validation_criteria': {
                'should_match_format': True,
                'should_contain_required_fields': True
            }
        }

        result = await self.generator.validate_example(example)

        assert result.validation_status == "passed"
        assert result.completeness_score >= 0.8

    @pytest.mark.asyncio
    async def test_validate_all_examples_integration(self):
        """Test complete validation workflow"""
        # Create test files with examples
        test_doc = self.docs_path / "integration_test.md"
        with open(test_doc, 'w', encoding='utf-8') as f:
            f.write("""
# Integration Test

```
Elena grew up in the shadow of the lighthouse, where her father kept watch over ships
that rarely came anymore. She had always been the responsible one, the sister who held
everything together when their parents divorced.
```

```python
result = await analyze_character_text("test")
```

## Expected Character Analysis
Character Profile: Elena with confidence score 0.85
            """)

        # Mock MCP tools
        mock_analysis_result = {
            "characters": [{"name": "Elena", "confidence_score": 0.85}],
            "narrative_themes": ["family"],
            "processing_time": 1.0
        }

        mock_tool = AsyncMock(return_value=json.dumps(mock_analysis_result))
        self.generator.mcp_tools = {'analyze_character_text': mock_tool}

        # Run validation
        report = await self.generator.validate_all_examples()

        assert report.total_examples >= 3  # narrative, code, expected_output
        assert report.passed_examples >= 1
        assert report.overall_success_rate > 0
        assert isinstance(report.validation_timestamp, str)

    def test_identify_missing_examples(self):
        """Test identification of missing example areas"""
        missing = self.generator._identify_missing_examples()

        # Should identify missing areas when no examples exist
        expected_areas = [
            "single_character_analysis",
            "multi_character_analysis",
            "album_creation_workflow",
            "prompt_template_usage",
            "error_handling_examples"
        ]

        for area in expected_areas:
            assert area in missing

    def test_identify_outdated_examples(self):
        """Test identification of outdated examples"""
        # Create mock validation results with some failures
        results = [
            ExampleValidationResult(
                example_name="outdated_example",
                file_path="test.md",
                validation_status="failed",
                execution_time=1.0,
                input_text="test",
                expected_output=None,
                actual_output=None,
                error_message="Failed validation",
                confidence_scores={},
                completeness_score=0.3,
                accuracy_score=0.2
            ),
            ExampleValidationResult(
                example_name="good_example",
                file_path="test.md",
                validation_status="passed",
                execution_time=1.0,
                input_text="test",
                expected_output=None,
                actual_output=None,
                error_message=None,
                confidence_scores={},
                completeness_score=0.9,
                accuracy_score=0.9
            )
        ]

        outdated = self.generator._identify_outdated_examples(results)

        assert "outdated_example" in outdated
        assert "good_example" not in outdated

    def test_generate_validation_report(self):
        """Test generation of validation report files"""
        # Create a mock report
        report = ValidationReport(
            total_examples=5,
            passed_examples=3,
            failed_examples=1,
            warning_examples=1,
            overall_success_rate=0.6,
            average_execution_time=2.5,
            validation_timestamp="2024-01-01T12:00:00",
            detailed_results=[],
            missing_examples=["test_area"],
            outdated_examples=["old_example"]
        )

        output_path = Path(self.temp_dir) / "test_report.json"
        self.generator.generate_validation_report(report, str(output_path))

        # Check that files were created
        assert output_path.exists()
        assert Path(str(output_path).replace('.json', '_summary.md')).exists()

        # Check JSON content
        with open(output_path, 'r') as f:
            saved_report = json.load(f)

        assert saved_report['total_examples'] == 5
        assert saved_report['overall_success_rate'] == 0.6

    def test_update_examples_when_code_changes(self):
        """Test identification of examples to update when code changes"""
        changed_files = ['server.py', 'working_universal_processor.py']

        examples_to_update = self.generator.update_examples_when_code_changes(changed_files)

        expected_examples = [
            'character_analysis', 'persona_generation', 'suno_commands',
            'universal_content', 'lyric_generation'
        ]

        for example in expected_examples:
            assert example in examples_to_update

# Integration test that can be run manually
async def manual_integration_test():
    """Manual integration test with real documentation"""
    generator = ExampleGenerator()

    print("Discovering examples...")
    examples = generator.discover_examples()
    print(f"Found {len(examples)} examples")

    if examples:
        print("\nValidating first example...")
        result = await generator.validate_example(examples[0])
        print(f"Result: {result.validation_status}")
        print(f"Accuracy: {result.accuracy_score:.2f}")
        print(f"Completeness: {result.completeness_score:.2f}")

if __name__ == "__main__":
    # Run manual integration test
    asyncio.run(manual_integration_test())
