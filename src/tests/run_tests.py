#!/usr/bin/env python3
"""
Test runner for SwarmTunnel test suites
Allows running specific test categories or all tests for both install.py and start.py
"""

import os
import sys

# Running this runner from repo root or from src/tests should both work.
# Compute directories relative to this file (src/tests/run_tests.py).
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))   # .../src/tests
SRC_DIR = os.path.abspath(os.path.join(TESTS_DIR, ".."))  # .../src

# Ensure src/ is on sys.path so `from swarmtunnel import ...` works.
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Ensure tests dir is on sys.path so local imports like `import test_install` work
# when the script is executed from elsewhere.
if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)
# During test runs, avoid detecting or using a system-wide cloudflared so tests
# are deterministic (CI/dev machines may have cloudflared installed).
os.environ.setdefault('SWARMTUNNEL_IGNORE_SYSTEM_CLOUDFLARED', '1')
    
import unittest
import argparse

def run_install_unit_tests():
    """Run only install.py unit tests (fast, no external dependencies)"""
    print("🧪 Running Install.py Unit Tests...")
    print("=" * 50)
    
    from test_install import (
        TestInstallationChecks,
        TestPlatformDetection,
        TestDownloadFunctions
    )
    
    test_classes = [
        TestInstallationChecks,
        TestPlatformDetection,
        TestDownloadFunctions
    ]
    
    return run_test_classes(test_classes)

def run_install_integration_tests():
    """Run install.py integration tests (moderate speed, some mocking)"""
    print("🔗 Running Install.py Integration Tests...")
    print("=" * 50)
    
    from test_install import (
        TestInstallationFunctions,
        TestIntegrationScenarios
    )
    
    test_classes = [
        TestInstallationFunctions,
        TestIntegrationScenarios
    ]
    
    return run_test_classes(test_classes)

def run_install_error_tests():
    """Run install.py error scenario tests"""
    print("⚠️  Running Install.py Error Scenario Tests...")
    print("=" * 50)
    
    from test_install import TestErrorScenarios
    
    test_classes = [TestErrorScenarios]
    
    return run_test_classes(test_classes)

def run_install_system_tests():
    """Run install.py system tests (requires internet connection)"""
    print("🌐 Running Install.py System Tests (requires internet)...")
    print("=" * 50)
    
    from test_install import TestSystemInstallation
    
    test_classes = [TestSystemInstallation]
    
    return run_test_classes(test_classes)

def run_install_environment_tests():
    """Run install.py environment variable and CLI tests"""
    print("🔧 Running Install.py Environment & CLI Tests...")
    print("=" * 50)
    
    from test_install import (
        TestEnvironmentVariables,
        TestCLIArguments,
        TestWindowsPermissions,
        TestCleanupFunctionality,
        TestLANBinding
    )
    
    test_classes = [
        TestEnvironmentVariables,
        TestCLIArguments,
        TestWindowsPermissions,
        TestCleanupFunctionality,
        TestLANBinding
    ]
    
    return run_test_classes(test_classes)

def run_start_unit_tests():
    """Run only start.py unit tests (fast, no external dependencies)"""
    print("🧪 Running Start.py Unit Tests...")
    print("=" * 50)
    
    from test_start import (
        TestDependencyChecking,
        TestSwarmUIBuilding,
        TestServiceWaiting,
        TestTunnelConfiguration
    )
    
    test_classes = [
        TestDependencyChecking,
        TestSwarmUIBuilding,
        TestServiceWaiting,
        TestTunnelConfiguration
    ]
    
    return run_test_classes(test_classes)

def run_start_integration_tests():
    """Run start.py integration tests (moderate speed, some mocking)"""
    print("🔗 Running Start.py Integration Tests...")
    print("=" * 50)
    
    from test_start import (
        TestSwarmUIStarting,
        TestTunnelStarting,
        TestTunnelURLExtraction,
        TestIntegrationScenarios
    )
    
    test_classes = [
        TestSwarmUIStarting,
        TestTunnelStarting,
        TestTunnelURLExtraction,
        TestIntegrationScenarios
    ]
    
    return run_test_classes(test_classes)

def run_start_environment_tests():
    """Run start.py environment variable and CLI tests"""
    print("🔧 Running Start.py Environment & CLI Tests...")
    print("=" * 50)
    
    from test_start import (
        TestEnvironmentVariables,
        TestCLIArguments,
        TestWindowsPowerShellFunctionality,
        TestLocalInstallationChecks
    )
    
    test_classes = [
        TestEnvironmentVariables,
        TestCLIArguments,
        TestWindowsPowerShellFunctionality,
        TestLocalInstallationChecks
    ]
    
    return run_test_classes(test_classes)

def run_start_error_tests():
    """Run start.py error scenario tests"""
    print("⚠️  Running Start.py Error Scenario Tests...")
    print("=" * 50)
    
    from test_start import (
        TestCleanup,
        TestErrorScenarios
    )
    
    test_classes = [
        TestCleanup,
        TestErrorScenarios
    ]
    
    return run_test_classes(test_classes)

def run_all_install_tests():
    """Run all install.py tests"""
    print("🚀 Running All Install.py Tests...")
    print("=" * 50)
    
    from test_install import (
        TestInstallationChecks,
        TestPlatformDetection,
        TestDownloadFunctions,
        TestInstallationFunctions,
        TestIntegrationScenarios,
        TestErrorScenarios,
        TestSystemInstallation,
        TestEnvironmentVariables,
        TestCLIArguments,
        TestWindowsPermissions,
        TestCleanupFunctionality,
        TestLANBinding
    )
    
    test_classes = [
        TestInstallationChecks,
        TestPlatformDetection,
        TestDownloadFunctions,
        TestInstallationFunctions,
        TestIntegrationScenarios,
        TestErrorScenarios,
        TestSystemInstallation,
        TestEnvironmentVariables,
        TestCLIArguments,
        TestWindowsPermissions,
        TestCleanupFunctionality,
        TestLANBinding
    ]
    
    return run_test_classes(test_classes)

def run_all_start_tests():
    """Run all start.py tests"""
    print("🚀 Running All Start.py Tests...")
    print("=" * 50)
    
    from test_start import (
        TestDependencyChecking,
        TestSwarmUIBuilding,
        TestServiceWaiting,
        TestSwarmUIStarting,
        TestTunnelConfiguration,
        TestTunnelStarting,
        TestTunnelURLExtraction,
        TestCleanup,
        TestIntegrationScenarios,
        TestEnvironmentVariables,
        TestCLIArguments,
        TestWindowsPowerShellFunctionality,
        TestLocalInstallationChecks,
        TestErrorScenarios
    )
    
    test_classes = [
        TestDependencyChecking,
        TestSwarmUIBuilding,
        TestServiceWaiting,
        TestSwarmUIStarting,
        TestTunnelConfiguration,
        TestTunnelStarting,
        TestTunnelURLExtraction,
        TestCleanup,
        TestIntegrationScenarios,
        TestEnvironmentVariables,
        TestCLIArguments,
        TestWindowsPowerShellFunctionality,
        TestLocalInstallationChecks,
        TestErrorScenarios
    ]
    
    return run_test_classes(test_classes)

def run_all_tests():
    """Run all tests from both test suites"""
    print("🚀 Running All Tests (Install.py + Start.py)...")
    print("=" * 50)
    
    install_success = run_all_install_tests()
    print("\n" + "=" * 50)
    start_success = run_all_start_tests()
    
    return install_success and start_success

def run_test_classes(test_classes):
    """Helper function to run a list of test classes"""
    test_suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

def main():
    parser = argparse.ArgumentParser(description='Run tests for SwarmTunnel (install.py and start.py)')
    parser.add_argument('--type', choices=[
        'install-unit', 'install-integration', 'install-error', 'install-system', 'install-env', 'install-all',
        'start-unit', 'start-integration', 'start-error', 'start-env', 'start-all',
        'all'
    ], default='all', help='Type of tests to run')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Verbose output')
    
    args = parser.parse_args()
    
    print("🧪 SwarmTunnel Test Suite")
    print("=" * 60)
    
    success = False
    
    if args.type == 'install-unit':
        success = run_install_unit_tests()
    elif args.type == 'install-integration':
        success = run_install_integration_tests()
    elif args.type == 'install-error':
        success = run_install_error_tests()
    elif args.type == 'install-system':
        success = run_install_system_tests()
    elif args.type == 'install-env':
        success = run_install_environment_tests()
    elif args.type == 'install-all':
        success = run_all_install_tests()
    elif args.type == 'start-unit':
        success = run_start_unit_tests()
    elif args.type == 'start-integration':
        success = run_start_integration_tests()
    elif args.type == 'start-error':
        success = run_start_error_tests()
    elif args.type == 'start-env':
        success = run_start_environment_tests()
    elif args.type == 'start-all':
        success = run_all_start_tests()
    elif args.type == 'all':
        success = run_all_tests()
    
    print("=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    print("\n💡 Test Categories:")
    print("  Install.py Tests:")
    print("    install-unit        - Fast unit tests (no external dependencies)")
    print("    install-integration - Integration tests (mocked dependencies)")
    print("    install-error       - Error handling and edge cases")
    print("    install-system      - System tests (requires internet)")
    print("    install-env         - Environment variables and CLI tests")
    print("    install-all         - All install.py tests")
    print("  Start.py Tests:")
    print("    start-unit          - Fast unit tests (no external dependencies)")
    print("    start-integration   - Integration tests (mocked dependencies)")
    print("    start-error         - Error handling and cleanup tests")
    print("    start-env           - Environment variables and CLI tests")
    print("    start-all           - All start.py tests")
    print("  Combined:")
    print("    all                 - All tests from both suites")
    
    print("\n🌐 For system tests requiring internet:")
    print("  TEST_WITH_INTERNET=1 python run_tests.py --type install-system")
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
