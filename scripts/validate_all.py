#!/usr/bin/env python3
"""
Comprehensive Validation Script

Validates all documentation, examples, and templates to ensure they work
correctly and provide accurate information to users.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.validation.documentation_validator import DocumentationValidator
from tests.validation.example_generator import ExampleGenerator
from tests.validation.prompt_template_system import PromptTemplateSystem


class ComprehensiveValidator:
    """Comprehensive validation of all documentation and examples"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.validation_results = {}

        # Initialize validators
        self.doc_validator = DocumentationValidator()
        self.example_generator = ExampleGenerator()
        self.template_system = PromptTemplateSystem()

        # Validation thresholds
        self.thresholds = {
            "documentation_completeness": 0.90,
            "example_accuracy": 0.95,
            "template_effectiveness": 0.85,
            "link_validity": 0.98
        }

    async def validate_documentation(self) -> Dict[str, Any]:
        """Validate all documentation for completeness and accuracy"""
        print("📚 Validating documentation...")

        try:
            # Run documentation validation
            validation_result = await self.doc_validator.validate_all_documentation()

            # Calculate scores
            total_checks = len(validation_result.get("checks", []))
            passed_checks = len([c for c in validation_result.get("checks", []) if c.get("passed", False)])

            completeness_score = passed_checks / total_checks if total_checks > 0 else 0.0

            result = {
                "type": "documentation",
                "success": completeness_score >= self.thresholds["documentation_completeness"],
                "score": completeness_score,
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "failed_checks": total_checks - passed_checks,
                "details": validation_result,
                "threshold": self.thresholds["documentation_completeness"]
            }

            if result["success"]:
                print(f"✅ Documentation validation passed: {completeness_score:.1%}")
            else:
                print(f"❌ Documentation validation failed: {completeness_score:.1%} < {self.thresholds['documentation_completeness']:.1%}")

            return result

        except Exception as e:
            print(f"❌ Documentation validation error: {e}")
            return {
                "type": "documentation",
                "success": False,
                "score": 0.0,
                "error": str(e)
            }

    async def validate_examples(self) -> Dict[str, Any]:
        """Validate all examples work correctly"""
        print("🔍 Validating examples...")

        try:
            # Generate and validate examples
            validation_results = await self.example_generator.validate_all_examples()

            # Calculate scores
            total_examples = len(validation_results)
            successful_examples = len([r for r in validation_results if r.get("success", False)])

            accuracy_score = successful_examples / total_examples if total_examples > 0 else 0.0

            result = {
                "type": "examples",
                "success": accuracy_score >= self.thresholds["example_accuracy"],
                "score": accuracy_score,
                "total_examples": total_examples,
                "successful_examples": successful_examples,
                "failed_examples": total_examples - successful_examples,
                "details": validation_results,
                "threshold": self.thresholds["example_accuracy"]
            }

            if result["success"]:
                print(f"✅ Example validation passed: {accuracy_score:.1%}")
            else:
                print(f"❌ Example validation failed: {accuracy_score:.1%} < {self.thresholds['example_accuracy']:.1%}")

            return result

        except Exception as e:
            print(f"❌ Example validation error: {e}")
            return {
                "type": "examples",
                "success": False,
                "score": 0.0,
                "error": str(e)
            }

    async def validate_templates(self) -> Dict[str, Any]:
        """Validate all prompt templates"""
        print("📝 Validating prompt templates...")

        try:
            # Test all templates
            template_results = await self.template_system.test_all_templates()

            # Calculate scores
            total_templates = len(template_results)
            effective_templates = len([r for r in template_results if r.get("effective", False)])

            effectiveness_score = effective_templates / total_templates if total_templates > 0 else 0.0

            result = {
                "type": "templates",
                "success": effectiveness_score >= self.thresholds["template_effectiveness"],
                "score": effectiveness_score,
                "total_templates": total_templates,
                "effective_templates": effective_templates,
                "ineffective_templates": total_templates - effective_templates,
                "details": template_results,
                "threshold": self.thresholds["template_effectiveness"]
            }

            if result["success"]:
                print(f"✅ Template validation passed: {effectiveness_score:.1%}")
            else:
                print(f"❌ Template validation failed: {effectiveness_score:.1%} < {self.thresholds['template_effectiveness']:.1%}")

            return result

        except Exception as e:
            print(f"❌ Template validation error: {e}")
            return {
                "type": "templates",
                "success": False,
                "score": 0.0,
                "error": str(e)
            }

    def validate_links(self) -> Dict[str, Any]:
        """Validate all links in documentation"""
        print("🔗 Validating documentation links...")

        try:
            # Find all markdown files
            md_files = list(self.project_root.rglob("*.md"))

            total_links = 0
            valid_links = 0
            broken_links = []

            import re
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

            for md_file in md_files:
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    links = re.findall(link_pattern, content)

                    for link_text, link_url in links:
                        total_links += 1

                        # Check internal links
                        if link_url.startswith('#') or link_url.startswith('./') or link_url.startswith('../'):
                            # Internal link - check if file exists
                            if link_url.startswith('#'):
                                # Anchor link - assume valid for now
                                valid_links += 1
                            else:
                                # File link
                                link_path = md_file.parent / link_url
                                if link_path.exists():
                                    valid_links += 1
                                else:
                                    broken_links.append({
                                        "file": str(md_file),
                                        "link": link_url,
                                        "text": link_text,
                                        "type": "internal"
                                    })
                        else:
                            # External link - assume valid for now (would need HTTP requests)
                            valid_links += 1

                except Exception as e:
                    print(f"⚠️ Failed to check links in {md_file}: {e}")

            link_validity_score = valid_links / total_links if total_links > 0 else 1.0

            result = {
                "type": "links",
                "success": link_validity_score >= self.thresholds["link_validity"],
                "score": link_validity_score,
                "total_links": total_links,
                "valid_links": valid_links,
                "broken_links": len(broken_links),
                "broken_link_details": broken_links,
                "threshold": self.thresholds["link_validity"]
            }

            if result["success"]:
                print(f"✅ Link validation passed: {link_validity_score:.1%}")
            else:
                print(f"❌ Link validation failed: {link_validity_score:.1%} < {self.thresholds['link_validity']:.1%}")
                for broken_link in broken_links[:5]:  # Show first 5 broken links
                    print(f"  🔗 Broken link: {broken_link['link']} in {broken_link['file']}")

            return result

        except Exception as e:
            print(f"❌ Link validation error: {e}")
            return {
                "type": "links",
                "success": False,
                "score": 0.0,
                "error": str(e)
            }

    def validate_file_structure(self) -> Dict[str, Any]:
        """Validate expected file structure exists"""
        print("📁 Validating file structure...")

        # Expected files and directories
        expected_structure = {
            "files": [
                "README.md",
                "pyproject.toml",
                "server.py",
                "tests/test_runner.py"
            ],
            "directories": [
                "docs/user_guides",
                "examples/character_driven_albums",
                "examples/concept_albums",
                "examples/prompt_templates",
                "tests/unit",
                "tests/integration",
                "tests/performance",
                "tests/fixtures",
                "tests/validation"
            ]
        }

        missing_files = []
        missing_directories = []

        # Check files
        for file_path in expected_structure["files"]:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        # Check directories
        for dir_path in expected_structure["directories"]:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing_directories.append(dir_path)

        total_expected = len(expected_structure["files"]) + len(expected_structure["directories"])
        total_missing = len(missing_files) + len(missing_directories)
        structure_score = (total_expected - total_missing) / total_expected

        result = {
            "type": "file_structure",
            "success": total_missing == 0,
            "score": structure_score,
            "total_expected": total_expected,
            "missing_count": total_missing,
            "missing_files": missing_files,
            "missing_directories": missing_directories
        }

        if result["success"]:
            print("✅ File structure validation passed")
        else:
            print(f"❌ File structure validation failed: {total_missing} missing items")
            for missing in (missing_files + missing_directories)[:5]:
                print(f"  📁 Missing: {missing}")

        return result

    async def run_all_validations(self) -> Dict[str, Any]:
        """Run all validation checks"""
        print("🔍 Starting comprehensive validation")
        print("=" * 60)

        start_time = datetime.now()

        # Run all validations
        validations = []

        # Documentation validation
        doc_result = await self.validate_documentation()
        validations.append(doc_result)

        # Example validation
        example_result = await self.validate_examples()
        validations.append(example_result)

        # Template validation
        template_result = await self.validate_templates()
        validations.append(template_result)

        # Link validation
        link_result = self.validate_links()
        validations.append(link_result)

        # File structure validation
        structure_result = self.validate_file_structure()
        validations.append(structure_result)

        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()

        # Calculate overall results
        total_validations = len(validations)
        passed_validations = len([v for v in validations if v["success"]])
        overall_success = passed_validations == total_validations
        overall_score = sum(v.get("score", 0) for v in validations) / total_validations

        # Generate comprehensive report
        report = {
            "timestamp": start_time.isoformat(),
            "duration": total_duration,
            "overall_success": overall_success,
            "overall_score": overall_score,
            "total_validations": total_validations,
            "passed_validations": passed_validations,
            "failed_validations": total_validations - passed_validations,
            "validations": validations,
            "thresholds": self.thresholds
        }

        # Save report
        report_file = f"validation_report_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Print summary
        self.print_validation_summary(report)

        print(f"📄 Validation report saved: {report_file}")

        return report

    def print_validation_summary(self, report: Dict[str, Any]) -> None:
        """Print comprehensive validation summary"""
        print("\n" + "=" * 60)
        print("🎯 VALIDATION SUMMARY")
        print("=" * 60)

        print(f"Overall Status: {'✅ PASSED' if report['overall_success'] else '❌ FAILED'}")
        print(f"Overall Score: {report['overall_score']:.1%}")
        print(f"Duration: {report['duration']:.2f}s")
        print(f"Validations: {report['passed_validations']}/{report['total_validations']} passed")

        print("\n📋 Validation Details:")
        for validation in report["validations"]:
            status = "✅" if validation["success"] else "❌"
            score = validation.get("score", 0.0)
            validation_type = validation["type"].title()

            print(f"  {status} {validation_type}: {score:.1%}")

            if not validation["success"] and "error" not in validation:
                # Show some details for failed validations
                if validation["type"] == "documentation":
                    failed = validation.get("failed_checks", 0)
                    print(f"    Failed checks: {failed}")
                elif validation["type"] == "examples":
                    failed = validation.get("failed_examples", 0)
                    print(f"    Failed examples: {failed}")
                elif validation["type"] == "templates":
                    ineffective = validation.get("ineffective_templates", 0)
                    print(f"    Ineffective templates: {ineffective}")
                elif validation["type"] == "links":
                    broken = validation.get("broken_links", 0)
                    print(f"    Broken links: {broken}")
                elif validation["type"] == "file_structure":
                    missing = validation.get("missing_count", 0)
                    print(f"    Missing items: {missing}")

        if report["overall_success"]:
            print("\n🎉 ALL VALIDATIONS PASSED!")
            print("✨ Documentation and examples are ready for users")
        else:
            print("\n⚠️ SOME VALIDATIONS FAILED")
            print("🔧 Please address the issues above before release")

        print("=" * 60)


async def main():
    """Main validation execution"""
    parser = argparse.ArgumentParser(description="Run comprehensive validation")
    parser.add_argument("--types", "-t", nargs="+",
                       choices=["documentation", "examples", "templates", "links", "structure"],
                       help="Specific validation types to run")
    parser.add_argument("--threshold", type=float, default=0.90,
                       help="Minimum overall score required for success")
    parser.add_argument("--output", "-o", default=None,
                       help="Output file for validation report")

    args = parser.parse_args()

    validator = ComprehensiveValidator()

    # Update thresholds if specified
    if args.threshold:
        for key in validator.thresholds:
            validator.thresholds[key] = args.threshold

    # Run validations
    report = await validator.run_all_validations()

    # Save to custom output file if specified
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"📄 Report also saved to: {args.output}")

    # Exit with appropriate code
    success = report["overall_success"] and report["overall_score"] >= args.threshold
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
