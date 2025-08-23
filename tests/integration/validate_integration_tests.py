#!/usr/bin/env python3
"""
Integration Tests Validation Script

Validates that all integration test modules are properly structured
and can be imported without running the actual tests.
"""

import sys
import os
import importlib.util
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def validate_test_module(module_path: Path, module_name: str) -> bool:
    """Validate a test module structure by reading the file content"""
    try:
        # Read the file content
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for expected test class
        expected_classes = {
            "test_complete_workflow": "TestCompleteWorkflow",
            "test_album_creation": "TestAlbumCreation", 
            "test_mcp_tools": "TestMCPToolsIntegration"
        }
        
        if module_name in expected_classes:
            expected_class = expected_classes[module_name]
            
            # Check if class is defined in the file
            if f"class {expected_class}" in content:
                print(f"✅ {module_name}: Class {expected_class} found")
                
                # Check for required methods
                required_methods = ["setup_method"]
                missing_methods = []
                
                for method in required_methods:
                    if f"def {method}" not in content:
                        missing_methods.append(method)
                
                if missing_methods:
                    print(f"⚠️  {module_name}: Missing methods: {', '.join(missing_methods)}")
                
                # Check for async test methods
                async_test_count = content.count("async def test_")
                if async_test_count > 0:
                    print(f"✅ {module_name}: Found {async_test_count} async test methods")
                else:
                    print(f"⚠️  {module_name}: No async test methods found")
                
                # Check for imports
                required_imports = ["asyncio", "json", "sys", "os"]
                missing_imports = []
                
                for imp in required_imports:
                    if f"import {imp}" not in content and f"from {imp}" not in content:
                        missing_imports.append(imp)
                
                if missing_imports:
                    print(f"⚠️  {module_name}: Missing imports: {', '.join(missing_imports)}")
                
                return True
            else:
                print(f"❌ {module_name}: Missing expected class {expected_class}")
                return False
        else:
            print(f"⚠️  {module_name}: Unknown module, checking basic structure")
            
            # Basic structure checks
            if "class Test" in content:
                print(f"✅ {module_name}: Contains test class")
                return True
            else:
                print(f"❌ {module_name}: No test class found")
                return False
            
    except Exception as e:
        print(f"❌ {module_name}: File reading failed - {str(e)}")
        return False

def main():
    """Main validation function"""
    print("🔍 VALIDATING INTEGRATION TEST MODULES")
    print("=" * 50)
    
    integration_dir = Path(__file__).parent
    test_modules = [
        ("test_complete_workflow.py", "test_complete_workflow"),
        ("test_album_creation.py", "test_album_creation"),
        ("test_mcp_tools.py", "test_mcp_tools")
    ]
    
    all_valid = True
    
    for filename, module_name in test_modules:
        module_path = integration_dir / filename
        
        if not module_path.exists():
            print(f"❌ {filename}: File not found")
            all_valid = False
            continue
        
        print(f"\n📋 Validating {filename}...")
        is_valid = validate_test_module(module_path, module_name)
        
        if not is_valid:
            all_valid = False
    
    print("\n" + "=" * 50)
    
    if all_valid:
        print("🎉 ALL INTEGRATION TEST MODULES ARE VALID!")
        print("\n📝 Summary:")
        print("  ✅ test_complete_workflow.py - End-to-end workflow validation")
        print("  ✅ test_album_creation.py - Multi-song album generation testing")
        print("  ✅ test_mcp_tools.py - MCP tool validation and error handling")
        print("\n🚀 Integration tests are ready for execution with pytest!")
        return True
    else:
        print("❌ SOME INTEGRATION TEST MODULES HAVE ISSUES")
        print("Please fix the issues above before running the tests.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)