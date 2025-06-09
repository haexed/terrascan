# Changelog

All notable changes to Terrascan will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-09

### Added
- **Complete Python + SQLite Architecture**: Full rewrite from previous Node.js system
- **Environmental Data Collection**: Automated tasks for NASA FIRMS fire detection, NOAA Ocean Service, and OpenAQ air quality
- **Comprehensive Web Interface**: 7 interactive pages for complete system transparency
  - Dashboard: Real-time overview with metrics and recent activity
  - Tasks: Task management with execution controls and status monitoring  
  - Data: Complete data browser with filtering and export capabilities
  - Metrics: Environmental data analysis with provider-grouped statistics
  - Providers: Data source information and API status
  - Schema: Interactive database schema visualization
  - System: Live logs and system health monitoring
- **Advanced Data Processing**: 
  - 3 active data providers with 6 automated collection tasks
  - Normalized database schema with proper relationships
  - Real-time data validation and error handling
- **Task Automation System**:
  - Configurable scheduling (hourly to daily intervals)
  - Automatic retry logic and error recovery
  - Comprehensive logging and monitoring
- **Data Providers**:
  - **NASA FIRMS**: Global and regional fire detection data
  - **NOAA Ocean Service**: Water levels, temperature, wind, and marine conditions
  - **OpenAQ**: Global air quality measurements
- **Professional Features**:
  - SQLite database with full ACID compliance
  - RESTful API endpoints for all data access
  - Source code transparency with syntax highlighting
  - Export capabilities (JSON, CSV)
  - Real-time metrics and statistical analysis

### Technical Details
- **Backend**: Python 3.x with Flask web framework
- **Database**: SQLite with normalized schema (6 tables)
- **Frontend**: Modern responsive HTML/CSS/JavaScript
- **Architecture**: Modular design with separate database, tasks, and web layers
- **Data Volume**: Capable of handling 3,400+ environmental records
- **Monitoring**: Complete system introspection and live status reporting

### Notes
- This represents a complete architectural rewrite
- All previous Node.js/Vercel code has been replaced
- System designed for local deployment with SQLite persistence
- Ready for expansion with additional environmental data providers 
