#!/usr/bin/env python3
"""
Test runner for MCP Atlassian.

This script runs all tests or specific test modules based on command line arguments.

Usage:
    python run_tests.py                   # Run all tests
    python run_tests.py test_custom_fields  # Run only the custom fields tests
"""

import unittest
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == '__main__':
    # Set up the test loader
    loader = unittest.TestLoader()
    
    # Determine which tests to run
    if len(sys.argv) > 1:
        # Run specific test modules
        test_names = sys.argv[1:]
        test_suite = unittest.TestSuite()
        for test_name in test_names:
            # If it's a module name, load the module
            if test_name.endswith('.py'):
                test_name = test_name[:-3]  # Remove .py extension
            
            # Try to import and add to the suite
            try:
                module = __import__(test_name)
                test_suite.addTest(loader.loadTestsFromModule(module))
            except ImportError:
                # If it's not a module, try as a class or method
                try:
                    test_suite.addTest(loader.loadTestsFromName(test_name))
                except Exception as e:
                    print(f"Error loading test {test_name}: {e}")
                    sys.exit(1)
    else:
        # Run all tests
        test_suite = loader.discover('tests')
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with proper status code
    sys.exit(not result.wasSuccessful())