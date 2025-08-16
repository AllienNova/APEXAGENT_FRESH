"""
Test runner for Knowledge Integration tests

This module provides a test runner for the knowledge integration tests,
ensuring that the src directory is properly added to the Python path.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import os
import sys
import unittest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the test module
from tests.test_knowledge_integration import *

if __name__ == '__main__':
    unittest.main()
