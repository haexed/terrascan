# Changelog

All notable changes to Terrascan will be documented in this file.

## [3.7.2] - 2026-09-19

### Removed
- `/system`: "Clear Old Data" button.

### Fixed
- Main page had a horizontal and a vertical scrollbar with nothing to scroll to: `map.html` blanked `{% block footer_container %}`, so the footer `.row`'s `-12px` gutter margins had no container padding to cancel them and overhung the viewport by 12px. Restored the `container-fluid` wrapper.

## [3.7.1] - 2026-09-19

### Changed
- `/tasks`: "Running" badge dropped from the Status column, the Result column already shows it.

## [3.7.0] - 2026-09-19

### Added
- Provider metadata (name, icon, URL, coverage, tasks, freshness) as one JSON row per provider in `provider_config`, seeded by `setup_providers.py`, read through `database/providers.py`.
- `/api/providers`.
- `/system`: "Unrecognized Providers" card, listing `provider_key`s in `metric_data` with no metadata.
- `fix_task_commands.py`: reports `task.command` values whose module doesn't import. Repair is opt-in, not run.

### Changed
- `/system`: 6 provider cards → one table of all 8. "Active Data Sources" counts operational providers instead of a hardcoded 6.
- `/system`: removed the "Recent Task Executions" table.
- Footer, `/about`, `/status`, `/dashboard` and `/map` labels read provider names/URLs/icons from the metadata. Footer listed 5, `/system` 6, `/about` 8, `/dashboard` 3; all now list 8.
- `/api/refresh` and `/api/collect-all-data` take their task list from provider metadata.

### Fixed
- `fa-spin` was frozen under `prefers-reduced-motion: reduce` — Font Awesome 7 sets `animation: none !important` on it. Now turns at 3s.
- `/api/smart-refresh` counted failed task runs as refreshed ones. Failures report under `failed`.
- `/api/smart-refresh` mapped gbif to `gbif_biodiversity` and openweather to `openweather_global`; neither task exists.

## [3.6.23] - 2026-09-19

### Added
- `/tasks`: one table replaces the "All Tasks" cards and the "Recent Task Runs" list. One row per task, with status/schedule/last-run/result columns and a View Logs button.
- `TaskRunner.run_task()` blocks a task from starting if it's already running.

### Fixed
- `checkTaskStatus()` in `tasks.js` read `data.status.running_tasks`, the API returns `data.running_tasks` at the top level. Threw a TypeError on every 30s poll.
- `/api/collect-biodiversity` and `/api/tasks/<name>/run` always returned a hardcoded "completed" message regardless of success/failure, never surfaced `result['error']`.

## [3.6.22] - 2026-09-19

### Changed
- "No stale tasks found" toast reworded to "No tasks running longer than 30 minutes". Dropped the ✨.

## [3.6.21] - 2026-09-19

### Fixed
- `.toast-notification` overlapped the "Cleanup Stale"/"Refresh Status" buttons on `/tasks`. Moved from top-right to bottom-right.

## [3.6.20] - 2026-09-19

### Fixed
- Replaced 7 blocking `alert()` popups on `/system` and `/system/schema` with the existing toast notification. Moved `showNotification()` into `base.html`, removed the duplicate from `tasks.js`.

### Added
- `?v={{ version }}` cache-busting query param on all local CSS/JS includes.

## [3.6.19] - 2026-09-19

### Fixed
- `.btn` anchors inside `.eco-card` showed an underline (Explore Map, System Status, Learn More, View Task Logs, View on GitHub). Restored `:not(.btn)` on `.eco-card a`.

### Reverted
- `/system` recent-runs duration: always a number + "s" again. (Logged as 3.6.18; no commit carried that version.)

## [3.6.17] - 2026-09-19

### Changed
- Anchor decoration: solid green underline everywhere.
- Removed `--infp-brown`.
- Footer link underline follows the link's own color instead of a fixed color.

## [3.6.16] - 2026-09-19

### Removed
- `.task-running .status-badge` and `.stat-item.scan-status` pulse animations. Both `@keyframes pulse` definitions.

## [3.6.15] - 2026-09-19

### Removed
- `.pulse` CSS class and its two badge usages.

## [3.6.14] - 2026-09-19

### Reverted
- 3.6.12's axe-core color/markup changes. Navbar/footer/status colors, badge colors, `.eco-card a`/`a.btn`, `<main>`/`<footer>` landmarks, `<h1>` promotions all back to prior state. Kept the 3.6.13 map panel redesign.

### Fixed
- Navbar "Terrascan" brand pinned to white, no underline, on `.logo`.

## [3.6.13] - 2026-09-19

### Changed
- `/map` control panel: Planetary Health merged into the top of the layer-toggle panel. "Live Environmental Layers" is the collapsible header. Removed the duplicate "🌍 Terrascan" header.
- Health breakdown panel repositioned to the left panel.

## [3.6.12] - 2026-09-19

### Fixed
- Ran axe-core against all 6 pages, fixed every violation. Reverted in 3.6.14.

## [3.6.11] - 2026-09-19

### Fixed
- Task card titles and Task Logs modal title: pinned color with `!important`.
- `/tasks` "Total Tasks" stat: fixed white-on-white.
- Status badges de-screamed: `.upper()` → title case across `/system` and `/system/schema` (OPERATIONAL, NO_DATA, RUNNING, YES/NO, etc.)
- `/system` recent-runs table showed "0.0s" for a still-running task — `duration_seconds` is NULL until completion, now shows "Running…"

## [3.6.10] - 2026-09-19

### Fixed
- `/system`'s Open-Meteo card showed 0 records (wrong hardcoded key `openmeteo` vs real `openmeteo_marine`) while the breakdown table below it showed the real count
- Aurora freshness badge used the wrong key (`noaa_aurora` vs real `noaa_swpc`), silently falling back to a 24h threshold instead of 1h
- Audited every real `provider_key` against every hardcoded provider list in the app

## [3.6.9] - 2026-09-19

### Fixed
- Heading hierarchy skips (h1→h3→h5, h2→h4/h5) on `/tasks`, `/system`, `/about` — all four audited pages now validate with 0 W3C errors

### Changed
- Stripped all HTML comments from templates

### Chore
- Tagged `3.6.8` (was committed but never tagged); dropped the stray `v3.7.0` tag locally and on GitHub

## [3.6.8] - 2026-09-19

### Fixed
- Heading-color specificity bug: `<h1 class="h2">`-style headings (Bootstrap's `.h1`-`.h6` beats our plain `h1`-`h6` rule) rendered dark green on the green background instead of white, site-wide
- "Task Logs" modal title was white-on-white
- `/map` banner stats used Jinja truthiness, so a real `0` count rendered as `—` same as missing data
- Invalid HTML from the W3C checker: `<div>` in `<label>` on `/map`, redundant `<meta http-equiv>` cache tags

### Changed
- Removed hover animations from `.eco-card`, `.hero-map-container`, `.task-card`
- "NO DATA" / "SYSTEM STATUS & DATA PROVIDERS" / "DATABASE SCHEMA DOCUMENTATION" → sentence case
- `.data-source` color: brown → sage green

## [3.6.7] - 2026-09-19

### Changed
- Upgraded Python deps: Flask 3.1.3, gunicorn 26.2.0, psycopg2-binary 2.9.13, others (now effectively requires Python ≥3.10)
- Bumped CDN libs: Bootstrap 5.3.8, Font Awesome 7.3.1
- Renamed `SECRET_KEY` env var to `FLASK_SECRET_KEY`
- Rewrote `.env.example` to only the vars the code actually reads
- Consolidated `DEVELOPMENT.md` into `README.md`; removed stale `SCAN_ARCHITECTURE.md`
- Fixed README inaccuracies: NASA FIRMS/World AQI rate limits, GBIF/NOAA Aurora freshness TTLs, removed nonexistent `/api/dashboard-data` from the API reference table

### Fixed
- Local dev was silently broken: `.env` had no secret-key var at all, so `python run.py` always crashed on startup despite production (Railway) working fine
- Rebuilt local `.venv` (was built against Python 3.13, which no longer exists on this machine)

## [3.6.6] - 2026-04-06

### Added
- **UCDP API token auth**: `fetch_ucdp_conflicts.py` now sends `x-ucdp-access-token` header from `UCDP_API_TOKEN` env var (UCDP moved to authenticated access, 5,000 req/day limit)
- **UCDP candidate dataset**: switched endpoint from stable `gedevents/25.1` (annual, lags ~1 year) to monthly candidate release `gedevents/26.0.2`. The stable dataset had no events newer than 2024 so the task was silently returning 0 records; candidate has 1000+ events from 2026 alone. See https://ucdp.uu.se/apidocs/ for current version string.
- `database/cleanup_indexes_and_data.py`: maintenance script for index cleanup, batched data retention enforcement, task_log pruning, and VACUUM ANALYZE
- `database/dump_backup.py`: portable Python-based full DB backup (schema + data) to stdout, no `pg_dump` required
- `?hero=true` parameter on `/api/map-data` returning a lightweight payload (50 fires, 50 air, 30 ocean — no conflicts/biodiversity/aurora) for the homepage hero map

### Changed
- **Map API performance**: bbox filtering now applied to all six query layers (previously conflicts, biodiversity, aurora, ocean ignored bbox)
- Air quality query window tightened from 7 days → 3 days; global limit reduced from 1000 → 500 (bbox 5000 → 2000)
- Hero map JS now requests the hero endpoint and renders backend results directly (eliminated client-side over-fetch + slice of 4100+ markers down to ~130)
- UCDP exempted from the 30-day data retention sweep (it stores historical event dates, not collection timestamps)
- Cleanup script uses autocommit batched DELETEs (50k rows/batch) to avoid long locks

### Fixed
- **Map layout**: map no longer renders behind the navbar
- **noaa_aurora task**: use `execute_insert` for DELETE so the statement actually commits
- **Cache invalidation**: now triggered after all data-modifying operations (was missing in several paths)
- **Status page — hero map removed**: redundant embedded map removed from `/status` (use `/map` for full view); dropped Leaflet deps from that page
- **Status page — ocean health "NO DATA"**: query now reads both `water_temperature` and `water_level` from `noaa_ocean`; UI shows whichever is available with a dynamic label, falls back gracefully
- **Decimal display**: `format_nullable_value()` now converts `Decimal` → `float` so PM2.5 etc. round properly (no more `6.1566568914956012`)
- **API type coercion**: fire/air/ocean formatters explicitly cast lat/lng/values to `float`/`int` before serialization, fixing `fire.lat.toFixed is not a function` in the frontend
- **JS validation**: added `validateFireData` / `validateAirData` / `validateOceanData` at the API boundary in `web/static/js/map.js`, plus JSDoc typedefs and null-safe display

### Removed
- **Version drift cleanup**: dropped the stale `system_config['version']` row (was `2.5.0`/`2.7.0` depending on which `setup_*` script ran last) and removed version-seeding from `setup_configs.py` and `setup_production_railway.py`. `utils.VERSION` is now the single source of truth — `run.py` startup banner, templates, and `/system` page all read from it.

### Infrastructure
- **Massive DB shrink**: deleted ~3M stale rows from `metric_data` (5.6M → 19k); volume dropped from ~6GB → ~3GB visible on Railway metrics on 2026-04-01
- Removed 7 redundant indexes covered by the unique constraint and composite indexes; ~2.6GB → ~1.3GB index footprint
- VACUUM ANALYZE reclaimed disk after batch deletions

## [3.6.5] - 2026-01-23

### Added
- **Lazy TTL Refresh**: Auto-detects stale data and shows refresh banner
- **Timestamp-based cache invalidation**: Cache auto-expires when new data arrives
- Stale data banner with one-click refresh button

### Changed
- Removed hamburger menu - nav always visible (icons stack on mobile)
- Optimized `get_tasks_with_last_run()` using `DISTINCT ON` (was 4 correlated subqueries)
- Cached expensive `/system` queries (provider_stats, data_breakdown)

### Removed
- Orphaned cron schedules (tasks are now on-demand only)
- Deleted `test_task_123` leftover from testing
- Removed unused task scheduling infrastructure

### Fixed
- Navbar responsive: icons above text at medium, icons only at small
- Query timing instrumentation for debugging slow pages

### Documentation
- Updated README: tasks are on-demand, not cron-scheduled
- Documented freshness TTL thresholds per data source

## [3.6.4] - 2026-01-23

### Changed
- Switched to gunicorn (1 worker, 2 threads) from Flask dev server
- Reduced DB connection pool from 20 to 3
- Added worker recycling (max-requests 500) to prevent memory leaks

### Infrastructure
- Added `railway.toml` with resource limits (0.5 vCPU, 512MB web)
- Enabled serverless mode (scale to zero when idle)
- Postgres resource limits: 0.5 vCPU, 1GB RAM
- Added `wsgi.py` entry point for gunicorn

### Notes
- Target: fit within Railway $5 hobby tier
- Serverless = near-zero cost during idle periods
- 2GB database with 2.2M rows works well with 1GB Postgres RAM

## [3.6.3] - 2025-12-31

### Added
- Database performance indexes migration script
  - `idx_metric_provider` - provider_key filtering
  - `idx_metric_timestamp` - timestamp ordering
  - `idx_metric_provider_metric` - composite for common WHERE patterns
  - `idx_metric_provider_timestamp` - viewport queries
  - `idx_task_log_task_started` - task log queries
  - `idx_metric_location` - spatial queries
- Google Analytics tracking (G-BVDKV5QWQ1)
- Beta badge on logo to indicate work-in-progress
- Logo assets for social media (logo-emoji.png, logo.svg)
- @Terrascan_io X/Twitter account

### Changed
- Provider stats query consolidated from 9 DB calls to 1 (GROUP BY)
- Task query extracted to reusable `get_tasks_with_last_run()` function
- UCDP conflicts filter extended from 365 to 730 days
- SECRET_KEY now required (no insecure fallback)
- Refresh/scan buttons moved to bottom-right corner

### Fixed
- Bare `except: pass` replaced with specific exceptions
- Removed duplicate `refreshRailwayData()` function
- Removed unused `get_db_connection` import
- Replaced deprecated `.substr()` with `.substring()`
- Removed duplicate return statement in add_deduplication.py
- Moved late imports (json, traceback, Decimal) to module top

## [3.6.2] - 2025-12-30

### Reverted
- Removed heatmap/clustering experiments (v3.7.0) - caused 5-10s load times
- Back to simple CircleMarkers which are faster and clearer

### Notes
- Heatmaps were too soft/blurry to show good vs bad data
- MarkerCluster library added significant overhead
- Simple colored circles communicate data quality better

## [3.6.1] - 2025-12-30

### Added
- **Viewport-based lazy loading** for map data
  - `/api/map-data` now accepts optional `bbox` parameter
  - Data reloads automatically when panning/zooming (debounced)
  - Higher limits when viewing specific regions (5000 AQ vs 1000 global)

### Fixed
- Scanned data now persists after page refresh (viewport-based query includes local data)
- Norway/rural areas no longer cut off by global station limit

## [3.6.0] - 2025-12-30

### Added
- **Data freshness visibility** across all views
  - Color-coded freshness badges (green/yellow/red) on dashboard cards
  - Per-source age indicators ("Updated 0.6h ago")
  - New `/api/freshness` endpoint with detailed source status
- **Health score breakdown panel** (clickable on map view)
  - Shows impact of each data source on total score
  - Displays freshness dots for each contributing source
  - Expandable/collapsible panel with animations
- **Smart refresh API** (`/api/smart-refresh`)
  - Only updates stale/aging data sources
  - Skips fresh sources to reduce API calls
  - Returns detailed refresh report

### Changed
- `/map` route now passes freshness data to template
- Health score calculation includes breakdown details
- Mobile-responsive breakdown panel (slides up from bottom)

## [3.5.1] - 2025-12-30

### Fixed
- Scan toast message now says "Loaded X stations" instead of misleading "Found new"
- AQ data query no longer deprioritizes good air quality locations
- Scanned data persists after page refresh (timestamp fix)
- Stale tasks cleanup endpoint and button on Tasks page

### Changed
- Scan threshold lowered to zoom level 8 (regional view)
- AQ station limit increased to 1000 for better coverage

## [3.5.0] - 2025-12-30

### Added
- **On-demand area scanning** - "Scan Area" button for discovering local data
  - Appears when zoomed to city level (zoom >= 10)
  - Fetches air quality stations from WAQI for visible map area
  - Toast notifications show scan results
  - New stations appear instantly on map with "Scanned just now" indicator
- New `/api/scan-area` endpoint for bbox-based data fetching

### Changed
- Scan button has pulsing animation while fetching data
- Mobile-responsive scan button and toast notifications

## [3.4.0] - 2025-12-29

### Added
- **Aurora forecast layer** from NOAA Space Weather Prediction Center
  - Real-time aurora probability using OVATION model
  - Kp geomagnetic index display (0-9 scale with status)
  - Green-to-purple color gradient based on intensity
  - Updates every 30 minutes
- **UCDP conflict data layer** from Uppsala Conflict Data Program
  - Global armed conflict events with fatality counts
  - Conflict metadata: sides, violence type, region
  - Historical data up to 365 days
- **Task creation API endpoint** (`POST /api/tasks/create`)
- NOAA SWPC and UCDP credits on About page

### Changed
- **Ocean temperature switched to Open-Meteo** for global SST coverage
  - Replaced US-only NOAA stations with 20 global monitoring points
  - Updated map labels and popup sources
- Removed redundant info-popup box (Leaflet popups sufficient)
- Cleaned up legend references from layer toggle handlers
- Map now has 6 toggleable layers: Fires, Air Quality, Ocean, Conflicts, Biodiversity, Aurora

### Fixed
- Task creation using wrong database function (`execute_query` → `execute_insert`)

## [3.3.0] - 2025-11-19

### Added
- Open-Meteo Marine API integration for global ocean data
  - Sea surface temperature, wave height, ocean currents
  - 20 global ocean monitoring points
  - CC-BY 4.0 attribution on About, Index, and System pages
- New API endpoints: `/api/tasks/status`, `/api/tasks/<name>/toggle`, `/api/collect-all-data`, `/api/collect-biodiversity`
- `.subheader` CSS class for light text on dark backgrounds
- Open-Meteo provider card on System page with stats

### Fixed
- **Critical**: Datetime comparison bug in `get_latest_timestamp()` - converted PostgreSQL datetime to ISO string
- **Critical**: WAQI global fetch returning 0 results - switched to map bounds API with world bbox
- **Critical**: Task logging not recording runs since September - `result[0]` → `result['id']` for RealDictCursor
- **Critical**: Task logs modal showing all entries as "Failed" - JavaScript checking non-existent `exit_code` instead of `status`
- Missing imports for `get_running_tasks`, `get_recent_task_runs`, `get_task_by_name` in app.py
- Missing template variables: `database_size`, `running_tasks`
- Hardcoded health score "30/POOR" → actual data or "NO DATA"
- Hardcoded fire confidence 75 → actual metadata value
- CSS contrast issues: `.eco-card a` white on white background → forest green
- Status colors for better readability: `.status-good` yellow → olive-green, `.status-moderate` → darker amber
- Navigation confusion: "View Dashboard" → "System Status" on index page
- System page quick action buttons not working

### Changed
- Ocean Health data source now credits "NOAA & Open-Meteo"
- Active Data Sources count: 5 → 6 environmental APIs
- Added `noaa_ocean_temperature` and `openmeteo_marine` to refresh tasks list

## [3.2.0] - 2025-09-05

### Added
- Production stabilization and Railway deployment improvements
- Enhanced error handling for API failures

### Fixed
- Various production bugs and stability issues

## [2.7.0] - 2025-06-16

### Fixed
- Task status display showing "Never run" for tasks that had executed
- Tasks page now shows proper last run timestamps, status, and duration
- API endpoint `/api/tasks` includes complete task execution history

### Improved
- Task monitoring with accurate execution status (Success/Failed/Running)
- Performance metrics display (duration, records processed)
- Real-time task status updates in web interface

## [3.1.2] - 2025-06-16

### Changed
- Rewrote web/app.py from 1,293 to 618 lines (52% reduction)
- Consolidated duplicate data preparation between routes
- Simplified cache busting with single decorator

### Removed
- Debug endpoints: /api/collect-biodiversity, /api/setup-production, /api/fix-tasks, /api/debug-task
- Redundant imports and duplicate code paths
- Ultra-aggressive cache headers throughout application

### Improved
- Clean Flask architecture with single-responsibility functions
- Consistent error handling across all endpoints
- Maintainable helper functions for data formatting

## [3.1.1] - 2025-06-15

### Removed
- All remaining SQLite references from documentation and codebase
- SQLite quick start section from DEVELOPMENT.md
- Production/development flags from database module

### Changed
- Function rename: get_db_path() → get_database_info()
- DEVELOPMENT.md to focus exclusively on PostgreSQL setup
- System template to show "PostgreSQL" uniformly

### Fixed
- Duration display bug in system task logs (null safety)
- Database error messages with clearer PostgreSQL guidance

## [3.1.0] - 2025-06-14

### Added
- PostgreSQL UPSERT prevents duplicate environmental data
- Incremental data fetching - only fetches new data since last collection
- Batch processing with transaction safety
- Automatic duplicate cleanup migration script
- Database constraints with composite unique keys
- New functions: get_latest_timestamp(), batch_store_metric_data(), get_data_coverage_stats()

### Changed
- NASA FIRMS fetcher to use actual fire detection times instead of current time
- Database schema with unique constraints on (provider, metric, timestamp, location)
- store_metric_data() enhanced with UPSERT and conflict resolution

### Fixed
- Major NASA FIRMS timestamp bug
- Data integrity with UPSERT updates instead of creating duplicates

### Improved
- 5-10x reduction in duplicate data storage
- Faster queries with deduplicated dataset
- Reduced database storage costs

## [3.0.1] - 2025-06-14

### Added
- utils/datetime_utils.py with centralized datetime formatting
- Template filters: format_dt, time_ago, format_iso
- Enhanced cache headers for Railway deployments

### Changed
- Merged tasks.css into style.css for cleaner codebase
- Moved version.py into utils package
- Centralized ISO 8601 compliant datetime system with timezone display

### Fixed
- PostgreSQL datetime errors in task templates
- Template cache disabled for production consistency
- Railway cache issues with build and nixpacks

### Removed
- Verbose admin notices and redundant text
- All text-muted classes (16 instances) for better readability
- Duplicate CSS files

## [3.0.0] - 2025-06-14

**BREAKING CHANGE**: Terrascan now requires PostgreSQL (DATABASE_URL environment variable)

### Removed
- Complete SQLite support and dual database complexity
- 500+ lines of dual database code across multiple modules
- All IS_PRODUCTION conditionals (47 instances)
- SQLite imports and dependencies throughout codebase
- Local development SQLite database support

### Changed
- Database module: complete rewrite 509 → 200 lines (60% reduction)
- Web application standardized to PostgreSQL SQL syntax
- Config manager simplified to PostgreSQL queries
- All SQL queries converted to %s parameters (PostgreSQL standard)
- Architecture: now pure Python + PostgreSQL stack

### Migration
- Local development now requires PostgreSQL or Railway dev database
- DATABASE_URL environment variable is now required
- No backward compatibility with SQLite databases

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
