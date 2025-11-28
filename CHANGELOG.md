# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Changes that are committed but not yet released go here

## [0.1.0] - 2025-11-28
### Added
- Initial release of data-governance-toolkit
- Unity Catalog comment synchronization functions:
  - `sync_table_comment`: Sync table-level comments between catalogs
  - `sync_schema_table_comments`: Sync all table comments in a schema
  - `sync_table_column_comments`: Sync column comments for a specific table
  - `sync_schema_column_comments`: Sync all column comments in a schema
- Data quality validation utilities:
  - `check_valid_date_range`: Validate start/end date relationships
  - `check_for_gaps`: Detect gaps in date range coverage
  - `check_for_no_overlaps`: Detect overlapping date ranges
  - `check_all_reference_in_master`: Validate referential integrity
- Example Jupyter notebook demonstrating Unity Catalog sync workflows
- Comprehensive README with installation and usage instructions

### Documentation
- MIT License
- Python 3.9+ support
- Built with `uv` package manager

---

## How to Use This Changelog

### Version Format
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
  - **MAJOR**: Breaking changes or major new features
  - **MINOR**: New features, backwards compatible
  - **PATCH**: Bug fixes, minor improvements

### Change Categories
Use these sections as appropriate:
- **Added**: New features or functionality
- **Changed**: Changes to existing functionality
- **Deprecated**: Features that will be removed in future versions
- **Removed**: Features that have been removed
- **Fixed**: Bug fixes
- **Security**: Security-related changes or fixes

### Example Entry
```markdown
## [0.2.0] - 2025-12-15
### Added
- Alation API integration for metadata sync
- Support for bulk operations with retry logic

### Fixed
- Bug where empty comments caused sync to fail
- Improved error handling for missing catalogs

### Changed
- Updated `sync_table_comment` to return detailed status dict
```

[Unreleased]: https://github.com/alexane-rose/data-governance-toolkit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/alexane-rose/data-governance-toolkit/releases/tag/v0.1.0