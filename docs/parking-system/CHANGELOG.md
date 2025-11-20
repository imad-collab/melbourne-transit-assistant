# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Feature X (in development)

### Changed
- Improvement Y

### Fixed
- Bug fix Z

## [0.1.0] - 2025-01-21

### Added
- Initial release
- WebSocket server for real-time parking updates
- Python WebSocket client
- HTML/JavaScript browser dashboard
- Data caching and filtering
- Support for Melbourne CBD parking data (3,309 spots)

### Features
- Real-time detection of parking status changes
- Bidirectional WebSocket communication
- Support for multiple concurrent clients
- Zone-based and status-based filtering
- Server status monitoring

### Known Issues
- Some parking sensor data is stale (>1 month old)
- Sensors fail silently without maintenance alerts
- Limited to Melbourne CBD only
