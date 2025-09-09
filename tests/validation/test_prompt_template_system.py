import pytest

#!/usr/bin/env python3
"""
Tests for PromptTemplateSystem class

This module tests the prompt template testing system to ensure it correctly
loads, validates, and reports on prompt templates.
"""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock

from prompt_template_system import PromptTemplate, PromptTemplateSystem, TemplateTestResult


class TestPromptTemplateSystem:
    """Test suite for PromptTemplateSystem functionality"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.templates_path = Path(self.temp_dir) / "templates"
        self.templates_path.mkdir(parents=True)

        self.system = PromptTemplateSystem(templates_path=str(self.templates_path))

    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_load_templates_empty_directory(self):
        """Test loading templates from empty directory"""
        templates = self.system.load_templates()
        assert templates == {}

    def test_parse_template_file(self):
        """Test parsing a complete template file"""
        template_content = """# Single Character Deep Dive Template

**Purpose**: Create comprehensive single character analysis for rich musical development  
**Best For**: Solo albums, character studies, introspective music  
**Difficulty**: Beginner to Intermediate  

## Template Structure

```
[CHARACTER_NAME] [CHARACTER_AGE_CONTEXT] in [SETTING_DESCRIPTION]. [OPENING_SITUATION] 
reveals [PRIMARY_PERSONALITY_TRAIT], but [CONTRASTING_ELEMENT] suggests [DEEPER_COMPLEXITY].

[DAILY_ROUTINE_OR_HABIT] [REVEALS_PSYCHOLOGY]. [SPECIFIC_BEHAVIOR_EXAMPLE] shows 
[CHARACTER_VALUE_OR_FEAR]. When [CHALLENGING_SITUATION], [CHARACTER_NAME] 
[SPECIFIC_REACTION] because [PSYCHOLOGICAL_MOTIVATION].
```

## Placeholder Guide

### Character Basics
- **[CHARACTER_NAME]**: Choose a name that fits the character's background and personality
- **[CHARACTER_AGE_CONTEXT]**: Age with relevant life stage context
- **[SETTING_DESCRIPTION]**: Specific location that influences character psychology

## Example: Filled Template

```
Elena, at twenty-eight and working her third job in two years, lived in a converted 
warehouse apartment in the arts district. Her carefully curated Instagram feed 
reveals her eye for beauty and composition, but her habit of deleting posts 
minutes after publishing suggests a perfectionism that borders on self-sabotage.

Every morning, Elena arranged her coffee cup, notebook, and vintage camera in 
perfect alignment before starting her day, a ritual that calmed her anxiety.
```

## Expected Results

### Character Analysis
- **Confidence Score**: ~0.89
- **Primary Traits**: Perfectionist, artistic, anxious, observant
"""

        template_file = self.templates_path / "character_deep_dive.md"
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(template_content)

        template = self.system._parse_template_file(template_file)

        assert template is not None
        assert template.name == "Single Character Deep Dive Template"
        assert template.use_case == "Create comprehensive single character analysis for rich musical development"
        assert template.difficulty_level == "beginner"
        assert "[CHARACTER_NAME]" in template.template_text
        assert "CHARACTER_NAME" in template.placeholder_descriptions
        assert template.placeholder_descriptions["CHARACTER_NAME"] == "Choose a name that fits the character's background and personality"

    def test_fill_template(self):
        """Test filling a template with values"""
        template = PromptTemplate(
            name="Test Template",
            use_case="Testing",
            template_text="[CHARACTER_NAME] lived in [LOCATION] and was [PERSONALITY_TRAIT].",
            placeholder_descriptions={
                "CHARACTER_NAME": "Name of character",
                "LOCATION": "Where they live",
                "PERSONALITY_TRAIT": "Main personality trait"
            },
            example_values={
                "CHARACTER_NAME": "Elena",
                "LOCATION": "the city",
                "PERSONALITY_TRAIT": "introspective"
            },
            expected_outcome="Character analysis",
            difficulty_level="beginner"
        )

        filled = self.system.fill_template(template)
        expected = "Elena lived in the city and was introspective."
        assert filled == expected

    def test_fill_template_with_custom_values(self):
        """Test filling template with custom values"""
        template = PromptTemplate(
            name="Test Template",
            use_case="Testing",
            template_text="[NAME] was [TRAIT].",
            placeholder_descriptions={},
            example_values={"NAME": "Default", "TRAIT": "default"},
            expected_outcome="Test",
            difficulty_level="beginner"
        )

        custom_values = {"NAME": "Marcus", "TRAIT": "ambitious"}
        filled = self.system.fill_template(template, custom_values)
        assert filled == "Marcus was ambitious."

    def test_score_character_content(self):
        """Test character content scoring heuristics"""
        # High-quality character content
        good_text = """
        Elena was a complex character driven by deep fears and desires. Her personality 
        showed through her daily struggles with anxiety and her motivation to create art. 
        She had conflicting emotions about her family relationships and dreamed of finding 
        her place in the world.
        """

        good_score = self.system._score_character_content(good_text)
        assert good_score > 0.5

        # Low-quality content
        poor_text = "She was nice and lived somewhere."
        poor_score = self.system._score_character_content(poor_text)
        assert poor_score < 0.3

    def test_score_genre_relevance(self):
        """Test genre relevance scoring"""
        folk_text = "acoustic guitar storytelling traditional rural simple"
        folk_score = self.system._score_genre_relevance(folk_text, "folk")
        assert folk_score > 0.8

        # Text without genre keywords
        generic_text = "character development story"
        generic_score = self.system._score_genre_relevance(generic_text, "folk")
        assert generic_score < 0.5

        # No genre focus
        no_genre_score = self.system._score_genre_relevance(generic_text, None)
        assert no_genre_score == 1.0

    def test_score_completeness(self):
        """Test template completeness scoring"""
        # Complete template (no unfilled placeholders)
        complete_text = "This is a complete template with enough content to be meaningful and useful for character analysis."
        complete_score = self.system._score_completeness(complete_text)
        assert complete_score > 0.8

        # Incomplete template (has unfilled placeholders)
        incomplete_text = "This template has [UNFILLED_PLACEHOLDER] and [ANOTHER_ONE]."
        incomplete_score = self.system._score_completeness(incomplete_text)
        assert incomplete_score < 0.7

        # Too short
        short_text = "Short."
        short_score = self.system._score_completeness(short_text)
        assert short_score < 0.5

    @pytest.mark.asyncio
    async def test_test_template_without_mcp_tools(self):
        """Test template testing without MCP tools (heuristic mode)"""
        template = PromptTemplate(
            name="Test Template",
            use_case="Testing",
            template_text="Elena was a complex character with deep psychology and emotional struggles.",
            placeholder_descriptions={},
            example_values={},
            expected_outcome="Good analysis",
            difficulty_level="beginner"
        )

        # Ensure no MCP tools are available
        self.system.mcp_tools = {}

        result = await self.system.test_template(template)

        assert result.template_name == "Test Template"
        assert result.test_status in ["passed", "warning", "failed"]
        assert 0.0 <= result.effectiveness_score <= 1.0
        assert 0.0 <= result.character_confidence <= 1.0
        assert result.filled_template == template.template_text

    @pytest.mark.asyncio
    async def test_test_template_with_mock_mcp_tools(self):
        """Test template testing with mocked MCP tools"""
        template = PromptTemplate(
            name="Mock Test Template",
            use_case="Testing with mocks",
            template_text="Elena was introspective and artistic.",
            placeholder_descriptions={},
            example_values={},
            expected_outcome="Good analysis",
            difficulty_level="beginner"
        )

        # Mock MCP tool response
        mock_analysis_result = {
            "characters": [
                {
                    "name": "Elena",
                    "confidence_score": 0.85,
                    "importance_score": 1.0
                }
            ],
            "narrative_themes": ["introspection", "art"],
            "processing_time": 2.0
        }

        mock_tool = AsyncMock(return_value=json.dumps(mock_analysis_result))
        self.system.mcp_tools = {'analyze_character_text': mock_tool}

        result = await self.system.test_template(template)

        assert result.template_name == "Mock Test Template"
        assert result.test_status == "passed"
        assert result.character_confidence == 0.85
        assert result.completeness_score == 1.0  # Both required fields present
        assert result.effectiveness_score > 0.8

    @pytest.mark.asyncio
    async def test_test_all_templates(self):
        """Test comprehensive template testing"""
        # Create test templates
        template1_content = """# Template 1
**Purpose**: Test template 1
## Template Structure
```
[NAME] was [TRAIT].
```
## Placeholder Guide
- **[NAME]**: Character name
- **[TRAIT]**: Character trait
## Example: Filled Template
```
Elena was introspective.
```
"""

        template2_content = """# Template 2
**Purpose**: Test template 2
## Template Structure
```
[CHARACTER] lived in [PLACE].
```
"""

        # Write template files
        (self.templates_path / "template1.md").write_text(template1_content)
        (self.templates_path / "template2.md").write_text(template2_content)

        # Mock MCP tools
        mock_analysis_result = {
            "characters": [{"name": "Test", "confidence_score": 0.8}],
            "narrative_themes": ["test"],
            "processing_time": 1.0
        }

        mock_tool = AsyncMock(return_value=json.dumps(mock_analysis_result))
        self.system.mcp_tools = {'analyze_character_text': mock_tool}

        # Test all templates
        report = await self.system.test_all_templates()

        assert report.total_templates == 2
        assert report.passed_templates >= 0
        assert report.failed_templates >= 0
        assert report.warning_templates >= 0
        assert len(report.detailed_results) == 2
        assert len(report.template_rankings) == 2
        assert isinstance(report.improvement_suggestions, list)

    def test_create_template(self):
        """Test creating a new template"""
        template = self.system.create_template(
            name="New Template",
            use_case="Testing creation",
            template_text="[NAME] was [TRAIT].",
            placeholder_descriptions={"NAME": "Character name", "TRAIT": "Main trait"},
            example_values={"NAME": "Test", "TRAIT": "creative"}
        )

        assert template.name == "New Template"
        assert template.use_case == "Testing creation"
        assert "New Template" in self.system.templates
        assert self.system.templates["New Template"] == template

    def test_verify_templates_produce_expected_results(self):
        """Test verification of template results"""
        # Create mock test results
        self.system.test_results = [
            TemplateTestResult(
                template_name="Good Template",
                test_status="passed",
                execution_time=1.0,
                filled_template="test",
                expected_output={},
                actual_output={},
                effectiveness_score=0.9,
                character_confidence=0.8,
                genre_accuracy=0.9,
                completeness_score=0.9,
                error_message=None,
                recommendations=[]
            ),
            TemplateTestResult(
                template_name="Bad Template",
                test_status="failed",
                execution_time=1.0,
                filled_template="test",
                expected_output={},
                actual_output={},
                effectiveness_score=0.3,
                character_confidence=0.2,
                genre_accuracy=0.4,
                completeness_score=0.3,
                error_message="Failed",
                recommendations=[]
            )
        ]

        verification = self.system.verify_templates_produce_expected_results(
            ["Good Template", "Bad Template", "Missing Template"]
        )

        assert verification["Good Template"] == True
        assert verification["Bad Template"] == False
        assert verification["Missing Template"] == False

    def test_generate_improvement_suggestions(self):
        """Test generation of improvement suggestions"""
        # Create mock results with various issues
        results = [
            TemplateTestResult(
                template_name="Failed 1",
                test_status="failed",
                execution_time=1.0,
                filled_template="test",
                expected_output={},
                actual_output={},
                effectiveness_score=0.2,
                character_confidence=0.1,
                genre_accuracy=0.2,
                completeness_score=0.3,
                error_message="Failed",
                recommendations=[]
            ),
            TemplateTestResult(
                template_name="Failed 2",
                test_status="failed",
                execution_time=6.0,  # Slow
                filled_template="test",
                expected_output={},
                actual_output={},
                effectiveness_score=0.3,
                character_confidence=0.2,
                genre_accuracy=0.3,
                completeness_score=0.4,
                error_message="Failed",
                recommendations=[]
            ),
            TemplateTestResult(
                template_name="Good",
                test_status="passed",
                execution_time=1.0,
                filled_template="test",
                expected_output={},
                actual_output={},
                effectiveness_score=0.9,
                character_confidence=0.8,
                genre_accuracy=0.9,
                completeness_score=0.9,
                error_message=None,
                recommendations=[]
            )
        ]

        suggestions = self.system._generate_improvement_suggestions(results)

        # Should detect high failure rate
        assert any("High failure rate" in s for s in suggestions)
        # Should detect low character confidence
        assert any("character confidence" in s for s in suggestions)
        # Should detect slow templates
        assert any("slow to process" in s for s in suggestions)

    def test_generate_template_report(self):
        """Test generation of template validation report"""
        from prompt_template_system import TemplateValidationReport

        report = TemplateValidationReport(
            total_templates=3,
            passed_templates=2,
            failed_templates=1,
            warning_templates=0,
            average_effectiveness=0.7,
            average_execution_time=2.0,
            validation_timestamp="2024-01-01T12:00:00",
            detailed_results=[],
            template_rankings=[
                {'name': 'Best Template', 'effectiveness_score': 0.9, 'status': 'passed'},
                {'name': 'Good Template', 'effectiveness_score': 0.8, 'status': 'passed'},
                {'name': 'Poor Template', 'effectiveness_score': 0.4, 'status': 'failed'}
            ],
            improvement_suggestions=["Improve failed templates"]
        )

        output_path = Path(self.temp_dir) / "test_template_report.json"
        self.system.generate_template_report(report, str(output_path))

        # Check that files were created
        assert output_path.exists()
        assert Path(str(output_path).replace('.json', '_summary.md')).exists()

        # Check JSON content
        with open(output_path, 'r') as f:
            saved_report = json.load(f)

        assert saved_report['total_templates'] == 3
        assert saved_report['average_effectiveness'] == 0.7

# Manual integration test
async def manual_integration_test():
    """Manual integration test with real templates"""
    system = PromptTemplateSystem()

    print("Loading templates...")
    templates = system.load_templates()
    print(f"Loaded {len(templates)} templates")

    if templates:
        print("\nTesting first template...")
        first_template = next(iter(templates.values()))
        result = await system.test_template(first_template)
        print(f"Result: {result.test_status}")
        print(f"Effectiveness: {result.effectiveness_score:.2f}")
        print(f"Character confidence: {result.character_confidence:.2f}")

if __name__ == "__main__":
    # Run manual integration test
    asyncio.run(manual_integration_test())
