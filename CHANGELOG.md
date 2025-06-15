# Changelog

All notable changes to TERRASCAN will be documented in this file.

## [3.1.1] - 2025-06-15

### Improved
- **Complete SQLite removal**: Cleaned all remaining SQLite references from documentation and codebase
- **PostgreSQL-only development**: Updated DEVELOPMENT.md to focus exclusively on PostgreSQL setup
- **Simplified database module**: Removed production/development flags and error messages  
- **Enhanced system page**: Added version display and improved database information formatting
- **Better error handling**: Fixed duration display bug in system task logs (null safety)

### Changed
- **DEVELOPMENT.md**: Streamlined PostgreSQL setup guide, removed SQLite quick start section
- **Database error messages**: Clearer PostgreSQL requirement messaging with setup guidance
- **Function rename**: `get_db_path()` → `get_database_info()` for better clarity
- **System template**: Simplified database display to show "PostgreSQL" uniformly

### Technical Cleanup
- **Removed 30+ lines** of SQLite-related documentation and dual-database setup complexity
- **Standardized database info**: Consistent PostgreSQL connection information display
- **Fixed template bugs**: Null-safe duration formatting in task execution logs

## [3.1.0] - 2025-06-14

### 🚀 MAJOR DATA EFFICIENCY UPGRADE - Smart Deduplication System

### Added
- **Intelligent deduplication**: PostgreSQL UPSERT prevents duplicate environmental data
- **Incremental data fetching**: Only fetches new data since last collection
- **Batch processing**: High-performance bulk data storage with transaction safety
- **Automatic duplicate cleanup**: Migration script removes existing duplicates
- **Smart fire timestamps**: NASA FIRMS now uses actual fire detection times (not fetch time)
- **Database constraints**: Composite unique keys prevent duplicate storage
- **Coverage statistics**: Data efficiency reporting and duplicate detection

### Changed
- **NASA FIRMS fetcher**: Fixed major bug using actual fire timestamps instead of current time
- **Database schema**: Added unique constraints on (provider, metric, timestamp, location)
- **Storage efficiency**: 5-10x reduction in duplicate data storage
- **Query performance**: Faster queries with deduplicated dataset
- **Data integrity**: UPSERT updates existing records instead of creating duplicates

### Technical Improvements
- **database/add_deduplication.py**: Complete migration system with duplicate analysis
- **Enhanced store_metric_data()**: UPSERT with conflict resolution 
- **New functions**: `get_latest_timestamp()`, `batch_store_metric_data()`, `get_data_coverage_stats()`
- **Railway deployment**: Automatic deduplication migration on deploy
- **Fallback compatibility**: Graceful handling during migration transition

### Performance Impact
- **Storage reduction**: Up to 90% reduction in duplicate environmental records
- **Faster queries**: Elimination of redundant data improves query performance  
- **Cost efficiency**: Reduced database storage costs on Railway
- **API efficiency**: Fetchers skip re-downloading existing data

## [3.0.1] - 2025-06-14

### Improved
- **Enhanced datetime formatting**: Centralized ISO 8601 compliant system with timezone display
- **PostgreSQL compatibility**: Fixed datetime subscriptable errors in task templates
- **Ultra-aggressive cache busting**: Railway deployment cache clearing with multiple strategies  
- **Consolidated CSS architecture**: Merged tasks.css into style.css for cleaner codebase
- **Streamlined UI**: Removed verbose admin notices and redundant text for professional interface
- **Better accessibility**: Removed all text-muted classes (16 instances) for improved readability

### Added
- **utils/datetime_utils.py**: Centralized datetime formatting with template filters
- **Template filters**: `format_dt`, `time_ago`, `format_iso` for consistent datetime display
- **Enhanced cache headers**: CDN and proxy cache busting for Railway deployments
- **Version consolidation**: Moved version.py into utils package for better organization

### Fixed
- **PostgreSQL datetime errors**: Tasks page template datetime formatting issues resolved
- **Template cache disabled**: Flask template caching disabled for production consistency
- **Railway cache issues**: Build and nixpacks cache disabling for fresh deployments

### Removed  
- **Redundant admin notices**: Cleaned verbose task control explanations
- **text-muted classes**: Enhanced contrast and accessibility across all templates
- **Duplicate CSS files**: Consolidated styling into single style.css file

## [3.0.0] - 2025-06-14

### 🚀 MAJOR ARCHITECTURAL CHANGE - Python/PostgreSQL Platform

**BREAKING CHANGE**: TERRASCAN now requires PostgreSQL (DATABASE_URL environment variable)

### Removed
- **Complete SQLite support** - no more dual database complexity
- **500+ lines of dual database code** across multiple modules  
- **All IS_PRODUCTION conditionals** (47 instances removed)
- **SQLite imports and dependencies** throughout codebase
- **Local development SQLite database** support

### Changed
- **Database module**: Complete rewrite - 509 → 200 lines (60% reduction)
- **Web application**: Standardized to PostgreSQL SQL syntax
- **Config manager**: Simplified to PostgreSQL queries  
- **All SQL queries**: Converted to %s parameters (PostgreSQL standard)
- **Architecture**: Now pure Python + PostgreSQL production stack

### Improved
- **Massive code simplification** - single source of truth for database logic
- **Eliminates parameter format confusion** (no more ? vs %s issues)
- **Faster development** without dual database testing complexity
- **Production-ready cloud-native architecture**
- **No more database compatibility bugs**
- **Clean, positive language** throughout codebase and documentation
- **Professional documentation** without legacy reference clutter

### Migration Guide
- **Local development** now requires PostgreSQL or Railway dev database
- **Environment variable** DATABASE_URL is now required
- **No backward compatibility** with SQLite databases

## [2.5.3] - 2025-06-14

### Removed
- "Force Ocean Refresh" debug button from Ocean Health card  
- Nuclear cache-busting JavaScript function and excessive console logging
- Debug styling and visual clutter from troubleshooting session

### Improved
- Clean, professional UI without debugging elements
- Reduced JavaScript bundle size by removing debug code

## [2.5.2] - 2025-06-14

### Removed
- Degraded system status warning banner from yesterday's launch issues
- Broken API configuration check functionality from system page

### Fixed
- Broken API endpoint `/api/run_task/<name>` → `/api/tasks/<name>/run`
- Broken API endpoint `/api/task_source/<name>` → `/api/tasks/<name>/logs`
- Broken API endpoint `/api/railway/refresh` → `/api/refresh`  
- Broken API endpoint `/operational` → `/api/health`
- Duplicate dashboard link now points to home page

### Changed
- Converted Railway configuration from TOML to JSON format
- Added JSON schema reference for better validation
- All navigation links and API endpoints now working properly

## [2.5.1] - 2025-06-14

### Fixed
- PostgreSQL GROUP BY SQL errors in map data queries
- Changed `metadata` to `MAX(metadata)` in air quality and ocean data aggregation
- Resolves production database errors preventing map visualization

## [2.5.0] - 2025-06-14

### Added
- Complete task management web interface at `/tasks` route
- Real-time task monitoring with auto-refresh
- Manual task execution and bulk operations
- Task execution logs with stdout/stderr viewing
- Comprehensive PostgreSQL/Railway deployment documentation
- Local development setup guide (DEVELOPMENT.md)
- Dual SQLite/PostgreSQL database support

### Changed
- Moved CSS/JS from inline to external files (tasks.css, tasks.js)
- Added Tasks link to main navigation
- Updated README with production deployment guide
- Removed unused sqlite3 imports from task files

### Removed
- Redundant RAILWAY_DEPLOYMENT.md file

## [2.4.0] - 2025-06-14

### Added
- GBIF API integration for biodiversity data
- 18 global biodiversity hotspots monitoring
- Species observations and diversity metrics
- Ecosystem health indicators

## [2.3.0] - 2025-06-14

### Added
- OpenWeatherMap API integration
- Real-time weather data for 24 major cities
- Weather alerts and atmospheric monitoring
- Automated weather collection every 2 hours

## [2.2.3] - 2025-06-14

### Removed
- Debug endpoints and UI elements from system page
- Ocean debug functionality and cache debug tools
- 421 lines of debug-specific code

## [2.2.2] - 2025-06-14

### Fixed
- Map coordinate field name errors (latitude/longitude → lat/lng)
- Air quality field names (value → pm25)
- Header time update janking issues
- Coordinate validation for undefined values

## [2.2.1] - 2025-06-14

### Fixed
- Flask app import errors and template data structure
- Production deployment stability issues
- Template rendering for environmental data display

## [2.2.0] - 2025-06-14

### Removed
- All simulation/mock data functionality
- 500+ lines of simulation code
- Complex fallback logic and simulation_mode settings

### Changed
- System now requires real API keys or fails gracefully
- Simplified configuration and faster startup

## [2.1.3] - 2025-06-13

### Added
- System status page with provider monitoring
- Advanced debugging tools for production
- Cache-busting solutions for browser issues

### Fixed
- Ocean temperature caching issues showing 0°C
- Persistent "Loading..." text states
- Data freshness display problems

## [2.1.2] - 2025-06-13

### Fixed
- Ocean temperature 0°C display bug
- Time display "Loading..." stuck states
- Added proper water temperature data collection
- Fixed duplicate HTML ID conflicts

## [2.1.1] - 2025-06-13

### Added
- Expanded from 6 to 65+ cities worldwide
- Global coverage across all continents
- 200 air quality monitoring stations

## [2.1.0] - 2025-06-13

### Added
- Homepage with hero map
- Full-screen map view at `/map` route
- About page with mission statement
- Modular template system with base.html
- Professional navigation with active states

## [2.0.0] - 2025-06-13

### Changed
- Complete transformation to focused environmental dashboard
- Replaced 7-page interface with single dashboard
- Real-time focus instead of historical analysis
- Added environmental health scoring (0-100)
- Simplified from 697 to ~350 lines of Flask code

## [1.1.6] - 2025-06-10
### Removed
- Deployment activity section from operational page
- Related API endpoints and JavaScript functions

## [1.1.5] - 2025-06-10
### Removed
- Traffic analytics section and related mock data
- Unused GraphQL queries and JavaScript functions

## [1.1.4] - 2025-06-10
### Changed
- Consolidated inline CSS to external style.css file
- Improved maintainability and caching

## [1.1.3] - 2025-06-10
### Fixed
- Railway cost calculation discrepancy
- Jinja2 template syntax errors
- Added Railway Hobby plan billing logic

## [1.1.2] - 2025-06-10
### Added
- Railway operational costs monitoring
- Real-time resource usage tracking
- Budget alerts and GraphQL API integration

## [1.1.1] - 2025-06-09
### Fixed
- Updated documentation from 2024 to 2025
- Corrected GitHub repository URLs

## [1.1.0] - 2025-06-09
### Changed
- Renamed database columns: created_at/updated_at → created_date/updated_date

## [1.0.0] - 2025-06-09
### Added
- Initial Python + SQLite architecture
- NASA FIRMS, NOAA Ocean Service, OpenAQ integration
- 7-page web interface with task management
- Professional scheduling and error handling
- Bootstrap responsive design
- MIT License 
