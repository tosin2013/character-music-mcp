#!/usr/bin/env python3
"""
Simple import test to verify basic module loading
Used by CI/CD pipeline to ensure core modules can be imported
"""

import os
import sys
import traceback


def test_basic_imports():
    """Test basic module imports"""

    print("🔍 Testing basic imports...")

    try:
        # Test core module imports
        import server
        print("✅ server module imported successfully")

        import mcp_tools_integration
        print("✅ mcp_tools_integration module imported successfully")

        import wiki_data_system
        print("✅ wiki_data_system module imported successfully")

        import enhanced_character_analyzer
        print("✅ enhanced_character_analyzer module imported successfully")

        import enhanced_emotional_analyzer
        print("✅ enhanced_emotional_analyzer module imported successfully")

        print("\n🎉 All basic imports successful!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return False

def test_optional_imports():
    """Test optional module imports that might not be critical"""

    print("\n🔍 Testing optional imports...")

    optional_modules = [
        'enhanced_beat_generator',
        'enhanced_genre_mapper',
        'dynamic_config_manager',
        'performance_monitor',
        'error_monitoring_system'
    ]

    success_count = 0

    for module_name in optional_modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name} imported successfully")
            success_count += 1
        except ImportError as e:
            print(f"⚠️  {module_name} import failed (optional): {e}")
        except Exception as e:
            print(f"❌ {module_name} unexpected error: {e}")

    print(f"\n📊 Optional imports: {success_count}/{len(optional_modules)} successful")
    return success_count

def main():
    """Main test function"""

    print("=" * 60)
    print("🧪 Simple Import Test")
    print("=" * 60)

    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    print(f"📁 Working directory: {current_dir}")
    print(f"🐍 Python version: {sys.version}")
    print(f"📚 Python path: {sys.path[:3]}...")  # Show first 3 entries

    # Run basic import tests
    basic_success = test_basic_imports()

    # Run optional import tests
    optional_count = test_optional_imports()

    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)

    if basic_success:
        print("✅ Basic imports: PASSED")
        print(f"📊 Optional imports: {optional_count} successful")
        print("\n🎉 Simple import test PASSED!")
        sys.exit(0)
    else:
        print("❌ Basic imports: FAILED")
        print("\n💥 Simple import test FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()

