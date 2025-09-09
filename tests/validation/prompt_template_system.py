#!/usr/bin/env python3
"""
Prompt Template Testing System

This module provides automated testing and validation of prompt templates,
ensuring they produce expected results and maintain effectiveness over time.
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
class PromptTemplate:
    """Represents a reusable prompt template"""
    name: str
    use_case: str
    template_text: str
    placeholder_descriptions: Dict[str, str]
    example_values: Dict[str, str]
    expected_outcome: str
    difficulty_level: str  # "beginner", "intermediate", "advanced"
    genre_focus: Optional[str] = None
    character_type: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

@dataclass
class TemplateTestResult:
    """Result of testing a single prompt template"""
    template_name: str
    test_status: str  # "passed", "failed", "warning"
    execution_time: float
    filled_template: str
    expected_output: Dict[str, Any]
    actual_output: Optional[Dict[str, Any]]
    effectiveness_score: float  # 0.0 to 1.0
    character_confidence: float
    genre_accuracy: float
    completeness_score: float
    error_message: Optional[str]
    recommendations: List[str]

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

@dataclass
class TemplateValidationReport:
    """Comprehensive report for all template testing"""
    total_templates: int
    passed_templates: int
    failed_templates: int
    warning_templates: int
    average_effectiveness: float
    average_execution_time: float
    validation_timestamp: str
    detailed_results: List[TemplateTestResult]
    template_rankings: List[Dict[str, Any]]
    improvement_suggestions: List[str]

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

class PromptTemplateSystem:
    """
    Manages and validates prompt templates for character-driven music generation

    This class provides automated testing of prompt templates to ensure they
    produce high-quality, consistent results across different use cases.
    """

    def __init__(self, templates_path: str = "examples/prompt_templates"):
        self.templates_path = Path(templates_path)
        self.templates: Dict[str, PromptTemplate] = {}
        self.test_results: List[TemplateTestResult] = []

        # Import MCP tools for testing
        try:
            from server import (
                analyze_character_text,
                complete_workflow,
                create_suno_commands,
                generate_artist_personas,
            )
            self.mcp_tools = {
                'analyze_character_text': analyze_character_text,
                'generate_artist_personas': generate_artist_personas,
                'create_suno_commands': create_suno_commands,
                'complete_workflow': complete_workflow
            }
        except ImportError as e:
            logger.warning(f"MCP tools not available for testing: {e}")
            self.mcp_tools = {}

    def load_templates(self) -> Dict[str, PromptTemplate]:
        """
        Load all prompt templates from the templates directory

        Returns:
            Dictionary of template name to PromptTemplate objects
        """
        templates = {}

        if not self.templates_path.exists():
            logger.warning(f"Templates path {self.templates_path} does not exist")
            return templates

        for template_file in self.templates_path.rglob("*.md"):
            try:
                template = self._parse_template_file(template_file)
                if template:
                    templates[template.name] = template
                    logger.info(f"Loaded template: {template.name}")
            except Exception as e:
                logger.error(f"Error loading template {template_file}: {e}")

        self.templates = templates
        logger.info(f"Loaded {len(templates)} prompt templates")
        return templates

    def _parse_template_file(self, file_path: Path) -> Optional[PromptTemplate]:
        """Parse a template markdown file into a PromptTemplate object"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract template metadata
            name = self._extract_template_name(content, file_path)
            use_case = self._extract_use_case(content)
            template_text = self._extract_template_text(content)
            placeholder_descriptions = self._extract_placeholder_descriptions(content)
            example_values = self._extract_example_values(content)
            expected_outcome = self._extract_expected_outcome(content)
            difficulty_level = self._extract_difficulty_level(content)
            genre_focus = self._extract_genre_focus(content)
            character_type = self._extract_character_type(content)

            if not template_text:
                logger.warning(f"No template text found in {file_path}")
                return None

            return PromptTemplate(
                name=name,
                use_case=use_case,
                template_text=template_text,
                placeholder_descriptions=placeholder_descriptions,
                example_values=example_values,
                expected_outcome=expected_outcome,
                difficulty_level=difficulty_level,
                genre_focus=genre_focus,
                character_type=character_type
            )

        except Exception as e:
            logger.error(f"Error parsing template file {file_path}: {e}")
            return None

    def _extract_template_name(self, content: str, file_path: Path) -> str:
        """Extract template name from content or filename"""
        # Try to find title in markdown
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()

        # Fall back to filename
        return file_path.stem.replace('_', ' ').title()

    def _extract_use_case(self, content: str) -> str:
        """Extract use case description from template"""
        purpose_match = re.search(r'\*\*Purpose\*\*:\s*(.+)', content)
        if purpose_match:
            return purpose_match.group(1).strip()

        best_for_match = re.search(r'\*\*Best For\*\*:\s*(.+)', content)
        if best_for_match:
            return best_for_match.group(1).strip()

        return "General character analysis"

    def _extract_template_text(self, content: str) -> str:
        """Extract the main template text with placeholders"""
        # Look for template structure section
        template_match = re.search(r'## Template Structure\s*```\s*(.*?)\s*```', content, re.DOTALL)
        if template_match:
            return template_match.group(1).strip()

        # Look for any code block that contains placeholders
        code_blocks = re.findall(r'```(?:text)?\s*(.*?)\s*```', content, re.DOTALL)
        for block in code_blocks:
            if '[' in block and ']' in block:  # Contains placeholders
                return block.strip()

        return ""

    def _extract_placeholder_descriptions(self, content: str) -> Dict[str, str]:
        """Extract placeholder descriptions from template"""
        descriptions = {}

        # Look for placeholder guide section
        guide_match = re.search(r'## Placeholder Guide(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if guide_match:
            guide_content = guide_match.group(1)

            # Extract individual placeholder descriptions
            placeholder_pattern = r'\*\*\[([^\]]+)\]\*\*:\s*(.+?)(?=\n\*\*\[|\n\n|\Z)'
            matches = re.findall(placeholder_pattern, guide_content, re.DOTALL)

            for placeholder, description in matches:
                descriptions[placeholder] = description.strip()

        return descriptions

    def _extract_example_values(self, content: str) -> Dict[str, str]:
        """Extract example values for placeholders"""
        example_values = {}

        # Look for filled template example
        example_match = re.search(r'## Example: Filled Template\s*```\s*(.*?)\s*```', content, re.DOTALL)
        if example_match:
            example_text = example_match.group(1)

            # Try to extract values from the filled example
            # This is a simplified approach - in practice, you'd want more sophisticated parsing
            lines = example_text.split('\n')
            for line in lines:
                if ':' in line and not line.strip().startswith('#'):
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        if value and not value.startswith('['):
                            example_values[key] = value

        return example_values

    def _extract_expected_outcome(self, content: str) -> str:
        """Extract expected outcome description"""
        outcome_match = re.search(r'## Expected Results.*?### (.+?)\s*-', content, re.DOTALL)
        if outcome_match:
            return outcome_match.group(1).strip()

        return "High-quality character analysis with musical direction"

    def _extract_difficulty_level(self, content: str) -> str:
        """Extract difficulty level"""
        difficulty_match = re.search(r'\*\*Difficulty\*\*:\s*(\w+)', content)
        if difficulty_match:
            return difficulty_match.group(1).lower()

        return "intermediate"

    def _extract_genre_focus(self, content: str) -> Optional[str]:
        """Extract genre focus if specified"""
        genre_match = re.search(r'genre[:\s]+(\w+)', content, re.IGNORECASE)
        if genre_match:
            return genre_match.group(1)

        return None

    def _extract_character_type(self, content: str) -> Optional[str]:
        """Extract character type focus if specified"""
        char_match = re.search(r'character[:\s]+(\w+)', content, re.IGNORECASE)
        if char_match:
            return char_match.group(1)

        return None

    def fill_template(self, template: PromptTemplate, custom_values: Optional[Dict[str, str]] = None) -> str:
        """
        Fill a template with example values or custom values

        Args:
            template: PromptTemplate to fill
            custom_values: Optional custom values to use instead of example values

        Returns:
            Filled template text
        """
        values = custom_values or template.example_values
        filled_text = template.template_text

        # Replace placeholders with values
        for placeholder, value in values.items():
            # Handle different placeholder formats
            patterns = [
                f'[{placeholder}]',
                f'[{placeholder.upper()}]',
                f'[{placeholder.lower()}]',
                f'{{{placeholder}}}',
                f'{{{placeholder.upper()}}}',
                f'{{{placeholder.lower()}}}'
            ]

            for pattern in patterns:
                filled_text = filled_text.replace(pattern, value)

        return filled_text

    async def test_template(self, template: PromptTemplate, custom_values: Optional[Dict[str, str]] = None) -> TemplateTestResult:
        """
        Test a single prompt template by filling it and processing through MCP tools

        Args:
            template: PromptTemplate to test
            custom_values: Optional custom values for testing

        Returns:
            TemplateTestResult with validation details
        """
        start_time = time.time()

        try:
            # Fill the template
            filled_template = self.fill_template(template, custom_values)

            if not filled_template.strip():
                return TemplateTestResult(
                    template_name=template.name,
                    test_status="failed",
                    execution_time=time.time() - start_time,
                    filled_template="",
                    expected_output={},
                    actual_output=None,
                    effectiveness_score=0.0,
                    character_confidence=0.0,
                    genre_accuracy=0.0,
                    completeness_score=0.0,
                    error_message="Template could not be filled",
                    recommendations=["Check template placeholders and example values"]
                )

            # Test with MCP tools if available
            if 'analyze_character_text' in self.mcp_tools:
                result = await self._test_with_mcp_tools(template, filled_template)
            else:
                result = await self._test_without_mcp_tools(template, filled_template)

            result.execution_time = time.time() - start_time
            return result

        except Exception as e:
            return TemplateTestResult(
                template_name=template.name,
                test_status="failed",
                execution_time=time.time() - start_time,
                filled_template=filled_template if 'filled_template' in locals() else "",
                expected_output={},
                actual_output=None,
                effectiveness_score=0.0,
                character_confidence=0.0,
                genre_accuracy=0.0,
                completeness_score=0.0,
                error_message=str(e),
                recommendations=["Review template structure and fix errors"]
            )

    async def _test_with_mcp_tools(self, template: PromptTemplate, filled_template: str) -> TemplateTestResult:
        """Test template using actual MCP tools"""
        # Create mock context
        class MockContext:
            def __init__(self):
                self.session_id = "template_test_session"

        mock_ctx = MockContext()

        try:
            # Analyze the filled template
            analysis_result = await self.mcp_tools['analyze_character_text'](filled_template, mock_ctx)
            analysis_data = json.loads(analysis_result)

            # Calculate effectiveness metrics
            character_confidence = 0.0
            if 'characters' in analysis_data and analysis_data['characters']:
                confidences = [char.get('confidence_score', 0) for char in analysis_data['characters']]
                character_confidence = sum(confidences) / len(confidences)

            # Check genre accuracy if template has genre focus
            genre_accuracy = 1.0  # Default to perfect if no specific genre expected
            if template.genre_focus and 'characters' in analysis_data:
                # This would need more sophisticated genre matching logic
                genre_accuracy = 0.8  # Placeholder

            # Calculate completeness score
            required_fields = ['characters', 'narrative_themes']
            present_fields = sum(1 for field in required_fields if field in analysis_data and analysis_data[field])
            completeness_score = present_fields / len(required_fields)

            # Calculate overall effectiveness
            effectiveness_score = (character_confidence + genre_accuracy + completeness_score) / 3

            # Determine test status
            if effectiveness_score >= 0.8:
                status = "passed"
            elif effectiveness_score >= 0.6:
                status = "warning"
            else:
                status = "failed"

            # Generate recommendations
            recommendations = []
            if character_confidence < 0.7:
                recommendations.append("Add more specific character details and psychology")
            if completeness_score < 0.8:
                recommendations.append("Include more narrative context and character relationships")
            if effectiveness_score < 0.8:
                recommendations.append("Consider revising template structure for better results")

            return TemplateTestResult(
                template_name=template.name,
                test_status=status,
                execution_time=0.0,  # Will be set by caller
                filled_template=filled_template,
                expected_output={'expected_effectiveness': 0.8},
                actual_output=analysis_data,
                effectiveness_score=effectiveness_score,
                character_confidence=character_confidence,
                genre_accuracy=genre_accuracy,
                completeness_score=completeness_score,
                error_message=None,
                recommendations=recommendations
            )

        except Exception as e:
            return TemplateTestResult(
                template_name=template.name,
                test_status="failed",
                execution_time=0.0,
                filled_template=filled_template,
                expected_output={},
                actual_output=None,
                effectiveness_score=0.0,
                character_confidence=0.0,
                genre_accuracy=0.0,
                completeness_score=0.0,
                error_message=str(e),
                recommendations=["Fix template processing errors"]
            )

    async def _test_without_mcp_tools(self, template: PromptTemplate, filled_template: str) -> TemplateTestResult:
        """Test template without MCP tools using heuristic analysis"""
        # Heuristic scoring based on template content
        character_confidence = self._score_character_content(filled_template)
        genre_accuracy = self._score_genre_relevance(filled_template, template.genre_focus)
        completeness_score = self._score_completeness(filled_template)

        effectiveness_score = (character_confidence + genre_accuracy + completeness_score) / 3

        status = "passed" if effectiveness_score >= 0.7 else "warning" if effectiveness_score >= 0.5 else "failed"

        recommendations = []
        if character_confidence < 0.6:
            recommendations.append("Add more character psychology and specific details")
        if completeness_score < 0.7:
            recommendations.append("Include more comprehensive character background")

        return TemplateTestResult(
            template_name=template.name,
            test_status=status,
            execution_time=0.0,
            filled_template=filled_template,
            expected_output={'heuristic_analysis': True},
            actual_output={'heuristic_scores': {
                'character_confidence': character_confidence,
                'genre_accuracy': genre_accuracy,
                'completeness_score': completeness_score
            }},
            effectiveness_score=effectiveness_score,
            character_confidence=character_confidence,
            genre_accuracy=genre_accuracy,
            completeness_score=completeness_score,
            error_message=None,
            recommendations=recommendations
        )

    def _score_character_content(self, text: str) -> float:
        """Score character content quality using heuristics"""
        score = 0.0

        # Check for character indicators
        character_indicators = ['character', 'personality', 'emotion', 'feeling', 'thought', 'motivation']
        for indicator in character_indicators:
            if indicator.lower() in text.lower():
                score += 0.1

        # Check for psychological depth indicators
        psychology_indicators = ['fear', 'desire', 'conflict', 'dream', 'hope', 'struggle']
        for indicator in psychology_indicators:
            if indicator.lower() in text.lower():
                score += 0.15

        # Check for narrative elements
        narrative_indicators = ['story', 'background', 'experience', 'relationship', 'family']
        for indicator in narrative_indicators:
            if indicator.lower() in text.lower():
                score += 0.1

        return min(score, 1.0)

    def _score_genre_relevance(self, text: str, genre_focus: Optional[str]) -> float:
        """Score genre relevance if genre focus is specified"""
        if not genre_focus:
            return 1.0  # No specific genre requirement

        genre_keywords = {
            'folk': ['acoustic', 'storytelling', 'traditional', 'rural', 'simple'],
            'rock': ['electric', 'powerful', 'energy', 'rebellion', 'loud'],
            'indie': ['independent', 'alternative', 'creative', 'unique', 'artistic'],
            'electronic': ['digital', 'synthetic', 'modern', 'technology', 'experimental']
        }

        if genre_focus.lower() in genre_keywords:
            keywords = genre_keywords[genre_focus.lower()]
            matches = sum(1 for keyword in keywords if keyword in text.lower())
            return min(matches / len(keywords), 1.0)

        return 0.8  # Default score for unknown genres

    def _score_completeness(self, text: str) -> float:
        """Score template completeness"""
        # Check for unfilled placeholders
        placeholder_patterns = [r'\[[\w\s_]+\]', r'\{[\w\s_]+\}']
        unfilled_count = 0

        for pattern in placeholder_patterns:
            unfilled_count += len(re.findall(pattern, text))

        if unfilled_count > 0:
            return max(0.0, 1.0 - (unfilled_count * 0.2))

        # Check for minimum content length
        if len(text.strip()) < 100:
            return 0.3
        elif len(text.strip()) < 300:
            return 0.6
        else:
            return 1.0

    async def test_all_templates(self) -> TemplateValidationReport:
        """
        Test all loaded templates and generate comprehensive report

        Returns:
            TemplateValidationReport with detailed results
        """
        logger.info("Starting comprehensive template testing...")

        if not self.templates:
            self.load_templates()

        test_results = []

        for template_name, template in self.templates.items():
            logger.info(f"Testing template: {template_name}")
            result = await self.test_template(template)
            test_results.append(result)

        # Calculate summary statistics
        total_templates = len(test_results)
        passed_templates = sum(1 for r in test_results if r.test_status == "passed")
        failed_templates = sum(1 for r in test_results if r.test_status == "failed")
        warning_templates = sum(1 for r in test_results if r.test_status == "warning")

        average_effectiveness = sum(r.effectiveness_score for r in test_results) / total_templates if total_templates > 0 else 0.0
        average_execution_time = sum(r.execution_time for r in test_results) / total_templates if total_templates > 0 else 0.0

        # Rank templates by effectiveness
        template_rankings = sorted([
            {
                'name': r.template_name,
                'effectiveness_score': r.effectiveness_score,
                'character_confidence': r.character_confidence,
                'status': r.test_status
            }
            for r in test_results
        ], key=lambda x: x['effectiveness_score'], reverse=True)

        # Generate improvement suggestions
        improvement_suggestions = self._generate_improvement_suggestions(test_results)

        report = TemplateValidationReport(
            total_templates=total_templates,
            passed_templates=passed_templates,
            failed_templates=failed_templates,
            warning_templates=warning_templates,
            average_effectiveness=average_effectiveness,
            average_execution_time=average_execution_time,
            validation_timestamp=datetime.now().isoformat(),
            detailed_results=test_results,
            template_rankings=template_rankings,
            improvement_suggestions=improvement_suggestions
        )

        self.test_results = test_results
        logger.info(f"Template testing complete: {passed_templates}/{total_templates} templates passed")
        return report

    def _generate_improvement_suggestions(self, results: List[TemplateTestResult]) -> List[str]:
        """Generate improvement suggestions based on test results"""
        suggestions = []

        # Analyze common failure patterns
        failed_results = [r for r in results if r.test_status == "failed"]
        if len(failed_results) > len(results) * 0.3:
            suggestions.append("High failure rate detected. Review template structure and placeholder definitions.")

        # Check for low character confidence
        low_confidence_count = sum(1 for r in results if r.character_confidence < 0.6)
        if low_confidence_count > len(results) * 0.4:
            suggestions.append("Many templates produce low character confidence. Add more psychological depth and specific character details.")

        # Check for completeness issues
        low_completeness_count = sum(1 for r in results if r.completeness_score < 0.7)
        if low_completeness_count > len(results) * 0.3:
            suggestions.append("Templates may have unfilled placeholders or insufficient content. Review example values and template structure.")

        # Performance suggestions
        slow_templates = [r for r in results if r.execution_time > 5.0]
        if slow_templates:
            suggestions.append(f"{len(slow_templates)} templates are slow to process. Consider optimizing template complexity.")

        return suggestions

    def generate_template_report(self, report: TemplateValidationReport, output_path: str = "template_validation_report.json"):
        """
        Generate comprehensive template validation report

        Args:
            report: TemplateValidationReport to save
            output_path: Path to save the report
        """
        report_data = report.to_dict()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Template validation report saved to {output_path}")

        # Generate human-readable summary
        summary_path = output_path.replace('.json', '_summary.md')
        self._generate_template_summary(report, summary_path)

    def _generate_template_summary(self, report: TemplateValidationReport, output_path: str):
        """Generate human-readable template summary report"""
        summary = f"""# Prompt Template Validation Report

Generated: {report.validation_timestamp}

## Summary Statistics

- **Total Templates**: {report.total_templates}
- **Passed**: {report.passed_templates} ({report.passed_templates/report.total_templates*100:.1f}%)
- **Failed**: {report.failed_templates} ({report.failed_templates/report.total_templates*100:.1f}%)
- **Warnings**: {report.warning_templates} ({report.warning_templates/report.total_templates*100:.1f}%)
- **Average Effectiveness**: {report.average_effectiveness:.2f}
- **Average Execution Time**: {report.average_execution_time:.2f}s

## Template Rankings

"""

        for i, template in enumerate(report.template_rankings[:10], 1):
            summary += f"{i}. **{template['name']}** - {template['effectiveness_score']:.2f} ({template['status']})\n"

        summary += "\n## Failed Templates\n\n"
        failed_results = [r for r in report.detailed_results if r.test_status == "failed"]
        for result in failed_results:
            summary += f"### {result.template_name}\n"
            summary += f"- **Effectiveness**: {result.effectiveness_score:.2f}\n"
            summary += f"- **Error**: {result.error_message}\n"
            if result.recommendations:
                summary += f"- **Recommendations**: {', '.join(result.recommendations)}\n"
            summary += "\n"

        if report.improvement_suggestions:
            summary += "## Improvement Suggestions\n\n"
            for suggestion in report.improvement_suggestions:
                summary += f"- {suggestion}\n"
            summary += "\n"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)

        logger.info(f"Template summary saved to {output_path}")

    def create_template(self, name: str, use_case: str, template_text: str,
                       placeholder_descriptions: Dict[str, str],
                       example_values: Dict[str, str]) -> PromptTemplate:
        """
        Create a new prompt template

        Args:
            name: Template name
            use_case: Description of when to use this template
            template_text: Template text with placeholders
            placeholder_descriptions: Descriptions of each placeholder
            example_values: Example values for placeholders

        Returns:
            New PromptTemplate object
        """
        template = PromptTemplate(
            name=name,
            use_case=use_case,
            template_text=template_text,
            placeholder_descriptions=placeholder_descriptions,
            example_values=example_values,
            expected_outcome="High-quality character analysis",
            difficulty_level="intermediate"
        )

        self.templates[name] = template
        return template

    def verify_templates_produce_expected_results(self, templates: List[str]) -> Dict[str, bool]:
        """
        Verify that specific templates produce expected results

        Args:
            templates: List of template names to verify

        Returns:
            Dictionary mapping template names to verification status
        """
        verification_results = {}

        for template_name in templates:
            if template_name in self.templates:
                # Find the test result for this template
                result = next((r for r in self.test_results if r.template_name == template_name), None)
                if result:
                    verification_results[template_name] = result.test_status == "passed"
                else:
                    verification_results[template_name] = False
            else:
                verification_results[template_name] = False

        return verification_results

# Example usage and testing
if __name__ == "__main__":
    async def main():
        system = PromptTemplateSystem()

        # Load and test all templates
        templates = system.load_templates()
        print(f"Loaded {len(templates)} templates")

        if templates:
            # Test all templates
            report = await system.test_all_templates()

            # Generate reports
            system.generate_template_report(report, "tests/validation/template_validation_report.json")

            print(f"Template testing complete: {report.passed_templates}/{report.total_templates} templates passed")
            print(f"Average effectiveness: {report.average_effectiveness:.2f}")

    asyncio.run(main())
