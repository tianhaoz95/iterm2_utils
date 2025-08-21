#!/usr/bin/env python3
"""
Test runner for append_python_path module
"""

import subprocess
import sys
import os


def run_tests():
    """Run all tests for the append_python_path module"""

    # Change to the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print("Running tests for append_python_path module...")
    print("=" * 50)

    # Run pytest tests
    try:
        # Try running pytest-style tests first
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "test_append_python_path_pytest.py",
            "-v", "--tb=short"
        ], capture_output=True, text=True)

        print("PYTEST OUTPUT:")
        print(result.stdout)
        if result.stderr:
            print("PYTEST ERRORS:")
            print(result.stderr)

        if result.returncode == 0:
            print("\n✅ All pytest tests passed!")
        else:
            print(f"\n❌ Pytest tests failed with return code {result.returncode}")

    except FileNotFoundError:
        print("❌ pytest not found. Please install pytest and pytest-asyncio:")
        print("   pip install pytest pytest-asyncio")
        return 1

    print("\n" + "=" * 50)
    print("Test run complete!")

    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
