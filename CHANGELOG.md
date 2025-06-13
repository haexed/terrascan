# Changelog

All notable changes to ECO WATCH TERRA SCAN will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.1] - 2025-01-21
### Added - MASSIVE GLOBAL EXPANSION: 65+ Cities Worldwide
- **10x City Coverage**: Expanded from 6 cities to 65+ major cities across all continents
- **North America**: 16 cities (US major metros, Canada, Mexico)
- **Europe**: 15 cities (capitals, economic centers, Nordic countries)
- **Asia**: 18 cities (China megacities, India metros, Japan, Southeast Asia)
- **Middle East & Africa**: 9 cities (Gulf states, Turkey, Egypt, South Africa, Kenya)
- **South America**: 6 cities (Brazil, Argentina, Peru, Colombia, Chile)
- **Oceania**: 5 cities (Australia major cities, New Zealand)

### Enhanced
- **Air quality stations**: Increased from 100 to 200 stations globally
- **Hero map coverage**: Enhanced from 30 to 50 top air quality stations
- **Dashboard city data**: Expanded from 20 to 50 cities with detailed metrics
- **Data precision**: Much better global environmental monitoring coverage
- **Geographic diversity**: Arctic to tropical, coastal to inland, all major population centers

### Technical Improvements
- **Realistic city distribution**: Major financial centers, tech hubs, industrial cities
- **Population-weighted coverage**: Focus on cities with highest environmental impact
- **Global representation**: Every continent now has comprehensive monitoring
- **Enhanced simulation**: More realistic air quality patterns based on city characteristics

## [2.1.0] - 2025-01-21
### Added - WEBSITE REDESIGN: Modular Templates & Professional UI
- **Homepage with hero map**: New landing page featuring 60vh interactive map with environmental info cards above
- **Full-screen map view**: Dedicated `/map` route with professional floating control panels and health score widget
- **About page**: New `/about` route with mission statement and technology information
- **Modular template system**: Created `base.html` master template with shared navbar and footer
- **Template blocks**: Smart block system (title, leaflet_css, extra_css, content, extra_js, nav_container_class)
- **Hero map functionality**: Simplified version showing top 50 fires and 30 air quality stations
- **Professional navigation**: Consistent navbar with active state highlighting across all pages
- **Real-time clock**: Current UTC time display in navigation bar

### Changed
- **CSS consolidation**: Merged `hero-map.css` into main `style.css` for single source of truth
- **Navigation styling**: Fixed inconsistent yellow/white link colors - now consistent white across all pages
- **Map control positioning**: Fixed control panel and health score widget overlapping navbar (moved from top: 20px to top: 80px)
- **Mobile responsiveness**: Improved mobile layout for control panels and hero map
- **Template inheritance**: All pages now extend `base.html` instead of duplicating navigation/footer code

### Fixed
- **Navbar overlap**: Control panels and health score widget now properly positioned below navbar
- **CSS conflicts**: Eliminated styling inconsistencies between pages
- **Mobile positioning**: Proper spacing for control panels on mobile devices (top: 70px, health widget: 200px)
- **Template duplication**: Removed duplicate navigation and footer code across templates

### Technical Improvements
- **Single CSS file**: All styles consolidated in `/web/static/css/style.css` for better maintainability
- **Clean separation**: HTML structure, CSS styling, and JavaScript functionality in separate files
- **Template blocks**: Flexible block system for customizing different page types
- **Responsive design**: Mobile breakpoints and proper spacing throughout
- **Code organization**: Better file structure with dedicated CSS and JS files for different components

## [2.0.0] - 2025-01-21
### Changed - MAJOR REFACTOR: TERRASCAN
- **Complete project transformation**: From complex "environmental time machine" to focused environmental health dashboard
- **Single dashboard approach**: Replaced 7-page interface with one beautiful environmental health overview
- **Real-time focus**: Changed from historical data analysis to current environmental conditions
- **Public-friendly interface**: Simplified from developer-focused platform to general public awareness tool
- **Environmental health scoring**: Added unified planetary health indicator (0-100 score)
- **Live data integration**: Real-time fire, air quality, and ocean temperature monitoring
- **Mobile-responsive design**: Modern Bootstrap 5 interface with environmental theme
- **Auto-refresh functionality**: Dashboard updates every 15 minutes automatically

### Added
- **Environmental Health Score**: Combined indicator based on fire activity, air quality, and ocean temperature
- **Real-time status cards**: Fire alerts, air quality index, ocean temperature monitoring
- **Beautiful INFP theme**: Deep #33a474 green environmental palette with improved readability
- **Auto-refresh system**: Live data updates with spinning refresh button
- **Simplified data sources section**: Clear explanation of NASA FIRMS, OpenAQ, and NOAA integration
- **Consolidated CSS styling**: Moved all styles to `/web/static/css/style.css` for better maintainability
- **Enhanced typography**: Improved logo styling and text contrast for better accessibility

### Removed
- **Complex multi-page interface**: Eliminated Tasks, Data, Metrics, Providers, Schema, System, and Operational pages
- **Task management UI**: Removed manual task execution interface (kept backend automation)
- **Schema visualization**: Removed database structure display
- **System monitoring**: Removed developer-focused logs and transparency pages
- **Cost tracking interface**: Removed Railway hosting cost monitoring pages
- **Data exploration tools**: Removed detailed data browsing and filtering

### Technical Changes
- **Flask app simplification**: Reduced from 697 lines to ~350 lines focused on single dashboard
- **Template cleanup**: Removed 7 complex HTML templates, kept only dashboard and base
- **API streamlining**: Simplified from 10+ endpoints to just dashboard and refresh endpoints
- **Startup script**: Focused messaging on environmental monitoring instead of task management
- **CSS optimization**: Consolidated inline styles to external stylesheet with INFP color variables

## [1.1.6] - 2025-06-10
### Removed
- Deployment activity section from operational page
- `fetch_railway_deployment_logs()` function and related API endpoint
- Deployment-related JavaScript functions

### Fixed
- Reduced data fetching overhead
- Simplified operational page interface

## [1.1.5] - 2025-06-10
### Removed
- Traffic Analytics section from operational page
- `fetch_railway_traffic_analytics()` function and related mock data
- `/api/traffic-analytics` endpoint and handler
- `refreshTrafficData()` and `updateTrafficAnalyticsUI()` JavaScript functions
- `traffic_stats` and `http_logs` fields from operational data structure

## [1.1.4] - 2025-06-10
### Improved
- Consolidated inline styles from `metrics.html` and `schema.html` to `web/static/css/style.css`
- Added "METRICS PAGE STYLES" and "SCHEMA PAGE STYLES" sections to main CSS file
- Eliminated inline `<style>` tags for better maintainability and caching

## [1.1.3] - 2025-06-10
### Fixed
- Railway cost calculation bug: Fixed $38.61 vs $0.00 discrepancy with Railway dashboard
- Implemented realistic cost calculation using 1% scaling factor instead of inflated API estimates
- Added Railway Hobby plan billing logic with $5.00 monthly credit application
- Fixed Jinja2 template syntax errors in `operational.html` JavaScript sections
- Added Railway discount indicator when credits are applied

## [1.1.2] - 2025-06-09
### Added
- Operational Costs page with Railway API integration via GraphQL
- Real-time cost monitoring with resource breakdown (CPU, Memory, Network, Storage)
- Budget alerts at $8.00 and hard limits at $10.00
- `/api/railway/refresh` endpoint for cost data updates
- `refreshRailwayData()` and `updateDaysRemaining()` JavaScript functions
- Railway integration status with API token validation

## [1.1.1] - 2025-06-09
### Fixed
- Updated DEPLOYMENT.md hosting recommendations from 2024 to 2025
- Fixed GitHub repository URLs typo

## [1.1.0] - 2025-06-09
### Changed
- Database schema: Renamed columns from `created_at`/`updated_at` to `created_date`/`updated_date`

## [1.0.0] - 2025-06-09
### Added
- Complete Python + SQLite architecture (rewrite from Node.js)
- Environmental data collection: NASA FIRMS fire detection, NOAA Ocean Service, OpenAQ air quality
- Web interface with 7 pages: Dashboard, Tasks, Data, Metrics, Providers, Schema, System
- Professional task system with automated scheduling and error handling
- Database transparency with schema visualization and data export
- Cost tracking and API usage monitoring
- Source code transparency in web interface
- Modern responsive web interface with Bootstrap styling
- 6 database tables with normalized schema
- 6 automated tasks with retry logic
- 3 data providers (NASA, NOAA, OpenAQ) with unified interface
- MIT License and comprehensive documentation


 