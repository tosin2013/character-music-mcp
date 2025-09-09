#!/usr/bin/env python3
"""
Fix import issues in generated test files
"""

import os
import glob

def fix_test_file(filepath):
    """Fix import and fixture issues in a test file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Fix pytest_asyncio import and fixture usage
        if 'pytest_asyncio' in content and 'import pytest_asyncio' not in content:
            content = content.replace('import pytest', 'import pytest\nimport pytest_asyncio')
        
        # Fix fixture decorators
        content = content.replace('@pytest_asyncio.fixture', '@pytest.fixture')
        
        # Write back
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed {filepath}")
        
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")

def main():
    """Fix all generated test files"""
    test_files = glob.glob('tests/unit/test_*.py')
    
    for test_file in test_files:
        if any(module in test_file for module in [
            'enhanced_beat_generator', 'enhanced_cache_manager', 
            'enhanced_emotional_analyzer', 'enhanced_understand_topic_emotions',
            'demo_config_management', 'demo_performance_monitoring',
            'mcp_data_utilities', 'mcp_tool_utils', 
            'validate_standard_character_profile', 'debug_imports'
        ]):
            fix_test_file(test_file)

if __name__ == "__main__":
    main()