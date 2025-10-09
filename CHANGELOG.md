# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2025-10-09

### Fixed
- **Critical:** Changed default timestamp from local time to UTC to prevent timezone inconsistencies across distributed systems
- Added validation for negative timestamps (before Unix epoch 1970-01-01)
- Added validation for timestamps exceeding 48-bit limit (approximately year 10889)

### Added
- Type validation for `create()` function parameters with clear error messages
- Comprehensive test suite with 36 test cases and 97% code coverage
- Improved docstrings with detailed parameter descriptions, return values, and exceptions
- Better error messages showing version and variant information for invalid UUIDs

### Changed
- Updated documentation to reflect UTC-only behavior and new validation rules
- Added pytest and pytest-cov as optional test dependencies

## [1.1.0] - [Previous Release]

Initial production release with RFC 9562 compliant UUIDv7 implementation.

## [1.0.0] - [First Release]

First stable release.
