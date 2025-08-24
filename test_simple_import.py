#!/usr/bin/env python3
"""
Simple import test to verify module availability
"""
import sys
import os
from pathlib import Path

def test_enhanced_genre_mapper_import():
    """Test that enhanced_genre_mapper can be imported"""
    try:
        import enhanced_genre_mapper
        print("✅ enhanced_genre_mapper imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import enhanced_genre_mapper: {e}")
        
        # Try adding current directory to path
        current_dir = Path(__file__).parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
            
        try:
            import enhanced_genre_mapper
            print("✅ enhanced_genre_mapper imported successfully after path fix")
            return True
        except ImportError as e2:
            print(f"❌ Still failed after path fix: {e2}")
            return False

if __name__ == "__main__":
    print("=== Simple Import Test ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")
    
    success = test_enhanced_genre_mapper_import()
    sys.exit(0 if success else 1)