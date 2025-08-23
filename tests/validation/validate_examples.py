#!/usr/bin/env python3
"""
Validation script for testing ExampleGenerator functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the validation directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from example_generator import ExampleGenerator

async def main():
    """Run example validation tests"""
    print("=== Example Generator Validation ===\n")
    
    # Initialize the generator
    generator = ExampleGenerator()
    
    # Test 1: Discover examples
    print("1. Testing example discovery...")
    examples = generator.discover_examples()
    print(f"   Found {len(examples)} examples")
    
    if examples:
        print("   Example types found:")
        types = set(ex['type'] for ex in examples)
        for ex_type in types:
            count = sum(1 for ex in examples if ex['type'] == ex_type)
            print(f"   - {ex_type}: {count}")
    
    # Test 2: Validate a few examples if available
    if examples:
        print(f"\n2. Testing example validation (first 3 examples)...")
        for i, example in enumerate(examples[:3]):
            print(f"   Validating: {example['name']}")
            try:
                result = await generator.validate_example(example)
                print(f"   - Status: {result.validation_status}")
                print(f"   - Accuracy: {result.accuracy_score:.2f}")
                print(f"   - Completeness: {result.completeness_score:.2f}")
                if result.error_message:
                    print(f"   - Error: {result.error_message}")
            except Exception as e:
                print(f"   - Error during validation: {e}")
            print()
    
    # Test 3: Full validation report
    print("3. Testing full validation report...")
    try:
        report = await generator.validate_all_examples()
        print(f"   Total examples: {report.total_examples}")
        print(f"   Passed: {report.passed_examples}")
        print(f"   Failed: {report.failed_examples}")
        print(f"   Warnings: {report.warning_examples}")
        print(f"   Success rate: {report.overall_success_rate*100:.1f}%")
        
        # Generate report files
        output_dir = Path("tests/validation/reports")
        output_dir.mkdir(exist_ok=True)
        
        report_path = output_dir / "validation_report.json"
        generator.generate_validation_report(report, str(report_path))
        print(f"   Report saved to: {report_path}")
        
    except Exception as e:
        print(f"   Error during full validation: {e}")
    
    # Test 4: Missing examples identification
    print("\n4. Testing missing examples identification...")
    missing = generator._identify_missing_examples()
    if missing:
        print("   Missing example areas:")
        for area in missing:
            print(f"   - {area}")
    else:
        print("   No missing example areas identified")
    
    # Test 5: Code change impact
    print("\n5. Testing code change impact analysis...")
    changed_files = ['server.py', 'working_universal_processor.py']
    examples_to_update = generator.update_examples_when_code_changes(changed_files)
    print(f"   Examples to update after code changes: {examples_to_update}")
    
    print("\n=== Validation Complete ===")

if __name__ == "__main__":
    asyncio.run(main())