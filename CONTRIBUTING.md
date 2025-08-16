# Contributing to SwarmTunnel

Thank you for your interest in contributing to SwarmTunnel! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** a feature branch
4. **Make** your changes
5. **Test** your changes thoroughly
6. **Submit** a pull request

## 📋 Prerequisites

- **Python 3.7+** installed and available in PATH
- **Git** installed and available in PATH
- **Windows**: Administrator privileges may be required for testing
- **Linux/macOS**: Python 3.7+ and Git required

## 🧪 Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/SwarmTunnel.git
cd SwarmTunnel
```

### 2. Run Tests

Before making changes, ensure all tests pass:

**Windows:**
```cmd
# Run all tests
python src/tests/run_tests.py

# Run specific test categories
python src/tests/run_tests.py --type install-unit
python src/tests/run_tests.py --type start-unit
```

**Linux/macOS:**
```bash
# Run all tests
python3 src/tests/run_tests.py

# Run specific test categories
python3 src/tests/run_tests.py --type install-unit
python3 src/tests/run_tests.py --type start-unit
```

### 3. Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards below

3. **Test your changes**:
   
   **Windows:**
   ```cmd
   # Run the specific tests related to your changes
   python src/tests/run_tests.py --type install-unit
   python src/tests/run_tests.py --type start-unit
   
   # Test the actual functionality
   python src/swarmtunnel/install.py --help
   python src/swarmtunnel/start.py --help
   ```
   
   **Linux/macOS:**
   ```bash
   # Run the specific tests related to your changes
   python3 src/tests/run_tests.py --type install-unit
   python3 src/tests/run_tests.py --type start-unit
   
   # Test the actual functionality
   python3 src/swarmtunnel/install.py --help
   python3 src/swarmtunnel/start.py --help
   ```

4. **Commit your changes** with clear, descriptive commit messages

## 📝 Coding Standards

### Python Code Style

- Use **4 spaces** for indentation (no tabs)
- Keep lines under **120 characters** when possible
- Use **descriptive variable names**
- Add **docstrings** for all functions and classes

### Commit Messages

Use clear, descriptive commit messages.

Examples:
```
feat: add new feature for cloudflared detection
fix: resolve Windows permission handling issue
docs: update README with new installation instructions
test: add comprehensive tests for error scenarios
```

### Code Organization

- **Keep functions focused** on a single responsibility
- **Add type hints** where helpful for clarity
- **Handle errors gracefully** with appropriate user feedback
- **Add comments** for complex logic

## 🧪 Testing Guidelines

### Writing Tests

1. **Test both success and failure scenarios**
2. **Mock external dependencies** (network, file system)
3. **Use descriptive test names** that explain what is being tested
4. **Follow the existing test structure** in `src/tests/`

### Test Categories

- **Unit Tests**: Test individual functions in isolation
- **Integration Tests**: Test function interactions and workflows
- **Error Tests**: Test error handling and edge cases
- **System Tests**: Test with real external dependencies (optional)

### Running Tests

**Windows:**
```cmd
# Run all tests
python src/tests/run_tests.py

# Run specific categories
python src/tests/run_tests.py --type install-unit
python src/tests/run_tests.py --type start-integration

# Run with internet tests (requires internet connection)
set TEST_WITH_INTERNET=1 && python src/tests/run_tests.py --type install-system
```

**Linux/macOS:**
```bash
# Run all tests
python3 src/tests/run_tests.py

# Run specific categories
python3 src/tests/run_tests.py --type install-unit
python3 src/tests/run_tests.py --type start-integration

# Run with internet tests (requires internet connection)
TEST_WITH_INTERNET=1 python3 src/tests/run_tests.py --type install-system
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Operating system** and version
2. **Python version**
3. **Steps to reproduce** the issue
4. **Expected behavior** vs actual behavior
5. **Error messages** or logs
6. **Environment details** (if relevant)
7. **Method used** (batch file or Python script)

## 💡 Feature Requests

When suggesting features:

1. **Describe the problem** you're trying to solve
2. **Explain why** this feature would be useful
3. **Provide examples** of how it would work
4. **Consider the impact** on existing functionality

## 🔄 Pull Request Process

1. **Ensure all tests pass** before submitting
2. **Update documentation** if needed
3. **Add tests** for new functionality
4. **Follow the commit message format** above
5. **Provide a clear description** of your changes
6. **Reference any related issues**

### PR Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Test addition/update
- [ ] Other (please describe)

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated if needed
- [ ] No breaking changes introduced
```

## 📚 Documentation

When updating documentation:

1. **Keep it clear and concise**
2. **Include examples** where helpful
3. **Update both README.md and TEST_README.md** if relevant
4. **Use consistent formatting** and emojis
5. **Include platform-specific instructions** (Windows vs Linux/macOS)

## 🌐 Platform-Specific Contributions

### Linux/macOS Support

We welcome contributions for Linux and macOS support:

1. **Shell Scripts**: Create tested shell scripts for Linux/macOS
2. **Testing**: Provide testing on actual Linux/macOS systems
3. **Documentation**: Update platform-specific instructions
4. **Bug Reports**: Report and fix platform-specific issues

### Windows Focus

The project currently has a Windows focus with:
- Batch file launchers
- PowerShell integration
- Windows-specific error handling

Contributions that improve Windows experience are highly valued.

## 🤝 Code Review

All contributions require review before merging. Reviewers will check:

- **Code quality** and adherence to standards
- **Test coverage** and quality
- **Documentation** updates
- **Potential security issues**
- **Performance implications**

## 📄 License

By contributing to SwarmTunnel, you agree that your contributions will be licensed under the MIT License.

## 🆘 Getting Help

If you need help with contributing:

1. **Check existing issues** for similar questions
2. **Review the documentation** in README.md and TEST_README.md
3. **Open a new issue** with the "question" label
4. **Join discussions** in existing issues

Thank you for contributing to SwarmTunnel! 🎉
