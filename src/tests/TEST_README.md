# Testing Strategy for SwarmTunnel

This document explains the comprehensive testing approach implemented for the SwarmTunnel project, covering both `install.py` and `start.py` scripts.

## 🎯 Testing Philosophy

The testing strategy follows **expert software testing principles**:

1. **Multi-Layer Testing**: Unit → Integration → System → Error scenarios
2. **Isolation**: Each test runs in a clean environment
3. **Mocking**: External dependencies are mocked for reliable testing
4. **Coverage**: Tests cover success, failure, and edge cases
5. **Cross-Platform**: Tests verify behavior across different OS/architectures
6. **Real-World**: Some tests use actual network calls for integration validation

## 📁 Test Files

- `test_install.py` - Comprehensive test suite for `install.py` functionality
- `test_start.py` - Comprehensive test suite for `start.py` functionality
- `run_tests.py` - Test runner with category selection for both test suites
- `run_tests.bat` - Windows batch file for easy test execution from top-level directory
- `TEST_README.md` - This documentation

## 🧪 Test Categories

### Install.py Test Suite

#### 1. **Unit Tests** (`TestInstallationChecks`, `TestPlatformDetection`, `TestDownloadFunctions`)
- **Purpose**: Test individual functions in isolation
- **Speed**: Fast (no external dependencies)
- **Coverage**: Pure functions, platform detection, file operations
- **Mocking**: Minimal mocking required

**Examples:**
- Installation detection functions
- Platform-specific URL generation
- File download and extraction functions

#### 2. **Integration Tests** (`TestInstallationFunctions`, `TestIntegrationScenarios`)
- **Purpose**: Test function interactions and complete workflows
- **Speed**: Moderate (some mocking)
- **Coverage**: Installation functions, idempotent behavior
- **Mocking**: External dependencies (git, network, file system)

**Examples:**
- Complete installation workflows
- Idempotent installation behavior
- Cross-platform installation scenarios

#### 3. **Error Scenario Tests** (`TestErrorScenarios`)
- **Purpose**: Test error handling and edge cases
- **Speed**: Fast (mocked failures)
- **Coverage**: Network failures, permission issues, cleanup
- **Mocking**: Failure conditions

**Examples:**
- Network connection failures
- Insufficient disk space
- Permission denied errors
- Git not installed scenarios

#### 4. **System Tests** (`TestSystemInstallation`)
- **Purpose**: Test with real external dependencies
- **Speed**: Slow (requires internet)
- **Coverage**: Actual git clone, actual downloads
- **Mocking**: None (real network calls)

**Examples:**
- Actual git repository cloning
- Real cloudflared binary downloads

#### 5. **Environment & CLI Tests** (`TestEnvironmentVariables`, `TestCLIArguments`, `TestWindowsPermissions`, `TestCleanupFunctionality`, `TestLANBinding`)
- **Purpose**: Test environment variable overrides and CLI arguments
- **Speed**: Fast (mocked environment)
- **Coverage**: Environment variable handling, CLI parsing, Windows permissions
- **Mocking**: Environment variables, file permissions

**Examples:**
- Environment variable overrides for directories
- CLI flag parsing (`--force-local-swarmui`, `--force-local-cloudflared`)
- Windows permission fixing
- LAN binding configuration

### Start.py Test Suite

#### 1. **Unit Tests** (`TestDependencyChecking`, `TestSwarmUIBuilding`, `TestServiceWaiting`, `TestTunnelConfiguration`)
- **Purpose**: Test individual functions in isolation
- **Speed**: Fast (no external dependencies)
- **Coverage**: Dependency checking, service waiting, configuration
- **Mocking**: Minimal mocking required

**Examples:**
- Dependency checking (SwarmUI, cloudflared, .NET)
- SwarmUI building verification
- Service availability checking
- Tunnel configuration file creation

#### 2. **Integration Tests** (`TestSwarmUIStarting`, `TestTunnelStarting`, `TestTunnelURLExtraction`, `TestIntegrationScenarios`)
- **Purpose**: Test function interactions and complete workflows
- **Speed**: Moderate (some mocking)
- **Coverage**: Process starting, URL extraction, complete workflows
- **Mocking**: Subprocess calls, network requests

**Examples:**
- SwarmUI startup in new PowerShell windows
- Cloudflare tunnel startup and URL extraction
- Complete workflow from dependency check to tunnel URL
- Windows PowerShell integration

#### 3. **Environment & CLI Tests** (`TestEnvironmentVariables`, `TestCLIArguments`, `TestWindowsPowerShellFunctionality`, `TestLocalInstallationChecks`)
- **Purpose**: Test environment variable overrides, CLI arguments, and Windows-specific functionality
- **Speed**: Fast (mocked environment)
- **Coverage**: Environment variables, CLI parsing, PowerShell integration
- **Mocking**: Environment variables, platform detection

**Examples:**
- Environment variable overrides for directories
- CLI flag parsing (`--force-local-swarmui`, `--force-local-cloudflared`)
- Windows PowerShell process launching
- Local installation checking

#### 4. **Error & Cleanup Tests** (`TestCleanup`, `TestErrorScenarios`)
- **Purpose**: Test error handling, cleanup, and edge cases
- **Speed**: Fast (mocked failures)
- **Coverage**: Process cleanup, error scenarios, graceful degradation
- **Mocking**: Process failures, file operations

**Examples:**
- Process termination and cleanup
- Error handling in dependency checks
- Graceful failure scenarios
- File cleanup on errors

## 🚀 Running Tests

### Quick Start (Windows)
```batch
# Run all tests (both install.py and start.py)
run_tests.bat

# Run only install.py tests
run_tests.bat --type install-all

# Run only start.py tests
run_tests.bat --type start-all

# Run only unit tests (fastest)
run_tests.bat --type install-unit
run_tests.bat --type start-unit

# Run integration tests
run_tests.bat --type install-integration
run_tests.bat --type start-integration

# Run error scenario tests
run_tests.bat --type install-error
run_tests.bat --type start-error

# Run environment and CLI tests
run_tests.bat --type install-env
run_tests.bat --type start-env

# Run system tests (requires internet)
set TEST_WITH_INTERNET=1
run_tests.bat --type install-system
```

### Quick Start (All Platforms)
```bash
# Run all tests (both install.py and start.py)
python run_tests.py

# Run only install.py tests
python run_tests.py --type install-all

# Run only start.py tests
python run_tests.py --type start-all

# Run only unit tests (fastest)
python run_tests.py --type install-unit
python run_tests.py --type start-unit

# Run integration tests
python run_tests.py --type install-integration
python run_tests.py --type start-integration

# Run error scenario tests
python run_tests.py --type install-error
python run_tests.py --type start-error

# Run environment and CLI tests
python run_tests.py --type install-env
python run_tests.py --type start-env

# Run system tests (requires internet)
TEST_WITH_INTERNET=1 python run_tests.py --type install-system
```

### Direct Test Execution
```bash
# Run the main test files directly
python test_install.py
python test_start.py

# Run with internet tests
TEST_WITH_INTERNET=1 python test_install.py
```

## 📊 Test Coverage

### **Install.py Test Suite** (50+ tests)

#### **Unit Tests** (15+ tests)
- ✅ Installation detection (SwarmUI, cloudflared)
- ✅ Platform detection (Windows, macOS, Linux)
- ✅ Architecture mapping (x86_64, ARM64, ARM, 386)
- ✅ URL generation for all platforms
- ✅ File download success/failure
- ✅ Archive extraction (ZIP, tar.gz)
- ✅ File corruption handling

#### **Integration Tests** (5+ tests)
- ✅ Complete installation workflows
- ✅ Idempotent installation behavior
- ✅ Cross-platform installation scenarios
- ✅ Function interaction testing

#### **Error Scenario Tests** (6+ tests)
- ✅ Git not installed
- ✅ Network failures
- ✅ Insufficient disk space
- ✅ Permission denied
- ✅ Cleanup on failure
- ✅ Partial file cleanup

#### **System Tests** (2+ tests)
- ✅ Actual git repository cloning
- ✅ Real cloudflared binary downloads

#### **Environment & CLI Tests** (20+ tests)
- ✅ Environment variable overrides
- ✅ CLI argument parsing
- ✅ Windows permission fixing
- ✅ LAN binding configuration
- ✅ Cleanup functionality

### **Start.py Test Suite** (40+ tests)

#### **Unit Tests** (15+ tests)
- ✅ Dependency checking (SwarmUI, cloudflared, .NET)
- ✅ SwarmUI building verification
- ✅ Service availability checking
- ✅ Tunnel configuration creation
- ✅ Launcher script finding

#### **Integration Tests** (10+ tests)
- ✅ SwarmUI startup in PowerShell windows
- ✅ Cloudflare tunnel startup
- ✅ URL extraction from tunnel output
- ✅ Complete workflow testing
- ✅ Windows PowerShell integration

#### **Environment & CLI Tests** (15+ tests)
- ✅ Environment variable overrides
- ✅ CLI argument parsing
- ✅ Windows PowerShell functionality
- ✅ Local installation checking
- ✅ DummyProcess handling

#### **Error & Cleanup Tests** (5+ tests)
- ✅ Process cleanup and termination
- ✅ Error handling scenarios
- ✅ Graceful failure handling
- ✅ File cleanup operations

## 🔧 Test Implementation Details

### **Test Isolation**
Each test class uses `setUp()` and `tearDown()` methods:
```python
def setUp(self):
    self.temp_dir = tempfile.mkdtemp()
    self.original_cwd = os.getcwd()
    os.chdir(self.temp_dir)

def tearDown(self):
    os.chdir(self.original_cwd)
    shutil.rmtree(self.temp_dir)
```

### **Mocking Strategy**
- **Platform detection**: Mock `platform.system()` and `platform.machine()`
- **Network operations**: Mock `urllib.request.urlretrieve()`
- **File operations**: Mock `os.chmod()` for permission tests
- **Subprocess calls**: Mock `subprocess.run()` and `subprocess.Popen()`
- **Environment variables**: Mock `os.environ` for environment tests

### **Assertion Patterns**
```python
# Function return value testing
self.assertTrue(is_cloudflared_installed())

# URL generation testing
self.assertIn("windows-amd64.exe", url)

# Error handling testing
with self.assertRaises(urllib.error.URLError):
    download_file("http://invalid", "test.txt")

# Mock verification
mock_download.assert_called_once()

# Flexible string matching for emoji assertions
success_found = any("SwarmUI started successfully" in str(call) for call in mock_print.call_args_list)
self.assertTrue(success_found, "Expected success message not found")
```

## 🎯 Testing Best Practices Demonstrated

### **1. Arrange-Act-Assert Pattern**
```python
def test_download_file_success(self):
    # Arrange
    url = "http://example.com/test"
    dest = "test.txt"
    
    # Act
    with patch('urllib.request.urlretrieve') as mock_download:
        download_file(url, dest)
    
    # Assert
    mock_download.assert_called_once_with(url, dest)
```

### **2. Test Independence**
- Each test creates its own temporary directory
- Tests don't interfere with each other
- Clean setup/teardown for each test

### **3. Meaningful Assertions**
- Tests verify actual behavior, not implementation details
- Clear error messages when tests fail
- Comprehensive coverage of edge cases

### **4. Error Path Coverage**
- Tests both success and failure scenarios
- Validates error messages and cleanup behavior
- Ensures graceful degradation

### **5. Cross-Platform Compatibility**
- Tests handle different operating systems
- Platform-specific functionality is properly tested
- Environment variable handling across platforms

## 🔍 Debugging Failed Tests

### **Common Issues**
1. **Import errors**: Ensure proper path setup in test files
2. **Permission errors**: Tests create temporary files that need cleanup
3. **Mock issues**: Check that mocks are applied to the correct modules
4. **Environment variable conflicts**: Tests may interfere with each other's environment

### **Verbose Output**
```bash
# Windows
run_tests.bat --verbose

# All platforms
python run_tests.py --verbose
```

### **Running Individual Tests**
```bash
# Run specific test class
python -m unittest test_install.TestInstallationChecks
python -m unittest test_start.TestDependencyChecking

# Run specific test method
python -m unittest test_install.TestInstallationChecks.test_is_cloudflared_installed_when_not_present
python -m unittest test_start.TestDependencyChecking.test_check_dependencies_all_present
```

## 📈 Continuous Integration

This test suite is designed for CI/CD integration:

```yaml
# Example GitHub Actions workflow
- name: Run Install.py Unit Tests
  run: python run_tests.py --type install-unit

- name: Run Install.py Integration Tests
  run: python run_tests.py --type install-integration

- name: Run Start.py Unit Tests
  run: python run_tests.py --type start-unit

- name: Run Start.py Integration Tests
  run: python run_tests.py --type start-integration

- name: Run Error Tests
  run: |
    python run_tests.py --type install-error
    python run_tests.py --type start-error

- name: Run System Tests (with internet)
  run: TEST_WITH_INTERNET=1 python run_tests.py --type install-system

# Example Windows batch file usage (for local development)
# run_tests.bat --type install-unit
# run_tests.bat --type start-all
# run_tests.bat --type all --verbose
```

## 🎓 Learning Outcomes

This testing strategy demonstrates:

1. **Professional Testing Practices**: Industry-standard testing patterns
2. **Test Organization**: Logical grouping of test types by functionality
3. **Mocking Techniques**: How to isolate units for testing
4. **Error Handling**: Comprehensive failure scenario coverage
5. **Cross-Platform Testing**: Handling different operating systems
6. **CI/CD Integration**: Tests designed for automated environments
7. **Environment Management**: Proper handling of environment variables and CLI arguments
8. **Process Management**: Testing subprocess interactions and cleanup

## 🚀 Next Steps

To extend this test suite:

1. **Add Performance Tests**: Measure installation time and resource usage
2. **Add Security Tests**: Validate downloaded files, check checksums
3. **Add Load Tests**: Test with multiple concurrent installations
4. **Add Regression Tests**: Ensure new changes don't break existing functionality
5. **Add Documentation Tests**: Verify help text and error messages
6. **Add End-to-End Tests**: Test complete user workflows
7. **Add Stress Tests**: Test behavior under resource constraints

This comprehensive testing approach ensures both `install.py` and `start.py` scripts are robust, reliable, and maintainable across different environments and use cases.
