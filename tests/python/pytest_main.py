import sys
import pytest
import os
import glob

if __name__ == "__main__":
    # Buck2 bundles the specific test file with this runner.
    # Find the test file in the same directory as this script (excluding this file).
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = [
        f
        for f in glob.glob(os.path.join(script_dir, "test_*.py"))
        if os.path.basename(f) != "pytest_main.py"
    ]

    if test_files:
        # Run only the bundled test file
        test_file = test_files[0]
        sys.exit(pytest.main([test_file] + sys.argv[1:]))
    else:
        # Fallback: run tests in current directory if no test file found
        sys.exit(pytest.main([script_dir] + sys.argv[1:]))
