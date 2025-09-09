#!/usr/bin/env python3
"""
Debug script to test imports in CI environment
"""
import os
import sys
from pathlib import Path

print("=== Import Debug Information ===")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path[:5]}...")  # First 5 entries
print(f"PYTHONPATH env: {os.environ.get('PYTHONPATH', 'Not set')}")

# Check if files exist
files_to_check = [
    'enhanced_genre_mapper.py',
    '__init__.py',
    'tests/conftest.py'
]

for file_path in files_to_check:
    exists = Path(file_path).exists()
    print(f"File {file_path}: {'EXISTS' if exists else 'MISSING'}")

# Try importing
try:
    import enhanced_genre_mapper
    print("✅ enhanced_genre_mapper import: SUCCESS")
    print(f"Module file: {enhanced_genre_mapper.__file__}")
except ImportError as e:
    print(f"❌ enhanced_genre_mapper import: FAILED - {e}")

try:
    from enhanced_genre_mapper import EnhancedGenreMapper
    print("✅ EnhancedGenreMapper class import: SUCCESS")
except ImportError as e:
    print(f"❌ EnhancedGenreMapper class import: FAILED - {e}")

print("=== End Debug Information ===")
