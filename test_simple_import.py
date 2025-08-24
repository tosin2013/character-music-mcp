#!/usr/bin/env python3
"""
Simple import test to verify module availability
"""
import sys
import os
from pathlib import Path

def test_enhanced_genre_mapper_import():
    """Test that enhanced_genre_mapper can be imported"""
    
    # First, check if the file exists
    current_dir = Path(__file__).parent
    enhanced_genre_mapper_file = current_dir / "enhanced_genre_mapper.py"
    print(f"File exists: {enhanced_genre_mapper_file.exists()}")
    
    if enhanced_genre_mapper_file.exists():
        print(f"File size: {enhanced_genre_mapper_file.stat().st_size} bytes")
        
        # Check if we can read the file
        try:
            with open(enhanced_genre_mapper_file, 'r') as f:
                first_line = f.readline().strip()
                print(f"First line: {first_line}")
        except Exception as e:
            print(f"❌ Cannot read file: {e}")
    
    # Test import dependencies first
    dependencies = [
        'wiki_data_models',
        'wiki_data_system', 
        'performance_monitor'
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ Dependency {dep}: OK")
        except ImportError as e:
            print(f"❌ Dependency {dep}: FAILED - {e}")
    
    try:
        import enhanced_genre_mapper
        print("✅ enhanced_genre_mapper imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import enhanced_genre_mapper: {e}")
        
        # Try adding current directory to path
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
            
        try:
            import enhanced_genre_mapper
            print("✅ enhanced_genre_mapper imported successfully after path fix")
            return True
        except ImportError as e2:
            print(f"❌ Still failed after path fix: {e2}")
            
            # Try to import with more detailed error info
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("enhanced_genre_mapper", enhanced_genre_mapper_file)
                if spec is None:
                    print("❌ Could not create module spec")
                    return False
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print("✅ enhanced_genre_mapper imported via importlib")
                return True
            except Exception as e3:
                print(f"❌ importlib also failed: {e3}")
                return False

if __name__ == "__main__":
    print("=== Simple Import Test ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")
    
    success = test_enhanced_genre_mapper_import()
    sys.exit(0 if success else 1)