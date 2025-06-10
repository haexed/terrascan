# Changelog

All notable changes to Terrascan will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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


 