# 🌍 Terrascan - Environmental Data Platform

**Environmental data aggregation and analysis platform built for geological timescales.**

**🎯 Environmental time machine showing current conditions in deep historical context**

---

## 🌱 **Environmental Impact & Mission**

**Primary Mission**: Create the world's most compelling environmental time machine.

**Core Values**:
- 🔓 **Open Data** - All environmental data should be freely accessible
- 🔬 **Scientific Transparency** - Show your work, open source everything
- 🌍 **Global Perspective** - Environmental challenges need global solutions
- 🕰️ **Long-term Thinking** - Geological timescales over quarterly reports

**Technical Philosophy**:
- Choose simplicity over sophistication
- SQLite over complex cloud databases
- Python scientific stack over JavaScript frameworks
- VPS hosting over serverless complexity
- Free data sources over proprietary APIs

---

## 🚀 **Quick Start**

```bash
git clone https://github.com/haexed/terrascan.git
cd terrascan

# Install dependencies
pip install -r requirements.txt

# Set up environment (optional - works in simulation mode)
cp .env.example .env

# Initialize database and start
python3 run.py

# Visit: http://localhost:5000
```

**That's it!** Terrascan works out of the box with simulated data, then add real API keys when ready.

---

## ✨ **What You Get**

### **🌐 Complete Web Interface**
- **📊 Dashboard** - System overview with real-time statistics
- **🔧 Tasks** - Manage data collection with "Run Now" buttons
- **📈 Data** - Explore 3,000+ environmental records collected
- **📊 Metrics** - Detailed analysis of all environmental metrics
- **🌐 Providers** - Browse NASA, NOAA, OpenAQ data sources
- **🗂️ Schema** - Visual database structure with relationships
- **🖥️ System** - Full transparency with logs and monitoring

### **🤖 Automated Data Collection**
- **🔥 NASA FIRMS** - Global fire detection from satellites
- **🌊 NOAA Ocean Service** - Water levels, temperature from 12 coastal stations
- **🌬️ OpenAQ** - Air quality (PM2.5) from global monitoring networks
- **⚙️ Configurable Tasks** - Easy to add new data sources

### **🗂️ Smart Data Architecture**
- **SQLite Database** - Simple, fast, no configuration needed
- **Normalized Schema** - Clean separation of tasks, providers, metrics
- **Full Transparency** - Every data point traceable to its source
- **Time-Series Optimized** - Built for geological timescale analysis

---

## 🏗️ **Architecture**

```
🌐 Flask Web UI ─── 📊 7 Interactive Pages
         │
         ▼
🤖 Task System ──── 🔧 Automated Data Collection
         │
         ▼  
🌍 Data Providers ─ 🔥 NASA/NOAA/OpenAQ APIs
         │
         ▼
💾 SQLite Database ─ 📈 Environmental Time Series
```

### **🎯 Design Philosophy**
- **🐍 Python-First** - Leverage scientific ecosystem (pandas, numpy, etc.)
- **💾 SQLite Simplicity** - Perfect for read-heavy environmental data
- **🕰️ Geological Timescales** - Years/decades over real-time
- **🔍 Full Transparency** - View source code for every data collection
- **🆓 Free & Open** - No vendor lock-in, runs anywhere

---

## 📊 **Current Data Collection**

| Provider | Status | Data Type | Records | Coverage |
|----------|--------|-----------|---------|----------|
| 🔥 **NASA FIRMS** | ✅ Active | Fire Detection | 2,700+ | Global |
| 🌊 **NOAA Ocean** | ✅ Active | Water Level/Temp | 720+ | 12 US Stations |
| 🌬️ **OpenAQ** | ✅ Active | Air Quality PM2.5 | 36+ | Global Cities |

**📈 Total: 3,400+ environmental measurements and growing**

---

## 🔧 **Features Deep Dive**

### **📊 Dashboard**
- Live system statistics and health monitoring
- Recent activity feed from all data collection tasks
- Quick-action buttons for manual task execution
- Cost tracking (all current sources are free!)

### **🔧 Task Management**
- **▶️ One-Click Execution** - Run any data collection task instantly
- **📄 Source Code Viewer** - See exactly how data is collected
- **📊 Real-Time Monitoring** - Live task status and performance
- **⏰ Scheduling** - Automated collection via cron schedules

### **📈 Data Exploration**
- Browse 3,400+ environmental records with full metadata
- Filter by provider, dataset, time range
- Geographic distribution of monitoring points
- Statistical summaries and data quality indicators

### **📊 Metrics Analysis**
- Comprehensive overview of all environmental metrics (fire brightness, water levels, air quality)
- Statistical analysis: min/max/average values per metric
- Geographic coverage: unique monitoring locations
- Temporal coverage: earliest to latest measurements
- Provider comparison and data quality insights

### **🌐 Provider Management**
- Browse all data sources (NASA, NOAA, OpenAQ)
- Real-time statistics for each provider
- Documentation links and API information
- Task configuration and scheduling per provider

### **🗂️ Schema Visualization**
- Table relationships and foreign keys
- Column types, constraints, and indexes
- Live row counts and data freshness
- Primary key highlighting and constraint visualization

### **🖥️ System Transparency**
- Complete task execution logs with timestamps
- Error handling and debugging information
- Performance metrics and execution times
- System health monitoring and alerts

---

## 🌍 **Supported Data Sources**

### **🔥 NASA FIRMS (Fire Information)**
- **Coverage**: Global satellite fire detection
- **Frequency**: Every 2 hours
- **Metrics**: Fire brightness temperature (Kelvin)
- **Locations**: Worldwide fire hotspots
- **API**: Free, requires registration

### **🌊 NOAA Ocean Service**
- **Coverage**: 12 major US coastal stations
- **Frequency**: Every 3 hours
- **Metrics**: Water level (meters), temperature (°C)
- **Locations**: NY, MA, VA, SC, FL, TX, CA, WA, HI, AK
- **API**: Free, no registration required

### **🌬️ OpenAQ (Air Quality)**
- **Coverage**: Global air quality monitoring networks
- **Frequency**: Hourly
- **Metrics**: PM2.5 concentration (μg/m³)
- **Locations**: Major cities worldwide
- **API**: Free, no registration required

---

## 🛠️ **Development & Customization**

### **Adding New Data Sources**

1. **Create Task Function** (`tasks/fetch_new_source.py`):
```python
def fetch_new_data(param1='default'):
    """Fetch data from new source"""
    # Get configuration
    base_url = get_provider_config('new_source', 'base_url')
    
    # Fetch and process data
    # ... your logic here ...
    
    # Store results
    store_metric_data(
        timestamp=datetime.now().isoformat(),
        provider_key='new_source',
        dataset='environmental',
        metric_name='new_metric',
        value=measurement_value,
        unit='units',
        location_lat=latitude,
        location_lng=longitude,
        metadata={'source': 'details'}
    )
    
    return {
        'output': f'Collected {count} measurements',
        'records_processed': count,
        'cost_cents': 0
    }
```

2. **Register Provider** (via database):
```sql
INSERT INTO provider (key, name, description, base_url) 
VALUES ('new_source', 'New Data Source', 'Description', 'https://api.example.com');
```

3. **Register Task**:
```sql
INSERT INTO task (name, description, command, provider, dataset) 
VALUES ('new_data_task', 'Collect new data', 'tasks.fetch_new_source', 'new_source', 'environmental');
```

4. **Update imports** (`tasks/__init__.py`):
```python
from .fetch_new_source import fetch_new_data
```

**That's it!** The web interface automatically discovers and displays your new data source.

---

## 📈 **Current Status & Roadmap**

### **✅ Phase 1: Foundation (COMPLETE)**
- ✅ Python + SQLite architecture with normalized schema
- ✅ Comprehensive web interface (7 pages: Dashboard, Tasks, Data, Metrics, Providers, Schema, System)
- ✅ Task system with full transparency and source code viewing
- ✅ 3 active data providers (NASA FIRMS, NOAA Ocean Service, OpenAQ)
- ✅ Schema visualization and metrics analysis pages
- ✅ NOAA Ocean Service integration with 12 coastal stations
- ✅ 3,400+ environmental measurements collected and growing

### **🔄 Phase 2: Data Visualization (IN PROGRESS)**
- 🔄 Interactive maps showing fire locations and monitoring stations
- 🔄 Time-series charts for temperature and pollution trends
- 🔄 Historical data import and analysis
- 🔄 Cross-correlation between different environmental factors

### **🔮 Phase 3: Intelligence**
- 🔮 Automated anomaly detection
- 🔮 Historical comparison algorithms  
- 🔮 Trend analysis and predictions
- 🔮 Custom alert systems

### **🚀 Phase 4: Scale**
- 🚀 Multi-region data collection
- 🚀 API for external integrations
- 🚀 Advanced visualization tools
- 🚀 Community data contributions

---

## 🤝 **Contributing**

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**: Add new data sources, improve visualizations
4. **Test locally**: `python3 run.py`
5. **Submit pull request**: Describe your environmental data contribution

**Most Wanted Contributions**:
- 🌍 New environmental data sources
- 📊 Data visualization improvements
- 🗺️ Interactive mapping features
- 📈 Historical data analysis tools
- 🌐 Internationalization and localization

---

## 📄 **License & Credits**

**MIT License** - Use Terrascan however you want, just keep environmental data free!

**Development Team**:
- **Stig Grindland** - Project Manager, Systems Architecture, Vision & Direction
- **Claude (Anthropic)** - Lead Developer, Code Implementation, Technical Architecture

**Data Sources**:
- NASA FIRMS for fire detection data
- NOAA Ocean Service for water level and temperature
- OpenAQ for air quality measurements
- All providers offer free API access

**Built With**: Python, Flask, SQLite, HTML, CSS, JavaScript

---

**🌍 Help us build the environmental time machine the world needs! 🌍**
