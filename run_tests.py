#!/usr/bin/env python3
"""
Test Runner for Groq Speech SDK

This script runs all tests in the correct order and provides comprehensive
test coverage reporting.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit            # Run only unit tests
    python run_tests.py --e2e             # Run only end-to-end tests
    python run_tests.py --cli             # Run only CLI tests
    python run_tests.py --verbose         # Run with verbose output
"""

import unittest
import sys
import os
import argparse
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def discover_tests():
    """Discover all test modules."""
    test_dir = Path(__file__).parent / "tests"
    loader = unittest.TestLoader()
    
    # Discover all test modules
    suite = loader.discover(
        start_dir=str(test_dir),
        pattern="test_*.py",
        top_level_dir=str(Path(__file__).parent)
    )
    
    return suite

def run_unit_tests():
    """Run unit tests only."""
    print("🧪 Running Unit Tests")
    print("=" * 50)
    
    # Change to tests directory and run the test
    import os
    original_dir = os.getcwd()
    os.chdir(Path(__file__).parent / "tests")
    
    try:
        loader = unittest.TestLoader()
        
        # Unit test modules
        unit_tests = [
            "unit.test_speech_config"
        ]
        
        suite = unittest.TestSuite()
        for test_module in unit_tests:
            try:
                suite.addTests(loader.loadTestsFromName(test_module))
            except Exception as e:
                print(f"⚠️  Could not load {test_module}: {e}")
        
        return suite
    finally:
        os.chdir(original_dir)

def run_e2e_tests():
    """Run end-to-end tests only."""
    print("🧪 Running End-to-End Tests")
    print("=" * 50)
    
    # Change to tests directory and run the test
    import os
    original_dir = os.getcwd()
    os.chdir(Path(__file__).parent / "tests")
    
    try:
        loader = unittest.TestLoader()
        
        # E2E test modules
        e2e_tests = [
            "test_e2e_cli"
        ]
        
        suite = unittest.TestSuite()
        for test_module in e2e_tests:
            try:
                suite.addTests(loader.loadTestsFromName(test_module))
            except Exception as e:
                print(f"⚠️  Could not load {test_module}: {e}")
        
        return suite
    finally:
        os.chdir(original_dir)

def run_cli_tests():
    """Run CLI-specific tests only."""
    print("🧪 Running CLI Tests")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName("tests.test_cli_validation")
    return suite

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run Groq Speech SDK tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--e2e", action="store_true", help="Run only end-to-end tests")
    parser.add_argument("--cli", action="store_true", help="Run only CLI tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--failfast", "-f", action="store_true", help="Stop on first failure")
    
    args = parser.parse_args()
    
    # Determine which tests to run
    if args.unit:
        suite = run_unit_tests()
    elif args.e2e:
        suite = run_e2e_tests()
    elif args.cli:
        suite = run_cli_tests()
    else:
        # Run all tests
        print("🧪 Running All Tests")
        print("=" * 50)
        suite = discover_tests()
    
    # Set up test runner
    verbosity = 2 if args.verbose else 1
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        failfast=args.failfast,
        buffer=True
    )
    
    # Run tests
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    # Exit with appropriate code
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
