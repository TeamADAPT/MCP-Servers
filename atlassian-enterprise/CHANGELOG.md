# Changelog

## [0.3.0] - 2025-05-21

### Added
- Implemented enterprise-grade features according to roadmap:
  - Added authentication and security module with OAuth 2.0 support
  - Implemented token refresh, rate limiting, and circuit breaker patterns
  - Added comprehensive audit logging for security events
  - Added analytics and insights module for cross-product analytics
  - Implemented time tracking analysis and issue pattern detection
  - Added custom report generation with Confluence publishing capabilities
  - Added AI-powered capabilities including smart issue classification
  - Implemented content suggestion, sentiment analysis, and SLA prediction
  - Added marketplace app integration for Tempo, Zephyr, and more
  - Created extensible app integration framework for future additions
- Added server integration for all enterprise features
- Added new MCP tools for enterprise features
- Added detailed documentation and usage examples in ENTERPRISE_FEATURES.md

### Changed
- Updated server infrastructure to support enterprise feature sets
- Refactored authentication handling for enhanced security
- Added new dependencies for machine learning and analytics components
- Updated version number to 0.3.0 to reflect major enterprise features addition

## [0.2.0] - 2025-05-07

### Added
- Implemented enhanced Confluence features according to roadmap
- Added `ConfluenceSpaceManager` for comprehensive space management:
  - Support for creating, archiving, and restoring spaces
  - Space permission management capabilities
  - Template-based space creation features
- Added `ConfluenceTemplateManager` for templates and blueprints:
  - Support for retrieving and using templates
  - Blueprint-based content creation features
  - Template management and customization
- Added `ConfluenceContentManager` for advanced content features:
  - Content properties management
  - Label and metadata management
  - Macro support in content creation and editing
  - Enhanced content version management
- Added comprehensive mock-based unit tests for all new classes
- Added server integration for enhanced Confluence features
- Updated existing Confluence API wrappers for compatibility

### Changed
- Refactored server infrastructure to support enhanced feature sets
- Improved documentation and code organization
- Enhanced error handling throughout Confluence integrations
- Updated version number to reflect major feature additions

## [0.1.9] - 2025-04-20

### Added
- Added robust handling for custom fields in Jira issue creation
- Added API methods for global custom field configuration
- Added caching mechanism to track field availability by project
- Added automatic retry for issue creation when custom fields fail
- Added comprehensive mock tests for custom fields functionality
- Added new MCP tools for custom field management

### Fixed
- Fixed issue where custom fields would fail in certain projects (e.g., ZSHOT)
- Fixed validation for required custom fields
- Fixed unnecessary prefix additions to issue titles
- Improved error handling and recovery for custom field errors

## [0.1.8] - 2025-02-16

### Added
- Added Docker support with multi-stage build
- Added Smithery configuration for deployment

### Fixed
- Fixed Jira date parsing for various timezone formats
- Fixed document types import error
- Updated logging configuration

## [0.1.7] - 2024-12-20

### Changed
- Optimized Confluence search performance by removing individual page fetching
- Updated search results format to use pre-generated excerpts

## [0.1.6] - 2025-12-19

### Changed
- Lowered minimum Python version requirement from 3.13 to 3.10 for broader compatibility

## [0.1.5] - 2024-12-19

### Fixed
- Aligned comment metadata keys in Confluence comments endpoint
- Fixed handling of nested structure in Confluence spaces response
- Updated README.md with improved documentation