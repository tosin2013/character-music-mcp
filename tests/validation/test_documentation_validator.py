#!/usr/bin/env python3
"""
Tests for DocumentationValidator class

This module tests the documentation completeness validation system.
"""

import tempfile
from pathlib import Path

from documentation_validator import DocumentationCoverage, DocumentationGap, DocumentationValidator


class TestDocumentationValidator:
    """Test suite for DocumentationValidator functionality"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.docs_path = Path(self.temp_dir) / "docs"
        self.examples_path = Path(self.temp_dir) / "examples"
        self.code_path = Path(self.temp_dir) / "code"

        # Create directory structure
        self.docs_path.mkdir(parents=True)
        self.examples_path.mkdir(parents=True)
        self.code_path.mkdir(parents=True)

        self.validator = DocumentationValidator(
            docs_path=str(self.docs_path),
            examples_path=str(self.examples_path),
            code_paths=[str(self.code_path)]
        )

    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_discover_documentation_files_empty(self):
        """Test discovering documentation files in empty directories"""
        doc_files = self.validator.discover_documentation_files()

        # Should return empty lists for all areas
        for area in self.validator.required_documentation_areas.keys():
            assert area in doc_files
            assert doc_files[area] == []

    def test_discover_documentation_files_with_content(self):
        """Test discovering documentation files with actual content"""
        # Create test documentation files
        (self.docs_path / "getting_started").mkdir()
        (self.docs_path / "getting_started" / "installation.md").write_text("# Installation Guide")
        (self.docs_path / "user_guides").mkdir()
        (self.docs_path / "user_guides" / "character_analysis.md").write_text("# Character Analysis")
        (self.examples_path / "single_character.md").write_text("# Single Character Example")

        doc_files = self.validator.discover_documentation_files()

        assert len(doc_files["getting_started"]) == 1
        assert len(doc_files["user_guides"]) == 1
        assert len(doc_files["examples"]) == 1

    def test_analyze_documentation_coverage(self):
        """Test documentation coverage analysis"""
        # Create test files with specific content
        getting_started_dir = self.docs_path / "getting_started"
        getting_started_dir.mkdir()

        # File covering installation and setup
        (getting_started_dir / "setup.md").write_text("""
        # Setup Guide

        This covers installation and setup procedures.
        Also includes basic_usage examples.
        """)

        coverage_results = self.validator.analyze_documentation_coverage()

        # Find getting_started coverage
        getting_started_coverage = next(
            (c for c in coverage_results if c.area_name == "getting_started"),
            None
        )

        assert getting_started_coverage is not None
        assert "installation" in getting_started_coverage.documented_topics
        assert "setup" in getting_started_coverage.documented_topics
        assert "basic_usage" in getting_started_coverage.documented_topics
        assert getting_started_coverage.coverage_percentage > 0

    def test_calculate_documentation_quality(self):
        """Test documentation quality calculation"""
        # Create high-quality documentation
        high_quality_file = self.docs_path / "high_quality.md"
        high_quality_file.write_text("""
        # High Quality Documentation

        This has headers, code examples, and lists.

        ```python
        example_code = "here"
        ```

        - List item 1
        - List item 2

        [Link to something](http://example.com)

        This covers character analysis and persona generation topics.
        """)

        # Create low-quality documentation
        low_quality_file = self.docs_path / "low_quality.md"
        low_quality_file.write_text("Short content.")

        high_score = self.validator._calculate_documentation_quality(
            [high_quality_file],
            ["character", "persona"]
        )
        low_score = self.validator._calculate_documentation_quality(
            [low_quality_file],
            ["character", "persona"]
        )

        assert high_score > low_score
        assert high_score > 0.5
        assert low_score < 0.5

    def test_extract_code_elements(self):
        """Test extraction of code elements from Python files"""
        # Create test Python file
        test_code = '''
"""Module docstring"""

import asyncio
from fastmcp import FastMCP

mcp = FastMCP("test")

@mcp.tool
@pytest.mark.asyncio
async def test_mcp_tool(param: str) -> str:
    """This is an MCP tool"""
    return param

class TestClass:
    """Test class docstring"""

    def public_method(self):
        """Public method"""
        pass

    def _private_method(self):
        """Private method"""
        pass

def public_function():
    """Public function"""
    pass

def _private_function():
    """Private function"""
    pass
        '''

        test_file = self.code_path / "test_code.py"
        test_file.write_text(test_code)

        elements = self.validator._extract_code_elements(test_file)

        # Should find MCP tool, class, and public functions
        element_names = [e['name'] for e in elements]
        assert 'test_mcp_tool' in element_names
        assert 'TestClass' in element_names
        assert 'public_method' in element_names
        assert 'public_function' in element_names

        # Should not include private methods in main results (but they're extracted)
        mcp_tool = next(e for e in elements if e['name'] == 'test_mcp_tool')
        assert mcp_tool['type'] == 'mcp_tool'
        assert mcp_tool['docstring'] == 'This is an MCP tool'

    def test_map_code_to_documentation(self):
        """Test mapping code elements to documentation"""
        # Create code elements
        code_elements = [
            {
                'name': 'documented_function',
                'type': 'function',
                'file': 'test.py',
                'line': 10,
                'docstring': 'Function docstring',
                'is_public': True
            },
            {
                'name': 'undocumented_function',
                'type': 'function',
                'file': 'test.py',
                'line': 20,
                'docstring': None,
                'is_public': True
            }
        ]

        # Create documentation that mentions one function
        (self.docs_path / "api.md").write_text("""
        # API Reference

        ## documented_function

        This function does something important.

        Example:
        ```python
        result = documented_function()
        ```
        """)

        mappings = self.validator.map_code_to_documentation(code_elements)

        assert len(mappings) == 2

        documented_mapping = next(m for m in mappings if m.code_element == 'documented_function')
        undocumented_mapping = next(m for m in mappings if m.code_element == 'undocumented_function')

        assert documented_mapping.documented
        assert documented_mapping.documentation_quality > 0.5
        assert not undocumented_mapping.documented

    def test_identify_documentation_gaps(self):
        """Test identification of documentation gaps"""
        # Create coverage with missing topics
        coverage = [
            DocumentationCoverage(
                area_name="getting_started",
                required_topics=["installation", "setup", "basic_usage"],
                documented_topics=["installation"],
                missing_topics=["setup", "basic_usage"],
                coverage_percentage=0.33,
                quality_score=0.5,
                last_updated="2024-01-01",
                file_paths=["docs/getting_started.md"]
            )
        ]

        # Create mappings with undocumented elements
        from documentation_validator import CodeDocumentationMapping
        mappings = [
            CodeDocumentationMapping(
                code_element="undocumented_tool",
                element_type="mcp_tool",
                source_file="server.py",
                documented=False,
                documentation_files=[],
                documentation_quality=0.0,
                last_code_change=None,
                last_doc_update=None,
                sync_status="missing"
            )
        ]

        gaps = self.validator.identify_documentation_gaps(coverage, mappings)

        # Should identify missing topics and undocumented code
        gap_descriptions = [g.description for g in gaps]
        assert any("setup" in desc for desc in gap_descriptions)
        assert any("basic_usage" in desc for desc in gap_descriptions)
        assert any("undocumented_tool" in desc for desc in gap_descriptions)

        # MCP tool should be high severity
        mcp_tool_gap = next(g for g in gaps if "undocumented_tool" in g.description)
        assert mcp_tool_gap.severity == "high"

    def test_determine_gap_severity(self):
        """Test gap severity determination"""
        # Critical areas and topics should be critical
        assert self.validator._determine_gap_severity("getting_started", "installation") == "critical"
        assert self.validator._determine_gap_severity("api_reference", "mcp_tools") == "critical"

        # User guides should be high
        assert self.validator._determine_gap_severity("user_guides", "character_analysis") == "high"

        # Other areas should be medium
        assert self.validator._determine_gap_severity("developer_guides", "architecture") == "medium"

    def test_calculate_priority_score(self):
        """Test priority score calculation"""
        critical_getting_started = self.validator._calculate_priority_score("critical", "getting_started")
        medium_developer = self.validator._calculate_priority_score("medium", "developer_guides")

        assert critical_getting_started > medium_developer
        assert critical_getting_started == 1.0  # Critical + getting_started = max priority

    def test_generate_improvement_recommendations(self):
        """Test generation of improvement recommendations"""
        # Create coverage with issues
        coverage = [
            DocumentationCoverage(
                area_name="getting_started",
                required_topics=["installation", "setup"],
                documented_topics=["installation"],
                missing_topics=["setup"],
                coverage_percentage=0.5,
                quality_score=0.6,
                last_updated="2024-01-01",
                file_paths=["docs/getting_started.md"]
            )
        ]

        # Create gaps
        gaps = [
            DocumentationGap(
                gap_type="missing",
                severity="critical",
                area="getting_started",
                description="Missing setup documentation",
                affected_files=["docs/getting_started.md"],
                suggested_action="Add setup documentation",
                priority_score=1.0
            )
        ]

        recommendations = self.validator._generate_improvement_recommendations(coverage, gaps)

        assert len(recommendations) > 0
        assert any("critical" in rec.lower() for rec in recommendations)
        assert any("coverage" in rec.lower() for rec in recommendations)

    def test_ensure_documentation_stays_current_with_code(self):
        """Test identification of docs to update when code changes"""
        changed_files = ['server.py', 'test_something.py', 'example_workflow.py']

        # Create some documentation files
        (self.docs_path / "api_reference").mkdir()
        (self.docs_path / "api_reference" / "mcp_tools.md").write_text("# MCP Tools")
        (self.docs_path / "user_guides").mkdir()
        (self.docs_path / "user_guides" / "usage.md").write_text("# Usage Guide")

        docs_to_update = self.validator.ensure_documentation_stays_current_with_code(changed_files)

        # Should identify docs that need updating based on changed files
        assert len(docs_to_update) > 0
        # Should include API reference and user guides for server.py changes
        doc_paths = [str(Path(d).parent.name) for d in docs_to_update]
        assert 'api_reference' in doc_paths or 'user_guides' in doc_paths

    def test_check_documentation_completeness_integration(self):
        """Test complete documentation completeness check"""
        # Create minimal test environment
        (self.docs_path / "getting_started").mkdir()
        (self.docs_path / "getting_started" / "setup.md").write_text("""
        # Setup Guide
        Installation and setup instructions here.
        """)

        # Create test code file
        (self.code_path / "test.py").write_text('''
@mcp.tool
@pytest.mark.asyncio
async def test_tool():
    """Test MCP tool"""
    pass
        ''')

        report = self.validator.check_documentation_completeness()

        assert report.total_areas_checked > 0
        assert report.overall_coverage_percentage >= 0.0
        assert isinstance(report.coverage_by_area, list)
        assert isinstance(report.code_documentation_mapping, list)
        assert isinstance(report.identified_gaps, list)
        assert isinstance(report.improvement_recommendations, list)

    def test_generate_completeness_report(self):
        """Test generation of completeness report files"""
        from documentation_validator import CompletionReport

        report = CompletionReport(
            overall_coverage_percentage=0.75,
            total_areas_checked=5,
            fully_covered_areas=2,
            partially_covered_areas=2,
            uncovered_areas=1,
            total_gaps=10,
            critical_gaps=2,
            high_priority_gaps=3,
            validation_timestamp="2024-01-01T12:00:00",
            coverage_by_area=[],
            code_documentation_mapping=[],
            identified_gaps=[],
            improvement_recommendations=["Improve coverage"]
        )

        output_path = Path(self.temp_dir) / "test_completeness_report.json"
        self.validator.generate_completeness_report(report, str(output_path))

        # Check that files were created
        assert output_path.exists()
        assert Path(str(output_path).replace('.json', '_summary.md')).exists()

        # Check JSON content
        import json
        with open(output_path, 'r') as f:
            saved_report = json.load(f)

        assert saved_report['overall_coverage_percentage'] == 0.75
        assert saved_report['total_gaps'] == 10

# Manual integration test
def manual_integration_test():
    """Manual integration test with real documentation"""
    validator = DocumentationValidator()

    print("Checking documentation completeness...")
    report = validator.check_documentation_completeness()

    print(f"Overall coverage: {report.overall_coverage_percentage*100:.1f}%")
    print(f"Total gaps: {report.total_gaps}")
    print(f"Critical gaps: {report.critical_gaps}")

    if report.coverage_by_area:
        print("\nCoverage by area:")
        for coverage in report.coverage_by_area:
            print(f"  {coverage.area_name}: {coverage.coverage_percentage*100:.1f}%")

if __name__ == "__main__":
    # Run manual integration test
    manual_integration_test()
