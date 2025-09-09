#!/usr/bin/env python3
"""
Validation script for testing DocumentationValidator functionality
"""

import sys
from pathlib import Path

# Add the validation directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from documentation_validator import DocumentationValidator


def main():
    """Run documentation completeness validation tests"""
    print("=== Documentation Completeness Validation ===\n")

    # Initialize the validator
    validator = DocumentationValidator()

    # Test 1: Discover documentation files
    print("1. Testing documentation file discovery...")
    doc_files = validator.discover_documentation_files()

    total_files = sum(len(files) for files in doc_files.values())
    print(f"   Found {total_files} documentation files across {len(doc_files)} areas")

    for area, files in doc_files.items():
        if files:
            print(f"   - {area}: {len(files)} files")

    # Test 2: Analyze documentation coverage
    print("\n2. Testing documentation coverage analysis...")
    coverage_results = validator.analyze_documentation_coverage()

    print(f"   Analyzed {len(coverage_results)} documentation areas")
    for coverage in coverage_results:
        print(f"   - {coverage.area_name}: {coverage.coverage_percentage*100:.1f}% coverage")
        print(f"     Quality: {coverage.quality_score:.2f}, Missing: {len(coverage.missing_topics)} topics")
        if coverage.missing_topics:
            print(f"     Missing topics: {', '.join(coverage.missing_topics[:3])}{'...' if len(coverage.missing_topics) > 3 else ''}")

    # Test 3: Discover code elements
    print("\n3. Testing code element discovery...")
    code_elements = validator.discover_code_elements()

    print(f"   Found {len(code_elements)} code elements")

    # Group by type
    element_types = {}
    for element in code_elements:
        element_type = element['type']
        if element_type not in element_types:
            element_types[element_type] = []
        element_types[element_type].append(element)

    for element_type, elements in element_types.items():
        print(f"   - {element_type}: {len(elements)}")
        if element_type == 'mcp_tool':
            tool_names = [e['name'] for e in elements[:5]]  # Show first 5
            print(f"     Examples: {', '.join(tool_names)}{'...' if len(elements) > 5 else ''}")

    # Test 4: Map code to documentation
    print("\n4. Testing code-to-documentation mapping...")
    mappings = validator.map_code_to_documentation(code_elements)

    documented_count = sum(1 for m in mappings if m.documented)
    undocumented_count = len(mappings) - documented_count

    print(f"   Mapped {len(mappings)} code elements")
    print(f"   - Documented: {documented_count}")
    print(f"   - Undocumented: {undocumented_count}")

    # Show some examples
    if mappings:
        print("   Examples:")
        for mapping in mappings[:3]:
            status = "✓" if mapping.documented else "✗"
            print(f"   {status} {mapping.code_element} ({mapping.element_type}) - Quality: {mapping.documentation_quality:.2f}")

    # Test 5: Identify documentation gaps
    print("\n5. Testing documentation gap identification...")
    gaps = validator.identify_documentation_gaps(coverage_results, mappings)

    print(f"   Identified {len(gaps)} documentation gaps")

    # Group by severity
    gap_severities = {}
    for gap in gaps:
        if gap.severity not in gap_severities:
            gap_severities[gap.severity] = []
        gap_severities[gap.severity].append(gap)

    for severity, severity_gaps in gap_severities.items():
        print(f"   - {severity}: {len(severity_gaps)} gaps")

    # Show critical gaps
    critical_gaps = [g for g in gaps if g.severity == "critical"]
    if critical_gaps:
        print("   Critical gaps:")
        for gap in critical_gaps[:3]:
            print(f"   - {gap.description}")

    # Test 6: Complete documentation check
    print("\n6. Testing complete documentation completeness check...")
    try:
        report = validator.check_documentation_completeness()

        print(f"   Overall coverage: {report.overall_coverage_percentage*100:.1f}%")
        print(f"   Areas checked: {report.total_areas_checked}")
        print(f"   Fully covered: {report.fully_covered_areas}")
        print(f"   Partially covered: {report.partially_covered_areas}")
        print(f"   Uncovered: {report.uncovered_areas}")
        print(f"   Total gaps: {report.total_gaps}")
        print(f"   Critical gaps: {report.critical_gaps}")
        print(f"   High priority gaps: {report.high_priority_gaps}")

        # Show improvement recommendations
        if report.improvement_recommendations:
            print("\n   Top improvement recommendations:")
            for i, recommendation in enumerate(report.improvement_recommendations[:3], 1):
                print(f"   {i}. {recommendation}")

        # Generate report files
        output_dir = Path("tests/validation/reports")
        output_dir.mkdir(exist_ok=True)

        report_path = output_dir / "documentation_completeness_report.json"
        validator.generate_completeness_report(report, str(report_path))
        print(f"\n   Report saved to: {report_path}")

    except Exception as e:
        print(f"   Error during complete check: {e}")

    # Test 7: Code change impact analysis
    print("\n7. Testing code change impact analysis...")
    changed_files = ['server.py', 'enhanced_server.py', 'test_new_feature.py']
    docs_to_update = validator.ensure_documentation_stays_current_with_code(changed_files)

    print(f"   Files that changed: {', '.join(changed_files)}")
    print(f"   Documentation files to review: {len(docs_to_update)}")
    if docs_to_update:
        print("   Files to update:")
        for doc_file in docs_to_update[:5]:
            print(f"   - {doc_file}")
        if len(docs_to_update) > 5:
            print(f"   - ... and {len(docs_to_update) - 5} more")

    print("\n=== Validation Complete ===")

if __name__ == "__main__":
    main()
