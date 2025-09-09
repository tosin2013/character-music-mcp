#!/usr/bin/env python3
"""
Parse pytest XML results and create structured failure data for GitHub issues
"""

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List


def parse_junit_xml(xml_file: str) -> List[Dict]:
    """Parse JUnit XML file and extract failure information"""
    failures = []

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Handle different JUnit XML formats
        testcases = root.findall('.//testcase')

        for testcase in testcases:
            failure = testcase.find('failure')
            error = testcase.find('error')

            if failure is not None or error is not None:
                issue_data = {
                    'test_name': testcase.get('name', 'Unknown Test'),
                    'class_name': testcase.get('classname', 'Unknown Class'),
                    'file_path': testcase.get('file', 'Unknown File'),
                    'time': testcase.get('time', '0'),
                }

                if failure is not None:
                    issue_data['error_type'] = 'Failure'
                    issue_data['error_message'] = failure.get('message', 'No message')
                    issue_data['full_error'] = failure.text or 'No details'
                elif error is not None:
                    issue_data['error_type'] = 'Error'
                    issue_data['error_message'] = error.get('message', 'No message')
                    issue_data['full_error'] = error.text or 'No details'

                # Clean up the file path
                if issue_data['file_path'] != 'Unknown File':
                    issue_data['file_path'] = str(Path(issue_data['file_path']).relative_to(Path.cwd()))

                failures.append(issue_data)

    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
    except FileNotFoundError:
        print(f"XML file not found: {xml_file}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return failures

def categorize_failures(failures: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize failures by type for better issue management"""
    categories = {
        'import_errors': [],
        'syntax_errors': [],
        'indentation_errors': [],
        'assertion_errors': [],
        'runtime_errors': [],
        'other_errors': []
    }

    for failure in failures:
        error_msg = failure['error_message'].lower()
        full_error = failure['full_error'].lower()

        if 'importerror' in error_msg or 'modulenotfounderror' in error_msg:
            categories['import_errors'].append(failure)
        elif 'syntaxerror' in error_msg or 'invalid syntax' in error_msg:
            categories['syntax_errors'].append(failure)
        elif 'indentationerror' in error_msg or 'unexpected indent' in error_msg:
            categories['indentation_errors'].append(failure)
        elif 'assertionerror' in error_msg or 'assert' in full_error:
            categories['assertion_errors'].append(failure)
        elif any(term in error_msg for term in ['runtimeerror', 'attributeerror', 'typeerror', 'valueerror']):
            categories['runtime_errors'].append(failure)
        else:
            categories['other_errors'].append(failure)

    return categories

def create_summary_issues(categories: Dict[str, List[Dict]]) -> List[Dict]:
    """Create summary issues for categories with multiple failures"""
    summary_issues = []

    for category, failures in categories.items():
        if len(failures) > 3:  # Create summary for categories with many failures
            issue_data = {
                'test_name': f"Multiple {category.replace('_', ' ').title()}",
                'class_name': 'Multiple Classes',
                'file_path': 'Multiple Files',
                'error_type': 'Category Summary',
                'error_message': f'{len(failures)} tests failing with {category.replace("_", " ")}',
                'full_error': 'Affected tests:\n' + '\n'.join([
                    f'- {f["test_name"]} in {f["file_path"]}: {f["error_message"][:100]}...'
                    for f in failures[:10]  # Limit to first 10
                ]),
                'category': category,
                'failure_count': len(failures)
            }
            summary_issues.append(issue_data)

    return summary_issues

def main():
    """Main function to parse test results and create issue data"""
    if len(sys.argv) != 2:
        print("Usage: python parse_test_failures.py <junit_xml_file>")
        sys.exit(1)

    xml_file = sys.argv[1]

    # Parse failures
    failures = parse_junit_xml(xml_file)

    if not failures:
        print("No test failures found")
        return

    print(f"Found {len(failures)} test failures")

    # Categorize failures
    categories = categorize_failures(failures)

    # Print summary
    for category, cat_failures in categories.items():
        if cat_failures:
            print(f"{category}: {len(cat_failures)} failures")

    # Create summary issues for categories with many failures
    summary_issues = create_summary_issues(categories)

    # Combine individual failures (limit to prevent spam) and summaries
    individual_failures = []
    for category, cat_failures in categories.items():
        if len(cat_failures) <= 3:  # Include all if few failures
            individual_failures.extend(cat_failures)
        else:  # Include only first few for categories with many failures
            individual_failures.extend(cat_failures[:2])

    all_issues = individual_failures + summary_issues

    # Limit total issues to prevent spam
    if len(all_issues) > 10:
        all_issues = all_issues[:10]
        print("Limited to first 10 issues to prevent spam")

    # Write to JSON file for GitHub Actions
    with open('test_failures.json', 'w') as f:
        json.dump(all_issues, f, indent=2)

    print(f"Created {len(all_issues)} issue(s) for GitHub")

if __name__ == "__main__":
    main()
