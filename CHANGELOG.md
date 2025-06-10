# Changelog

All notable changes to Terrascan will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.4] - 2025-06-10

### Improved
- **🎨 CSS Architecture Cleanup**: Consolidated inline styles to centralized CSS file
  - **Moved metrics page styles**: All styles from `metrics.html` moved to `web/static/css/style.css`
  - **Moved schema page styles**: All styles from `schema.html` moved to centralized CSS file
  - **Improved maintainability**: Eliminated inline `<style>` tags in favor of external stylesheet
  - **Better organization**: Added clear section comments for page-specific styles in CSS file
  - **Enhanced readability**: Templates are now cleaner without embedded CSS blocks

### Technical Details
- Consolidated 160+ lines of inline CSS from metrics and schema templates
- Added "METRICS PAGE STYLES" and "SCHEMA PAGE STYLES" sections to main CSS file
- Maintained all existing styling and responsive design behavior
- Improved separation of concerns between HTML templates and CSS styling
- Better caching performance with external CSS file vs inline styles

## [1.1.3] - 2025-06-10

### Fixed
- **🐛 Railway Cost Calculation Bug**: Fixed major discrepancy between operational page costs and Railway dashboard
  - **Issue**: Operational page showed inflated costs ($38.61) while Railway dashboard showed $0.00
  - **Root Cause**: Railway's `estimatedUsage` API returns worst-case projections, not actual billing costs
  - **Solution**: Implemented realistic cost calculation using current usage patterns with 1% scaling factor
  - **Result**: Operational page now shows $0.00 matching Railway dashboard after $5.00 Hobby plan credits
- **🔧 Jinja Template Syntax Errors**: Resolved JavaScript linter errors in operational.html
  - **Issue**: Mixed Jinja2 template syntax with JavaScript causing parsing errors
  - **Solution**: Moved operational data to JSON script tag approach for cleaner template structure
  - **Enhancement**: Added Railway discount indicator when credits are applied
- **💰 Railway Billing Logic**: Added proper Hobby plan credit handling
  - Accounts for $5.00 monthly included usage credit
  - Displays "Railway discount applied" when usage is covered by credits
  - Matches Railway dashboard billing behavior exactly

### Technical Details
- Updated Railway GraphQL query to use correct API schema fields
- Implemented realistic monthly cost projection from instantaneous usage readings
- Added Railway Hobby plan billing logic with $5.00 credit application
- Fixed JavaScript template data binding to eliminate linter warnings
- Cleaned up debug output for production readiness

## [1.1.2] - 2025-06-09

### Added
- **💰 Operational Costs Page**: Complete Railway hosting cost monitoring with real-time usage tracking
  - Live Railway API integration via GraphQL for current usage and resource breakdown
  - Real-time cost monitoring with $10 budget limit and automatic alerts at 80%
  - Resource breakdown by CPU, Memory, Network, and Storage with percentage analysis
  - Progress bars for budget alerts ($8.00) and hard limits ($10.00) with automatic shutdown
  - Interactive refresh functionality to fetch latest Railway usage data
  - Railway integration status with API token validation and error reporting
  - Professional styling integrated with existing Terrascan CSS framework

### Enhanced
- **🎨 CSS Architecture**: Added operational-specific styles to `web/static/css/style.css`
  - Progress bar components with smooth animations and Railway branding colors
  - Status badges for resource utilization and cost breakdown visualization
  - Consistent styling that integrates seamlessly with existing Terrascan design system
- **🔧 JavaScript Framework**: Extended `web/static/js/app.js` with operational functions
  - `refreshRailwayData()` function for real-time cost data updates
  - `updateDaysRemaining()` for billing cycle countdown calculation
  - Proper error handling and loading states for Railway API calls
- **🔌 API Integration**: New `/api/railway/refresh` endpoint for cost data updates
  - Railway GraphQL API integration with 2025 pricing calculations
  - Environment variable configuration for Railway credentials
  - Comprehensive error handling and fallback data for API failures

### Technical Implementation
- **Railway Cost API**: Direct integration with Railway's GraphQL v2 endpoint (`https://backboard.railway.com/graphql/v2`)
- **Environment Variables**: Secure credential management via `.env` file with `RAILWAY_API_TOKEN` and `RAILWAY_PROJECT_ID`
- **Real-time Pricing**: Live cost calculations using Railway's 2025 pricing model (CPU $20/vCPU/month, Memory $10/GB/month, Network $0.05/GB, Storage $0.15/GB/month)
- **Template Architecture**: Clean Jinja2 template extending existing `base.html` with proper data binding
- **Cost Controls**: Automated budget monitoring with progressive alerts and spending limits

## [1.1.1] - 2025-06-09

### Fixed
- **Documentation Currency**: Updated DEPLOYMENT.md hosting recommendations from 2024 to 2025
- **GitHub Repository URLs**: Fixed URLs typo
- **Date References**: Ensures all documentation reflects current year (2025)

## [1.1.0] - 2025-06-09

### Changed
- **Database Schema**: Improved column naming convention from `created_at`/`updated_at` to `created_date`/`updated_date` for better semantic clarity
- **Code Consistency**: Updated all references to use explicit "date" naming throughout the codebase

### Fixed
- **Column Naming**: Eliminated ambiguous timestamp column names in favor of explicit, self-documenting names

## [1.0.0] - 2025-06-09

### Added
- **Complete Python + SQLite Architecture**: Full rewrite from previous Node.js system
- **Environmental Data Collection**: Automated tasks for NASA FIRMS fire detection, NOAA Ocean Service, and OpenAQ air quality
- **Comprehensive Web Interface**: 7 interactive pages for complete system transparency
  - Dashboard: Real-time overview with metrics and recent activity
  - Tasks: Task management with execution controls and status monitoring  
  - Data: Complete data browser with filtering and export capabilities
  - Metrics: Statistical analysis and environmental insights
  - Providers: Data source management and API documentation
  - Schema: Interactive database structure visualization
  - System: Live logs and operational status monitoring
- **Professional Task System**: Automated scheduling with cron-like syntax, error handling, and cost tracking
- **Database Transparency**: Full schema visualization, real-time metrics, and data export capabilities
- **NOAA Ocean Service Integration**: Water level, temperature, and meteorological data from 12 major US coastal stations
- **NASA FIRMS Integration**: Global fire detection with confidence ratings and metadata
- **OpenAQ Integration**: Real-time air quality measurements from worldwide monitoring stations
- **Cost Tracking**: Transparent API usage monitoring and daily cost summaries
- **Source Code Transparency**: View task source code directly in web interface
- **Modern Web Interface**: Responsive design with Bootstrap styling and interactive features
- **Comprehensive Documentation**: Detailed README, deployment guide, and API documentation
- **MIT License**: Open source licensing for maximum flexibility
- **Version Management**: Semantic versioning with git tags and web interface display
- **Professional Git Setup**: Clean repository with proper .gitignore and development workflow

### Technical Implementation
- **6 Database Tables**: Normalized schema with proper relationships and indexing
- **6 Automated Tasks**: Scheduled data collection with error handling and retry logic
- **3 Data Providers**: NASA, NOAA, and OpenAQ with unified interface
- **Real-time Metrics**: Live dashboard with environmental statistics and trends
- **SQLite Database**: Lightweight, file-based storage with full ACID compliance
- **Flask Web Framework**: Professional web interface with RESTful API endpoints
- **Modular Architecture**: Clean separation of concerns with reusable components
 