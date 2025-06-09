# Changelog

All notable changes to Terrascan will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
