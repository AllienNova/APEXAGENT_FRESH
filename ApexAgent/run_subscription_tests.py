"""
Modified helper script to run the subscription system tests with proper import paths.

This script ensures that the parent directory of 'src' is in the Python path
before running the tests, allowing the test modules to import the
subscription package correctly.
"""

import os
import sys
import unittest

# Add the parent directory of src to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Now run the tests with modified imports
if __name__ == "__main__":
    # Create a test loader
    loader = unittest.TestLoader()
    
    # Load tests from the test file
    test_dir = os.path.join(project_root, 'tests', 'subscription')
    suite = loader.discover(test_dir)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
