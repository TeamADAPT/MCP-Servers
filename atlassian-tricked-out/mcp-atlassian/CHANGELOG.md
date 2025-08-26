# Changelog

## [0.3.0] - 2025-05-18

### Added
- Implemented Enhanced Jira Integration (Phase 3, Group 1):
  - Added comprehensive feature flags system for conditional enablement
  - Enhanced Jira functionality with custom field management
  - Added caching system for performance improvements
  - Implemented bulk operations for issues and links
  - Added project health analysis and reporting
  - Added improved error handling with retry logic
  - Created tests for enhanced Jira functionality
  - Added documentation in docs/enhanced_jira_integration.md
  - Prepared staging directory with deployment scripts

## [0.2.1] - 2025-05-14

### Added
- Added core module integrations as part of Phase 2:
  - Added BitbucketConfig class to config.py
  - Added stub files for Bitbucket integration (bitbucket.py, bitbucket_integration.py, bitbucket_pipeline.py)
  - Added basic analytics.py module with project metrics and time tracking analysis
  - Updated documentation in docs/core_modules_update.md

### Fixed
- Fixed custom fields in Jira issue and epic creation:
  - Removed hardcoded values for customfield_10057 ("name") and customfield_10058 ("Dept")
  - Made name and dept parameters required in create_issue and create_epic methods
  - Added proper validation to ensure the required parameters are provided
  - Updated tool schemas to include the required parameters
  - Added test script to verify the changes
  - Added detailed documentation in docs/custom_fields_fix.md

## [0.2.0] - 2025-05-13

### Added
- Implemented enhanced Confluence features with feature flags
  - Space management (creation, permissions, archiving)
  - Template management (templates, blueprints)
  - Content management (properties, restrictions, labels, exports)
- Added feature dependency system for automatic enablement of dependent features
- Updated documentation with enhanced Confluence tools
- Added feature-specific testing for enhanced modules

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
