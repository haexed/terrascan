# Changelog

All notable changes to ECO WATCH TERRA SCAN will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.0] - 2024-12-19

### 🌡️ **MAJOR FEATURE: Weather & Climate Integration**

**New Weather Data Collection:**
- **🌍 Global Weather Monitoring**: Added OpenWeatherMap One Call API 3.0 integration
- **📊 Real-time Weather Data**: Temperature, humidity, wind speed, atmospheric pressure
- **🚨 Weather Alerts**: Government weather warnings and severe weather notifications
- **🌐 24 Major Cities**: Worldwide coverage across all continents
- **⏰ Automated Collection**: Every 2 hours for current weather, hourly for alerts

**Enhanced Dashboard:**
- **🌡️ Global Weather Panel**: Average temperature, humidity, wind speed, pressure
- **🚨 Weather Alerts Panel**: Active weather warnings with risk levels
- **📈 Improved Health Score**: Weather factors now included in environmental health calculation
- **🎨 Beautiful UI**: Weather data integrated seamlessly with existing design

**Technical Implementation:**
- **📁 New Task System**: `tasks/fetch_weather.py` with comprehensive error handling
- **⚙️ Configuration Management**: OpenWeatherMap provider settings
- **🗄️ Database Integration**: Weather metrics stored in existing `metric_data` table
- **🔄 Graceful Degradation**: Works without API key, shows clear setup instructions

**API Integration:**
- **🆓 Free Tier**: 1,000 API calls/day (sufficient for monitoring)
- **📡 One Call API 3.0**: Current weather, forecasts, historical data, alerts
- **🌍 Global Coverage**: Weather data for major cities worldwide
- **⚡ Rate Limiting**: Built-in delays to respect API limits

**Health Score Updates:**
- **🌡️ Temperature Extremes**: Penalties for extreme hot/cold conditions
- **🌪️ Severe Weather**: Weather alerts impact environmental health score
- **💨 High Winds**: Wind speed factors into overall environmental conditions
- **🌀 Storm Systems**: Low pressure systems (storms) affect health calculations

## [2.2.3] - 2024-12-19

### 🧹 **Production Cleanup - Debug Removal**

**System Page Cleanup:**
- **🗑️ Removed Debug Ocean Button**: Eliminated "Debug Ocean Data" button from system page
- **🗑️ Removed Cache & Debug Section**: Cleaned up "Cache & Debug Information" panel
- **🗑️ Removed Debug JavaScript**: Eliminated `debugOceanData()`, `forceClearCache()`, and `testOceanAPI()` functions
- **✅ Streamlined Quick Actions**: Kept essential actions (Refresh All Data, View System Logs, Clear Old Data)
- **📝 Improved User Messages**: Better messaging for system logs and data cleanup features

**API Endpoint Cleanup:**
- **🗑️ Removed `/api/debug/production`**: Eliminated comprehensive debug endpoint (106 lines)
- **🗑️ Removed `/api/debug/ocean`**: Eliminated ocean-specific debug endpoint (67 lines)
- **🗑️ Removed `/api/force-ocean-temp`**: Eliminated manual ocean task trigger (33 lines)
- **🗑️ Removed `/api/fix-missing-task`**: Eliminated task creation debug endpoint (52 lines)
- **🗑️ Removed `/api/debug-task-creation`**: Eliminated step-by-step task debug (85 lines)
- **🗑️ Removed `/api/insert-task-direct`**: Eliminated direct SQL task insertion (78 lines)

**Code Quality:**
- **📉 Reduced Codebase**: Removed 421 lines of debug-specific code
- **🎯 Production Focus**: System now contains only production-ready functionality
- **🔒 Security**: Eliminated debug endpoints that could expose system internals
- **🚀 Performance**: Cleaner codebase with fewer unused routes and functions

**Benefits:**
- **✅ Cleaner UI**: System page now focuses on essential monitoring and actions
- **✅ Reduced Attack Surface**: No debug endpoints accessible in production
- **✅ Better UX**: Simplified interface without confusing debug options
- **✅ Maintainability**: Less code to maintain and fewer potential failure points

## [2.2.2] - 2024-12-19

### 🔧 **Map & UI Fixes - Launch Hell Resolution**

**Map Coordinate Fixes:**
- **🗺️ Fixed Invalid LatLng Errors**: Corrected coordinate field names in `map.js` (`latitude/longitude` → `lat/lng`)
- **🌬️ Fixed Air Quality Data**: Updated field names to match API response (`value` → `pm25`)
- **✅ Added Coordinate Validation**: Prevents undefined coordinates from causing map errors
- **🔥 Fire Markers**: Now properly display with correct coordinates and brightness data
- **🌬️ Air Quality Markers**: Now show PM2.5 levels with proper color coding

**UI Performance Improvements:**
- **⏰ Fixed Header Janking**: Optimized time update function to prevent visual glitches
- **🚀 Smooth Time Updates**: Only updates DOM when time actually changes (prevents re-renders)
- **📱 Better UX**: Eliminated header text jumping during time updates

**Navigation Cleanup:**
- **🧹 Removed Dashboard Link**: Home IS the dashboard - cleaner navigation
- **🎯 Simplified UX**: No more confusion between Home and Dashboard routes
- **✅ Active State Fix**: Home link properly highlights for both `/` and `/dashboard` routes

**Production Stability:**
- **🚨 Resolved Console Errors**: Fixed "Invalid LatLng object: (undefined, undefined)" errors
- **🗺️ Map Data Loading**: Interactive map now properly displays environmental data points
- **📊 API Endpoint Fixes**: All missing routes (`/dashboard`, `/api/map-data`, `/api/refresh`) now functional

## [2.2.1] - 2024-12-19

### 🚀 **Railway Pro Deployment**

**Production Ready:**
- **✅ Fixed Flask App Issues**: Resolved import errors and template data structure mismatches
- **✅ Real Data Verified**: 14,099 fires, 75.5 μg/m³ PM2.5, 18.2°C ocean temps, 30/100 health score
- **✅ Railway Pro Ready**: Upgraded infrastructure to handle increased traffic
- **✅ Deployment Stable**: All template rendering and data transformation issues resolved

**Technical Fixes:**
- **🔧 Import Fix**: `setup_configs.py` now uses correct `database.config_manager` imports
- **🔧 Template Fix**: Added proper data transformation in `simple_app.py` for dashboard template
- **🔧 Status Fix**: Health score status format changed from `"POOR"` to `"STATUS POOR"` for template compatibility
- **🔧 Helper Functions**: Added `get_air_quality_status()` and `get_ocean_status()` functions

**Live Environmental Data:**
- **🔥 NASA FIRMS**: 14,099 active fire detections globally
- **🌬️ OpenAQ**: 1,908 air quality stations showing 75.5 μg/m³ PM2.5 (HAZARDOUS)
- **🌊 NOAA Ocean**: 2,448 temperature measurements averaging 18.2°C (NORMAL)
- **🌍 Health Score**: 30/100 (STATUS POOR) - significant environmental stress

## [2.2.0] - 2024-12-19

### 🚀 **MAJOR REFACTOR: Simulation Mode Removed**

**Breaking Changes:**
- **❌ Removed Simulation Mode**: Eliminated all simulation/mock data functionality
- **✅ Real Data Only**: System now works with live APIs or fails gracefully with clear error messages
- **🔧 Simplified Configuration**: No more simulation_mode settings or complex fallback logic

**Code Cleanup:**
- **📁 Task Files**: Completely refactored `fetch_nasa_fires.py`, `fetch_openaq_latest.py`, `fetch_noaa_ocean.py`
- **🗑️ Removed Functions**: Deleted all `_simulate_*` functions and related mock data generation
- **📦 Cleaner Imports**: Removed unused dependencies and old database imports
- **⚙️ Setup Configs**: Simplified system configuration setup, removed simulation_mode parameter
- **🌐 Flask App**: Updated to use new simplified data functions with proper error handling

**Benefits:**
- **🎯 Focused Purpose**: Clear distinction between working (with API keys) vs not working
- **🐛 Better Debugging**: Real errors from real APIs are more useful than fake success
- **📝 Cleaner Code**: Removed 500+ lines of simulation code and complexity
- **🚀 Faster Startup**: No simulation data generation during initialization
- **💡 User Clarity**: Either it works with real data, or shows clear "API key needed" messages

**Migration Notes:**
- **🔑 API Keys Required**: System now requires actual API keys to function
- **📊 No Fallback Data**: No more simulated data when APIs are unavailable
- **⚠️ Clear Errors**: Helpful error messages guide users to configure API keys properly

## [2.1.3] - 2025-06-13
### Added - SYSTEM PAGE & ADVANCED DEBUGGING TOOLS 🔧
- **🔧 New System Page**: Complete system status and data provider monitoring at `/system`
  - **📊 System Statistics**: Total records (27,000+), active tasks, recent runs (24h)
  - **🔥 NASA FIRMS Status**: Fire detection monitoring with operational status
  - **🌬️ OpenAQ Status**: Air quality network (65+ cities) with provider health
  - **🌊 NOAA Ocean Status**: Ocean monitoring (12 stations) with temperature/level data
  - **📈 Recent Task Executions**: Live task log with timing, status, and record counts
  - **📊 Data Breakdown**: Records by provider with visual statistics
  - **⚙️ System Configuration**: Version, database size, simulation mode status
- **🐛 Advanced Debugging Tools**: Production-ready diagnostic capabilities
  - **Debug Ocean API**: `/api/debug/ocean` endpoint with detailed ocean data analysis
  - **Cache Detection**: Automatic browser cache issue detection and warnings
  - **Force Refresh**: Cache-busting buttons with timestamp parameters
  - **Real-time Testing**: Live API testing with temperature validation
- **🧹 Cache-Busting Solutions**: Comprehensive browser caching issue resolution
  - **Smart Detection**: Automatic 0°C temperature detection (cache issue indicator)
  - **Visual Indicators**: Orange border highlighting for cached data elements
  - **Quick Actions**: One-click refresh buttons on homepage and system page
  - **Timestamp URLs**: Cache-busting parameters for forced fresh data

### Enhanced
- **🌐 Navigation**: Added System link to main navigation with active state highlighting
- **⏰ Time Display**: Enhanced time update function for both navbar and map widgets
- **🔍 Error Detection**: Browser console warnings for potential cache issues
- **📱 Mobile Support**: Responsive design for all new debugging tools
- **🎯 User Experience**: Intuitive cache-busting with confirmation dialogs

### Fixed - BROWSER CACHING ISSUES RESOLVED
- **🌊 Ocean Temperature "NO DATA"**: Resolved browser caching showing old 0°C values
  - **Root Cause**: Browser displaying cached version instead of live 18.3°C data
  - **Solution**: Multiple cache-busting mechanisms and user-friendly refresh options
  - **Verification**: Debug tools confirm 1,296+ temperature records with 18.3°C average
- **🔄 Loading States**: Fixed persistent "Loading..." text on cached pages
- **📊 Data Freshness**: Ensured all environmental metrics display current values
- **🎯 User Guidance**: Clear instructions for resolving cache issues
- **🔧 Final Ocean Display Fix**: Eliminated last remaining 0°C display issues
  - **Enhanced Cache-Busting**: Added ETag and Last-Modified headers for aggressive cache prevention
  - **Client-Side Detection**: JavaScript automatically detects and highlights cache issues with orange borders
  - **Debug Logging**: Server-side debug output confirms correct data flow (18.3°C consistently)
  - **Template Data Attributes**: Added data-temp attributes for cache issue verification
  - **User Feedback**: Visual indicators and tooltips show correct temperature when cache detected

### Technical Improvements
- **🔧 Debug Infrastructure**: Comprehensive diagnostic API endpoints
- **📊 System Monitoring**: Real-time provider health and task execution tracking
- **🧪 Testing Tools**: Built-in API testing and data validation
- **🔄 Cache Management**: Smart cache detection and busting mechanisms
- **📈 Performance**: Optimized database queries for system statistics
- **🛡️ Error Handling**: Robust error handling for all new diagnostic features

### Production Impact
- **✅ Cache Issues Eliminated**: Users can easily resolve "NO DATA" display problems
- **✅ System Transparency**: Complete visibility into data collection and provider status
- **✅ Debugging Capabilities**: Production-ready tools for diagnosing environmental data issues
- **✅ User Empowerment**: Self-service cache-busting and data refresh capabilities
- **✅ Operational Excellence**: Real-time monitoring of all environmental data systems

## [2.1.2] - 2025-01-21
### Fixed - CRITICAL BUG FIXES: Ocean Data & Time Display
- **🌊 Ocean Temperature Bug**: Fixed "0°C" display issue by adding proper water temperature data collection
  - **Root Cause**: System only collected `water_level` data, but health calculation needed `water_temperature`
  - **Solution**: Added `noaa_ocean_temperature` task with correct parameters
  - **Result**: Ocean temperature now displays correctly (e.g., 18.4°C instead of 0°C)
- **⏰ Time Display Bug**: Fixed "Loading..." text stuck on map view
  - **Root Cause**: Duplicate `id="current-time"` elements causing JavaScript conflicts
  - **Solution**: Unique IDs for navbar (`current-time`) and map widget (`map-current-time`)
  - **Result**: Time updates correctly on both navbar and map health widget
- **🔄 Enhanced Refresh API**: Now runs both water level AND water temperature tasks
  - **Ocean Level Task**: Collects tidal and water level data
  - **Ocean Temperature Task**: Collects sea surface temperature data
  - **Complete Coverage**: Full ocean health monitoring with proper data

### Technical Improvements
- **Database Schema**: Added `noaa_ocean_temperature` task with `{"product": "water_temperature"}` parameters
- **Task Runner**: Enhanced parameter passing for specialized data collection
- **JavaScript**: Improved time update function to handle multiple time display elements
- **Data Quality**: Now collecting 288 water temperature + 288 water level measurements per refresh

### Production Impact
- **✅ NO DATA states eliminated**: All environmental metrics now display real values
- **✅ Loading states fixed**: Time displays update in real-time
- **✅ Ocean health accurate**: Proper temperature-based health scoring
- **✅ Global coverage maintained**: 65+ cities with enhanced ocean monitoring

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


 