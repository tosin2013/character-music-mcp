#!/usr/bin/env python3
"""
Documentation Completeness Validator

This module provides comprehensive validation of documentation coverage,
ensuring that all aspects of the system are properly documented and
that documentation stays current with code changes.
"""

import asyncio
import json
import os
import re
import ast
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from pathlib import Path
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentationCoverage:
    """Coverage information for a specific documentation area"""
    area_name: str
    required_topics: List[str]
    documented_topics: List[str]
    missing_topics: List[str]
    coverage_percentage: float
    quality_score: float  # 0.0 to 1.0
    last_updated: Optional[str]
    file_paths: List[str]
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

@dataclass
class CodeDocumentationMapping:
    """Mapping between code elements and their documentation"""
    code_element: str
    element_type: str  # "function", "class", "tool", "endpoint"
    source_file: str
    documented: bool
    documentation_files: List[str]
    documentation_quality: float
    last_code_change: Optional[str]
    last_doc_update: Optional[str]
    sync_status: str  # "current", "outdated", "missing"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

@dataclass
class DocumentationGap:
    """Represents a gap in documentation coverage"""
    gap_type: str  # "missing", "outdated", "incomplete", "inconsistent"
    severity: str  # "critical", "high", "medium", "low"
    area: str
    description: str
    affected_files: List[str]
    suggested_action: str
    priority_score: float
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

@dataclass
class CompletionReport:
    """Comprehensive documentation completeness report"""
    overall_coverage_percentage: float
    total_areas_checked: int
    fully_covered_areas: int
    partially_covered_areas: int
    uncovered_areas: int
    total_gaps: int
    critical_gaps: int
    high_priority_gaps: int
    validation_timestamp: str
    coverage_by_area: List[DocumentationCoverage]
    code_documentation_mapping: List[CodeDocumentationMapping]
    identified_gaps: List[DocumentationGap]
    improvement_recommendations: List[str]
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

class DocumentationValidator:
    """
    Validates comprehensive documentation coverage and currency
    
    This class ensures that all aspects of the system are properly documented
    and that documentation stays synchronized with code changes.
    """
    
    def __init__(self, docs_path: str = "docs", examples_path: str = "examples", 
                 code_paths: List[str] = None):
        self.docs_path = Path(docs_path)
        self.examples_path = Path(examples_path)
        self.code_paths = [Path(p) for p in (code_paths or [".", "tests"])]
        
        # Define required documentation areas and their topics
        self.required_documentation_areas = {
            "getting_started": [
                "installation", "setup", "first_example", "basic_usage",
                "system_requirements", "troubleshooting_setup"
            ],
            "user_guides": [
                "character_analysis", "persona_generation", "suno_commands",
                "album_creation", "lyric_generation", "prompt_engineering",
                "best_practices", "common_workflows"
            ],
            "api_reference": [
                "mcp_tools", "data_models", "error_handling", "parameters",
                "return_values", "examples", "rate_limits", "authentication"
            ],
            "examples": [
                "single_character", "multi_character", "concept_albums",
                "genre_specific", "prompt_templates", "workflow_examples",
                "edge_cases", "advanced_usage"
            ],
            "developer_guides": [
                "architecture", "contributing", "testing", "deployment",
                "code_structure", "extending_system", "debugging"
            ],
            "troubleshooting": [
                "common_errors", "performance_issues", "setup_problems",
                "output_quality", "integration_issues", "debugging_guide"
            ]
        }
        
        # Define code elements that require documentation
        self.code_elements_requiring_docs = [
            "mcp_tools", "classes", "public_functions", "endpoints",
            "data_models", "configuration", "workflows"
        ]
    
    def discover_documentation_files(self) -> Dict[str, List[Path]]:
        """
        Discover all documentation files organized by area
        
        Returns:
            Dictionary mapping area names to lists of file paths
        """
        doc_files = {}
        
        # Discover files in docs directory
        if self.docs_path.exists():
            for area in self.required_documentation_areas.keys():
                area_files = []
                
                # Look for area-specific directories
                area_dir = self.docs_path / area
                if area_dir.exists():
                    area_files.extend(area_dir.rglob("*.md"))
                
                # Look for files with area name in filename
                for file_path in self.docs_path.rglob("*.md"):
                    if area in file_path.name.lower():
                        area_files.append(file_path)
                
                doc_files[area] = list(set(area_files))  # Remove duplicates
        
        # Discover files in examples directory
        if self.examples_path.exists():
            doc_files["examples"] = list(self.examples_path.rglob("*.md"))
        
        return doc_files
    
    def analyze_documentation_coverage(self) -> List[DocumentationCoverage]:
        """
        Analyze coverage for each documentation area
        
        Returns:
            List of DocumentationCoverage objects
        """
        doc_files = self.discover_documentation_files()
        coverage_results = []
        
        for area, required_topics in self.required_documentation_areas.items():
            area_files = doc_files.get(area, [])
            
            # Extract documented topics from files
            documented_topics = []
            file_paths = []
            
            for file_path in area_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                    
                    file_paths.append(str(file_path))
                    
                    # Check which required topics are covered in this file
                    for topic in required_topics:
                        if topic.lower() in content:
                            documented_topics.append(topic)
                
                except Exception as e:
                    logger.warning(f"Error reading {file_path}: {e}")
            
            # Remove duplicates and calculate coverage
            documented_topics = list(set(documented_topics))
            missing_topics = [t for t in required_topics if t not in documented_topics]
            coverage_percentage = len(documented_topics) / len(required_topics) if required_topics else 1.0
            
            # Calculate quality score based on content depth
            quality_score = self._calculate_documentation_quality(area_files, documented_topics)
            
            # Get last update time
            last_updated = self._get_last_update_time(area_files)
            
            coverage = DocumentationCoverage(
                area_name=area,
                required_topics=required_topics,
                documented_topics=documented_topics,
                missing_topics=missing_topics,
                coverage_percentage=coverage_percentage,
                quality_score=quality_score,
                last_updated=last_updated,
                file_paths=file_paths
            )
            
            coverage_results.append(coverage)
            logger.info(f"Area '{area}': {coverage_percentage*100:.1f}% coverage, quality: {quality_score:.2f}")
        
        return coverage_results
    
    def _calculate_documentation_quality(self, files: List[Path], topics: List[str]) -> float:
        """Calculate quality score for documentation files"""
        if not files:
            return 0.0
        
        total_score = 0.0
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_score = 0.0
                
                # Check for structural elements
                if re.search(r'^#+ ', content, re.MULTILINE):  # Headers
                    file_score += 0.2
                
                if '```' in content:  # Code examples
                    file_score += 0.3
                
                if re.search(r'^\s*[-*+] ', content, re.MULTILINE):  # Lists
                    file_score += 0.1
                
                if len(content) > 500:  # Substantial content
                    file_score += 0.2
                
                if re.search(r'\[.*\]\(.*\)', content):  # Links
                    file_score += 0.1
                
                # Check for completeness indicators
                if any(topic in content.lower() for topic in topics):
                    file_score += 0.1
                
                total_score += min(file_score, 1.0)
            
            except Exception as e:
                logger.warning(f"Error analyzing quality of {file_path}: {e}")
        
        return total_score / len(files)
    
    def _get_last_update_time(self, files: List[Path]) -> Optional[str]:
        """Get the most recent update time for a list of files"""
        if not files:
            return None
        
        try:
            latest_time = max(f.stat().st_mtime for f in files if f.exists())
            return datetime.fromtimestamp(latest_time).isoformat()
        except Exception:
            return None
    
    def discover_code_elements(self) -> List[Dict[str, Any]]:
        """
        Discover code elements that require documentation
        
        Returns:
            List of code element dictionaries
        """
        code_elements = []
        
        for code_path in self.code_paths:
            if not code_path.exists():
                continue
            
            # Find Python files
            for py_file in code_path.rglob("*.py"):
                if py_file.name.startswith('.') or '__pycache__' in str(py_file):
                    continue
                
                elements = self._extract_code_elements(py_file)
                code_elements.extend(elements)
        
        return code_elements
    
    def _extract_code_elements(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract documentable code elements from a Python file"""
        elements = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if it's an MCP tool
                    is_mcp_tool = any(
                        isinstance(decorator, ast.Name) and decorator.id == 'tool'
                        or (isinstance(decorator, ast.Attribute) and decorator.attr == 'tool')
                        for decorator in node.decorator_list
                    )
                    
                    element_type = "mcp_tool" if is_mcp_tool else "function"
                    
                    elements.append({
                        'name': node.name,
                        'type': element_type,
                        'file': str(file_path),
                        'line': node.lineno,
                        'docstring': ast.get_docstring(node),
                        'is_public': not node.name.startswith('_')
                    })
                
                elif isinstance(node, ast.ClassDef):
                    elements.append({
                        'name': node.name,
                        'type': 'class',
                        'file': str(file_path),
                        'line': node.lineno,
                        'docstring': ast.get_docstring(node),
                        'is_public': not node.name.startswith('_')
                    })
        
        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e}")
        
        return elements
    
    def map_code_to_documentation(self, code_elements: List[Dict[str, Any]]) -> List[CodeDocumentationMapping]:
        """
        Map code elements to their documentation
        
        Args:
            code_elements: List of code element dictionaries
            
        Returns:
            List of CodeDocumentationMapping objects
        """
        mappings = []
        doc_files = self.discover_documentation_files()
        
        # Flatten all documentation files
        all_doc_files = []
        for files in doc_files.values():
            all_doc_files.extend(files)
        
        for element in code_elements:
            # Skip private elements unless they're important
            if not element['is_public'] and element['type'] not in ['mcp_tool']:
                continue
            
            element_name = element['name']
            element_type = element['type']
            source_file = element['file']
            
            # Find documentation files that mention this element
            documentation_files = []
            documentation_quality = 0.0
            
            for doc_file in all_doc_files:
                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if element is mentioned
                    if element_name.lower() in content.lower():
                        documentation_files.append(str(doc_file))
                        
                        # Calculate quality based on context
                        if f"`{element_name}`" in content:  # Code formatting
                            documentation_quality += 0.3
                        if f"## {element_name}" in content or f"### {element_name}" in content:  # Dedicated section
                            documentation_quality += 0.4
                        if "example" in content.lower() and element_name in content:  # Has examples
                            documentation_quality += 0.3
                
                except Exception as e:
                    logger.warning(f"Error checking {doc_file} for {element_name}: {e}")
            
            # Determine documentation status
            documented = len(documentation_files) > 0 or element['docstring'] is not None
            
            # Calculate sync status (simplified)
            sync_status = "current"  # Would need git integration for real sync checking
            if not documented:
                sync_status = "missing"
            elif documentation_quality < 0.5:
                sync_status = "outdated"
            
            mapping = CodeDocumentationMapping(
                code_element=element_name,
                element_type=element_type,
                source_file=source_file,
                documented=documented,
                documentation_files=documentation_files,
                documentation_quality=min(documentation_quality, 1.0),
                last_code_change=None,  # Would need git integration
                last_doc_update=None,   # Would need git integration
                sync_status=sync_status
            )
            
            mappings.append(mapping)
        
        return mappings
    
    def identify_documentation_gaps(self, coverage: List[DocumentationCoverage], 
                                  mappings: List[CodeDocumentationMapping]) -> List[DocumentationGap]:
        """
        Identify gaps in documentation coverage
        
        Args:
            coverage: Documentation coverage analysis
            mappings: Code to documentation mappings
            
        Returns:
            List of DocumentationGap objects
        """
        gaps = []
        
        # Identify missing topic coverage
        for area_coverage in coverage:
            for missing_topic in area_coverage.missing_topics:
                severity = self._determine_gap_severity(area_coverage.area_name, missing_topic)
                
                gap = DocumentationGap(
                    gap_type="missing",
                    severity=severity,
                    area=area_coverage.area_name,
                    description=f"Missing documentation for '{missing_topic}' in {area_coverage.area_name}",
                    affected_files=area_coverage.file_paths,
                    suggested_action=f"Add documentation for {missing_topic} to {area_coverage.area_name} area",
                    priority_score=self._calculate_priority_score(severity, area_coverage.area_name)
                )
                gaps.append(gap)
        
        # Identify undocumented code elements
        undocumented_elements = [m for m in mappings if not m.documented]
        for mapping in undocumented_elements:
            severity = "high" if mapping.element_type == "mcp_tool" else "medium"
            
            gap = DocumentationGap(
                gap_type="missing",
                severity=severity,
                area="api_reference",
                description=f"Undocumented {mapping.element_type}: {mapping.code_element}",
                affected_files=[mapping.source_file],
                suggested_action=f"Add documentation for {mapping.code_element} in API reference",
                priority_score=self._calculate_priority_score(severity, "api_reference")
            )
            gaps.append(gap)
        
        # Identify low-quality documentation
        low_quality_mappings = [m for m in mappings if m.documented and m.documentation_quality < 0.5]
        for mapping in low_quality_mappings:
            gap = DocumentationGap(
                gap_type="incomplete",
                severity="medium",
                area="api_reference",
                description=f"Low-quality documentation for {mapping.code_element}",
                affected_files=mapping.documentation_files,
                suggested_action=f"Improve documentation quality for {mapping.code_element}",
                priority_score=self._calculate_priority_score("medium", "api_reference")
            )
            gaps.append(gap)
        
        # Identify areas with low overall coverage
        low_coverage_areas = [c for c in coverage if c.coverage_percentage < 0.7]
        for area_coverage in low_coverage_areas:
            gap = DocumentationGap(
                gap_type="incomplete",
                severity="high" if area_coverage.coverage_percentage < 0.5 else "medium",
                area=area_coverage.area_name,
                description=f"Low coverage in {area_coverage.area_name}: {area_coverage.coverage_percentage*100:.1f}%",
                affected_files=area_coverage.file_paths,
                suggested_action=f"Improve coverage in {area_coverage.area_name} area",
                priority_score=self._calculate_priority_score("high", area_coverage.area_name)
            )
            gaps.append(gap)
        
        return gaps
    
    def _determine_gap_severity(self, area: str, topic: str) -> str:
        """Determine the severity of a documentation gap"""
        critical_areas = ["getting_started", "api_reference"]
        critical_topics = ["installation", "setup", "mcp_tools", "basic_usage"]
        
        if area in critical_areas or topic in critical_topics:
            return "critical"
        elif area in ["user_guides", "examples"]:
            return "high"
        else:
            return "medium"
    
    def _calculate_priority_score(self, severity: str, area: str) -> float:
        """Calculate priority score for a gap"""
        severity_scores = {"critical": 1.0, "high": 0.8, "medium": 0.6, "low": 0.4}
        area_weights = {
            "getting_started": 1.0,
            "api_reference": 0.9,
            "user_guides": 0.8,
            "examples": 0.7,
            "developer_guides": 0.6,
            "troubleshooting": 0.8
        }
        
        severity_score = severity_scores.get(severity, 0.5)
        area_weight = area_weights.get(area, 0.5)
        
        return severity_score * area_weight
    
    def check_documentation_completeness(self) -> CompletionReport:
        """
        Perform comprehensive documentation completeness check
        
        Returns:
            CompletionReport with detailed analysis
        """
        logger.info("Starting comprehensive documentation completeness check...")
        
        # Analyze documentation coverage
        coverage_results = self.analyze_documentation_coverage()
        
        # Discover and map code elements
        code_elements = self.discover_code_elements()
        code_mappings = self.map_code_to_documentation(code_elements)
        
        # Identify gaps
        gaps = self.identify_documentation_gaps(coverage_results, code_mappings)
        
        # Calculate overall statistics
        total_areas = len(coverage_results)
        fully_covered_areas = sum(1 for c in coverage_results if c.coverage_percentage >= 0.9)
        partially_covered_areas = sum(1 for c in coverage_results if 0.1 <= c.coverage_percentage < 0.9)
        uncovered_areas = sum(1 for c in coverage_results if c.coverage_percentage < 0.1)
        
        overall_coverage = sum(c.coverage_percentage for c in coverage_results) / total_areas if total_areas > 0 else 0.0
        
        total_gaps = len(gaps)
        critical_gaps = sum(1 for g in gaps if g.severity == "critical")
        high_priority_gaps = sum(1 for g in gaps if g.severity == "high")
        
        # Generate improvement recommendations
        recommendations = self._generate_improvement_recommendations(coverage_results, gaps)
        
        report = CompletionReport(
            overall_coverage_percentage=overall_coverage,
            total_areas_checked=total_areas,
            fully_covered_areas=fully_covered_areas,
            partially_covered_areas=partially_covered_areas,
            uncovered_areas=uncovered_areas,
            total_gaps=total_gaps,
            critical_gaps=critical_gaps,
            high_priority_gaps=high_priority_gaps,
            validation_timestamp=datetime.now().isoformat(),
            coverage_by_area=coverage_results,
            code_documentation_mapping=code_mappings,
            identified_gaps=gaps,
            improvement_recommendations=recommendations
        )
        
        logger.info(f"Documentation completeness check complete: {overall_coverage*100:.1f}% overall coverage")
        return report
    
    def _generate_improvement_recommendations(self, coverage: List[DocumentationCoverage], 
                                           gaps: List[DocumentationGap]) -> List[str]:
        """Generate improvement recommendations based on analysis"""
        recommendations = []
        
        # Overall coverage recommendations
        overall_coverage = sum(c.coverage_percentage for c in coverage) / len(coverage) if coverage else 0.0
        if overall_coverage < 0.7:
            recommendations.append("Overall documentation coverage is below 70%. Focus on improving coverage across all areas.")
        
        # Critical gap recommendations
        critical_gaps = [g for g in gaps if g.severity == "critical"]
        if critical_gaps:
            recommendations.append(f"Address {len(critical_gaps)} critical documentation gaps immediately.")
        
        # Area-specific recommendations
        low_coverage_areas = [c for c in coverage if c.coverage_percentage < 0.6]
        if low_coverage_areas:
            area_names = [c.area_name for c in low_coverage_areas]
            recommendations.append(f"Improve coverage in these areas: {', '.join(area_names)}")
        
        # Code documentation recommendations
        undocumented_tools = sum(1 for g in gaps if g.gap_type == "missing" and "mcp_tool" in g.description)
        if undocumented_tools > 0:
            recommendations.append(f"Document {undocumented_tools} MCP tools that are missing documentation.")
        
        # Quality recommendations
        quality_issues = sum(1 for g in gaps if g.gap_type == "incomplete")
        if quality_issues > 0:
            recommendations.append(f"Improve quality of {quality_issues} documentation areas with incomplete coverage.")
        
        return recommendations
    
    def generate_completeness_report(self, report: CompletionReport, 
                                   output_path: str = "documentation_completeness_report.json"):
        """
        Generate comprehensive documentation completeness report
        
        Args:
            report: CompletionReport to save
            output_path: Path to save the report
        """
        report_data = report.to_dict()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Documentation completeness report saved to {output_path}")
        
        # Generate human-readable summary
        summary_path = output_path.replace('.json', '_summary.md')
        self._generate_completeness_summary(report, summary_path)
    
    def _generate_completeness_summary(self, report: CompletionReport, output_path: str):
        """Generate human-readable completeness summary"""
        summary = f"""# Documentation Completeness Report

Generated: {report.validation_timestamp}

## Overall Statistics

- **Overall Coverage**: {report.overall_coverage_percentage*100:.1f}%
- **Total Areas Checked**: {report.total_areas_checked}
- **Fully Covered Areas**: {report.fully_covered_areas}
- **Partially Covered Areas**: {report.partially_covered_areas}
- **Uncovered Areas**: {report.uncovered_areas}
- **Total Gaps**: {report.total_gaps}
- **Critical Gaps**: {report.critical_gaps}
- **High Priority Gaps**: {report.high_priority_gaps}

## Coverage by Area

"""
        
        for coverage in sorted(report.coverage_by_area, key=lambda x: x.coverage_percentage, reverse=True):
            summary += f"### {coverage.area_name.replace('_', ' ').title()}\n"
            summary += f"- **Coverage**: {coverage.coverage_percentage*100:.1f}%\n"
            summary += f"- **Quality Score**: {coverage.quality_score:.2f}\n"
            summary += f"- **Missing Topics**: {len(coverage.missing_topics)}\n"
            if coverage.missing_topics:
                summary += f"  - {', '.join(coverage.missing_topics)}\n"
            summary += "\n"
        
        # Critical gaps
        critical_gaps = [g for g in report.identified_gaps if g.severity == "critical"]
        if critical_gaps:
            summary += "## Critical Gaps\n\n"
            for gap in critical_gaps:
                summary += f"### {gap.description}\n"
                summary += f"- **Area**: {gap.area}\n"
                summary += f"- **Action**: {gap.suggested_action}\n"
                summary += f"- **Priority**: {gap.priority_score:.2f}\n\n"
        
        # Improvement recommendations
        if report.improvement_recommendations:
            summary += "## Improvement Recommendations\n\n"
            for i, recommendation in enumerate(report.improvement_recommendations, 1):
                summary += f"{i}. {recommendation}\n"
            summary += "\n"
        
        # Code documentation status
        undocumented_code = [m for m in report.code_documentation_mapping if not m.documented]
        if undocumented_code:
            summary += "## Undocumented Code Elements\n\n"
            for mapping in undocumented_code[:10]:  # Show first 10
                summary += f"- **{mapping.code_element}** ({mapping.element_type}) in {mapping.source_file}\n"
            if len(undocumented_code) > 10:
                summary += f"- ... and {len(undocumented_code) - 10} more\n"
            summary += "\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logger.info(f"Completeness summary saved to {output_path}")
    
    def ensure_documentation_stays_current_with_code(self, changed_files: List[str]) -> List[str]:
        """
        Identify documentation that needs updating when code changes
        
        Args:
            changed_files: List of code files that have changed
            
        Returns:
            List of documentation files that may need updating
        """
        docs_to_update = []
        
        # Map changed files to documentation areas
        file_to_area_mapping = {
            'server.py': ['api_reference', 'user_guides'],
            'enhanced_server.py': ['api_reference', 'user_guides'],
            'working_universal_processor.py': ['api_reference', 'user_guides'],
            'test_': ['developer_guides'],  # Any test file
            'example': ['examples']
        }
        
        affected_areas = set()
        for changed_file in changed_files:
            file_name = Path(changed_file).name
            
            for pattern, areas in file_to_area_mapping.items():
                if pattern in file_name:
                    affected_areas.update(areas)
        
        # Find documentation files in affected areas
        doc_files = self.discover_documentation_files()
        for area in affected_areas:
            if area in doc_files:
                docs_to_update.extend([str(f) for f in doc_files[area]])
        
        return list(set(docs_to_update))  # Remove duplicates

# Example usage and testing
if __name__ == "__main__":
    def main():
        validator = DocumentationValidator()
        
        # Check documentation completeness
        report = validator.check_documentation_completeness()
        
        # Generate reports
        validator.generate_completeness_report(report, "tests/validation/documentation_completeness_report.json")
        
        print(f"Documentation completeness check complete:")
        print(f"Overall coverage: {report.overall_coverage_percentage*100:.1f}%")
        print(f"Critical gaps: {report.critical_gaps}")
        print(f"Total gaps: {report.total_gaps}")
    
    main()