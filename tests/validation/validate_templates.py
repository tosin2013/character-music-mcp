#!/usr/bin/env python3
"""
Validation script for testing PromptTemplateSystem functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the validation directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from prompt_template_system import PromptTemplateSystem

async def main():
    """Run prompt template validation tests"""
    print("=== Prompt Template System Validation ===\n")
    
    # Initialize the system
    system = PromptTemplateSystem()
    
    # Test 1: Load templates
    print("1. Testing template loading...")
    templates = system.load_templates()
    print(f"   Loaded {len(templates)} templates")
    
    if templates:
        print("   Template names:")
        for name in templates.keys():
            print(f"   - {name}")
    
    # Test 2: Test individual template
    if templates:
        print(f"\n2. Testing individual template...")
        first_template_name = next(iter(templates.keys()))
        first_template = templates[first_template_name]
        
        print(f"   Testing: {first_template_name}")
        print(f"   Use case: {first_template.use_case}")
        print(f"   Difficulty: {first_template.difficulty_level}")
        
        # Fill the template
        filled = system.fill_template(first_template)
        print(f"   Filled template length: {len(filled)} characters")
        
        # Test the template
        try:
            result = await system.test_template(first_template)
            print(f"   Test status: {result.test_status}")
            print(f"   Effectiveness score: {result.effectiveness_score:.2f}")
            print(f"   Character confidence: {result.character_confidence:.2f}")
            print(f"   Completeness score: {result.completeness_score:.2f}")
            if result.recommendations:
                print(f"   Recommendations: {', '.join(result.recommendations)}")
        except Exception as e:
            print(f"   Error during testing: {e}")
    
    # Test 3: Test all templates
    if templates:
        print(f"\n3. Testing all templates...")
        try:
            report = await system.test_all_templates()
            print(f"   Total templates: {report.total_templates}")
            print(f"   Passed: {report.passed_templates}")
            print(f"   Failed: {report.failed_templates}")
            print(f"   Warnings: {report.warning_templates}")
            print(f"   Average effectiveness: {report.average_effectiveness:.2f}")
            print(f"   Average execution time: {report.average_execution_time:.2f}s")
            
            # Show top templates
            if report.template_rankings:
                print("\n   Top 3 templates by effectiveness:")
                for i, template in enumerate(report.template_rankings[:3], 1):
                    print(f"   {i}. {template['name']}: {template['effectiveness_score']:.2f}")
            
            # Show improvement suggestions
            if report.improvement_suggestions:
                print("\n   Improvement suggestions:")
                for suggestion in report.improvement_suggestions:
                    print(f"   - {suggestion}")
            
            # Generate report files
            output_dir = Path("tests/validation/reports")
            output_dir.mkdir(exist_ok=True)
            
            report_path = output_dir / "template_validation_report.json"
            system.generate_template_report(report, str(report_path))
            print(f"\n   Report saved to: {report_path}")
            
        except Exception as e:
            print(f"   Error during full testing: {e}")
    
    # Test 4: Create a new template
    print("\n4. Testing template creation...")
    try:
        new_template = system.create_template(
            name="Test Template",
            use_case="Testing template creation",
            template_text="[CHARACTER_NAME] was a [PERSONALITY_TRAIT] person who lived in [LOCATION].",
            placeholder_descriptions={
                "CHARACTER_NAME": "Name of the character",
                "PERSONALITY_TRAIT": "Main personality trait",
                "LOCATION": "Where they live"
            },
            example_values={
                "CHARACTER_NAME": "Elena",
                "PERSONALITY_TRAIT": "introspective",
                "LOCATION": "the city"
            }
        )
        
        print(f"   Created template: {new_template.name}")
        
        # Test the new template
        filled = system.fill_template(new_template)
        print(f"   Filled template: {filled}")
        
        result = await system.test_template(new_template)
        print(f"   Test result: {result.test_status} (effectiveness: {result.effectiveness_score:.2f})")
        
    except Exception as e:
        print(f"   Error creating template: {e}")
    
    # Test 5: Template verification
    print("\n5. Testing template verification...")
    if system.test_results:
        template_names = [r.template_name for r in system.test_results[:3]]
        verification = system.verify_templates_produce_expected_results(template_names)
        
        print("   Verification results:")
        for name, passed in verification.items():
            print(f"   - {name}: {'✓' if passed else '✗'}")
    else:
        print("   No test results available for verification")
    
    print("\n=== Validation Complete ===")

if __name__ == "__main__":
    asyncio.run(main())