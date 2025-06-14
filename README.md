# 🌍 TERRASCAN

**Monitor Earth's environmental health in real-time**

![Version](https://img.shields.io/badge/version-3.0.1-blue)
![Database](https://img.shields.io/badge/database-PostgreSQL-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![Status](https://img.shields.io/badge/status-production-green)

**TERRASCAN** gives you instant access to current environmental conditions across the globe:

- 🔥 **Active Wildfires**: Live fire detection from NASA satellites
- 🌬️ **Air Quality**: Real-time pollution levels from 200+ monitoring stations  
- 🌊 **Ocean Health**: Sea surface temperature and water level data from NOAA
- 🌡️ **Global Weather**: Current conditions and alerts for 24+ major cities
- 🦋 **Biodiversity**: Species observations from 18 global biodiversity hotspots
- 📊 **Health Score**: Combined environmental health indicator (0-100)

**🌐 Live Site**: [terrascan.io](https://terrascan.io)

---

## ⚡ Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/haexed/terrascan.git
   cd terrascan
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Start the application**
   ```bash
   python run.py
   ```

5. **Open your browser**
   ```
   http://localhost:5000
   ```

**🔑 API Keys Required**: TERRASCAN works with real environmental data from NASA, NOAA, and OpenAQ APIs.

### Get Your API Keys

| Provider | API Key Required | Free Tier | Sign Up Link |
|----------|------------------|-----------|--------------|
| 🔥 NASA FIRMS | Yes | 1000/day | [NASA Earthdata](https://urs.earthdata.nasa.gov/) |
| 🌬️ OpenAQ | Recommended | 10,000/month | [OpenAQ](https://openaq.org/) |
| 🌊 NOAA | Yes | 1000/day | [NOAA API](https://www.ncdc.noaa.gov/cdo-web/token) |
| 🌡️ OpenWeatherMap | Yes | 1000/day | [OpenWeatherMap](https://openweathermap.org/api) |
| 🦋 GBIF | No | Unlimited | Free (no key required) |

---

## 🚀 Production Deployment

TERRASCAN is production-ready and deployed on Railway at [terrascan.io](https://terrascan.io).

### Railway Deployment

1. **Create Railway project**
   ```bash
   railway login
   railway init
   ```

2. **Add PostgreSQL database**
   ```bash
   railway add postgresql
   ```

3. **Set environment variables**
   ```bash
   railway variables set NASA_API_KEY=your_key
   railway variables set OPENAQ_API_KEY=your_key
   railway variables set NOAA_API_KEY=your_key
   railway variables set OPENWEATHERMAP_API_KEY=your_key
   ```

4. **Deploy**
   ```bash
   railway up
   ```

### Task Management Security

**🔒 Admin Task Control**: For security, task management is **read-only** for public users. Task enable/disable controls are managed via environment variables:

```bash
# Environment variables for production task control
TASK_ENABLED_FIRES=true
TASK_ENABLED_AIR_QUALITY=true
TASK_ENABLED_OCEAN=true
TASK_ENABLED_WEATHER=true
TASK_ENABLED_BIODIVERSITY=true
```

**Public Interface**: The `/tasks` page shows monitoring information:
- ✅ Task status and last run information
- ✅ Recent execution logs (last 10 runs)
- ✅ Success/failure statistics

**Admin Control**: Task configuration changes require:
- Railway dashboard environment variable updates
- Database configuration changes
- Server restart for changes to take effect

---

## 📊 System Architecture

### Database Architecture

TERRASCAN is built on **PostgreSQL** for production deployment:

**PostgreSQL (Production & Development)**
```bash
# Set via environment variable
DATABASE_URL=postgresql://user:pass@host:port/db
```

**Railway PostgreSQL** (Recommended)
```bash
# Automatically configured via Railway
railway add postgresql
# DATABASE_URL automatically set
```

### Data Collection Tasks

| Task | Description | Frequency | Records/Run |
|------|-------------|-----------|-------------|
| 🔥 NASA Fires | Active fire detection | 15 minutes | ~500-2000 |
| 🌬️ OpenAQ Latest | Air quality stations | 30 minutes | ~200-500 |
| 🌊 NOAA Ocean | Ocean temperature/levels | 1 hour | ~100-300 |
| 🌡️ OpenWeatherMap | Current conditions/alerts | 2 hours | ~50-100 |
| 🦋 GBIF Biodiversity | Species observations | 6 hours | ~20-50 |

### Database Schema

```sql
-- Core tables
CREATE TABLE metric_data (...)     -- Environmental measurements
CREATE TABLE task (...)           -- Task definitions  
CREATE TABLE task_log (...)       -- Execution history
CREATE TABLE system_config (...)  -- Application settings
```

For complete schema details, see: [database/schema.sql](database/schema.sql)

---

## 🛠️ Local Development Setup

### Requirements

- Python 3.8+
- pip package manager
- Internet connection (for API calls)

### SQLite Development (Recommended)

```bash
# 1. Clone and setup
git clone https://github.com/haexed/terrascan.git
cd terrascan
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Run application
python run.py
```

### PostgreSQL Development (Advanced)

For local PostgreSQL development, see: [DEVELOPMENT.md](DEVELOPMENT.md)

---

## 📡 API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/tasks` | GET | Task monitoring |
| `/system` | GET | System status |
| `/map` | GET | Interactive map view |
| `/about` | GET | Project information |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/dashboard-data` | GET | Dashboard metrics |
| `/api/map-data` | GET | Map markers data |
| `/api/refresh` | POST | Trigger data collection |
| `/api/tasks` | GET | Task list and status |
| `/api/tasks/<name>/logs` | GET | Task execution logs |

### Administrative APIs

**🔒 Note**: Administrative task control is environment-based. No public APIs for task management.

---

## 🌍 Environmental Impact

**TERRASCAN** promotes environmental awareness by:

- **🔥 Fire Monitoring**: Early wildfire detection and tracking
- **🌬️ Air Quality**: Public health air pollution alerts  
- **🌊 Ocean Health**: Climate change ocean temperature monitoring
- **🌡️ Weather Tracking**: Extreme weather event awareness
- **🦋 Biodiversity**: Species conservation monitoring
- **📈 Data Transparency**: Open access to environmental data
- **🎯 Health Scoring**: Simplified environmental health communication

### Data Sources

- **NASA FIRMS**: Fire Information for Resource Management System
- **OpenAQ**: Open Air Quality platform with global coverage
- **NOAA**: National Oceanic and Atmospheric Administration
- **OpenWeatherMap**: Global weather data and alerts
- **GBIF**: Global Biodiversity Information Facility

---

## 🤝 Contributing

We welcome contributions! Here's how to help:

### Development Setup

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/your-username/terrascan.git
cd terrascan

# 3. Create a feature branch
git checkout -b feature/your-feature-name

# 4. Set up development environment
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env

# 5. Make your changes and test
python run.py

# 6. Commit and push
git add .
git commit -m "Add your feature"
git push origin feature/your-feature-name

# 7. Create a pull request
```

### What We Need

- 🐛 **Bug Fixes**: Report issues or submit fixes
- 🌟 **New Features**: Environmental data sources, visualizations
- 📚 **Documentation**: Improve setup guides, API docs
- 🎨 **UI/UX**: Design improvements, mobile responsiveness
- 🧪 **Testing**: Unit tests, integration tests
- 🌍 **Localization**: Multi-language support

---

## 🙏 Credits

**TERRASCAN** is developed through collaborative human-AI partnership:

- **🎯 Project Management & Vision**: [Stig Grindland](https://hæx.com)
  - Strategic direction and system architecture decisions
  - Quality assurance and production deployment planning
  - Environmental data source selection and API integration strategy

- **⚡ Development & Implementation**: Claude Sonnet (Anthropic)
  - Full-stack development and database architecture
  - API integrations and real-time monitoring systems
  - Security implementation and production optimization

This project demonstrates the power of human creativity and AI capability working together to build meaningful environmental technology.

---

## 📄 License

**MIT License** - Use TERRASCAN however you want, spread environmental awareness!

See [LICENSE](LICENSE) for full details.

---

## 🔗 Links

- **🌐 Live Site**: [terrascan.io](https://terrascan.io)  
- **📂 Source Code**: [GitHub](https://github.com/haexed/terrascan)
- **📊 Railway**: [Production Dashboard](https://railway.app)
- **🐛 Issues**: [GitHub Issues](https://github.com/haexed/terrascan/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/haexed/terrascan/discussions)

---

**🌱 Keep watch on our planet. Every day.**
