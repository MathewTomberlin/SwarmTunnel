# Changelog

All notable changes to SwarmTunnel will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-15

### Added
- Initial release of SwarmTunnel
- SwarmUI installation and configuration
- Cloudflare Quick Tunnel integration
- Windows batch file launchers
- Comprehensive test suite with 90+ tests
- Logging system with centralized log directory
- Environment variable support for customization
- CLI argument support for force flags
- Cross-platform Python script support (Windows, macOS, Linux)
- Process detachment for better user experience
- Comprehensive error handling and cleanup

### Changed
- Moved all log files to `logs/` directory
- Improved Windows permission handling
- Enhanced PowerShell integration
- Better process management and cleanup

### Fixed
- Timeout and duplicate message issues
- Terminal window closing behavior
- PowerShell command parsing errors
- Environment variable handling
- Process attachment issues

### Features
- **Installation**: SwarmUI and cloudflared installation
- **Tunneling**: Cloudflare Quick Tunnel for remote access
- **Cross-platform**: Windows (batch files + Python), Linux/macOS (Python only)
- **User-friendly**: Simple batch file launchers for Windows
- **Logging**: Basic logging and error tracking

---

## Version History

### Version 1.0.0
- **Release Date**: 2025-08-XX
- **Status**: Initial Release
- **Key Features**:
  - SwarmUI installation
  - Cloudflare Quick Tunnel integration
  - Cross-platform Python script support
  - Windows batch file launchers
  - Basic error handling
---

## Migration Guide

### From Pre-1.0 Versions
- No migration required - this is the initial release
- All features are new and backward compatible

### Future Versions
- Check this changelog for breaking changes
- Review README.md for updated usage instructions
- Test in a development environment before upgrading

---

## Contributing to the Changelog

When contributing to SwarmTunnel, please update this changelog:

1. **Add entries** under the appropriate version section
2. **Use the correct categories**: Added, Changed, Deprecated, Removed, Fixed, Security
3. **Be descriptive** but concise
4. **Include issue numbers** when relevant
5. **Follow the existing format**

### Changelog Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security-related changes

---

## Release Process

1. **Update version** in relevant files
2. **Update changelog** with new version
3. **Create release** on GitHub
4. **Tag release** with version number
5. **Update documentation** if needed
6. **Announce release** to community

---

## Support

For questions about specific versions or changes:

- **Check this changelog** for version details
- **Review README.md** for usage instructions
- **Open an issue** for questions or problems
- **Check existing issues** for similar questions
