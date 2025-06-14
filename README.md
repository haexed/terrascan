# 🌍 ECO WATCH TERRA SCAN

**Real-time environmental health dashboard showing what's happening to our planet right now.**

**🎯 Know your planet's pulse - fires, air quality, ocean temps - all in one view**

**🚀 Live at [terrascan.io](https://terrascan.io) - Hosted on Railway with PostgreSQL**

---

## 🌱 **Mission: Environmental Awareness Now**

**ECO WATCH TERRA SCAN** gives you instant access to current environmental conditions across the globe:

- 🔥 **Active Fires** - Live fire detection from NASA satellites
- 🌬️ **Air Quality** - Real-time pollution levels in major cities  
- 🌊 **Ocean Health** - Current water temperature and levels from NOAA
- 🌍 **Environmental Score** - Overall planetary health indicator
- 🔧 **Task Management** - Monitor and control data collection processes

**Philosophy**: Real data only. Either it works with live APIs, or shows clear guidance on what's needed.

---

## 🚀 **Quick Start**

### **🌐 Production Deployment**
- **Live Dashboard**: [terrascan.io](https://terrascan.io)
- **Hosting**: Railway with PostgreSQL database
- **Auto-deployment**: Push to main branch triggers deployment
- **Monitoring**: Built-in task management and system status

### **💻 Local Development**

```bash
git clone https://github.com/haexed/terrascan.git
cd terrascan

# Install dependencies
pip install -r requirements.txt

# Configure API keys (copy .env.example to .env)
cp .env.example .env
# Edit .env with your API keys

# Option 1: SQLite (Simple - Zero Config)
python3 run.py

# Option 2: PostgreSQL (Recommended for production-like development)
# See "Local PostgreSQL Setup" section below

# Visit: http://localhost:5000
```

**🔑 API Keys Required**: ECO WATCH works with real environmental data from NASA, NOAA, and OpenAQ APIs.

---

## 🗄️ **Database Architecture**

### **🏢 Production (Railway)**
- **Database**: PostgreSQL (managed by Railway)
- **Environment**: `DATABASE_URL` automatically configured
- **Features**: Full ACID compliance, concurrent connections, production performance
- **Backup**: Automated daily backups via Railway

### **💻 Local Development**

**Option 1: SQLite (Default - Zero Configuration)**
```bash
# Automatically creates ./database/terrascan.db
python3 run.py
```

**Option 2: PostgreSQL (Recommended)**
```bash
# Install PostgreSQL locally
sudo apt-get install postgresql postgresql-contrib  # Ubuntu/Debian
brew install postgresql                             # macOS
# Windows: Download from postgresql.org

# Create database and user
sudo -u postgres psql
CREATE DATABASE terrascan_dev;
CREATE USER terrascan_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE terrascan_dev TO terrascan_user;
\q

# Set environment variable for local PostgreSQL
export DATABASE_URL="postgresql://terrascan_user:your_password@localhost/terrascan_dev"

# Run setup script to create tables
python3 setup_production_railway.py

# Start application
python3 run.py
```

**🔄 Database Migration**: The system automatically detects the environment and uses appropriate database drivers (psycopg2 for PostgreSQL, sqlite3 for SQLite).

---

## ✨ **What You See**

### **🌐 Single Dashboard View**
- **🔥 Fire Alert Status** - Global active fires with brightness levels
- **🌬️ Air Quality Index** - PM2.5 levels from cities worldwide
- **🌊 Ocean Conditions** - Water temperatures from 12 US coastal stations
- **🌍 Environmental Health Score** - Combined 0-100 planetary health indicator
- **🔧 Task Management** - Monitor and control data fetching tasks
- **📱 Mobile-Friendly** - Check planetary health from anywhere

### **📊 Environmental Health Score (0-100)**

The **Planetary Health Score** combines critical environmental factors into a single 0-100 indicator:

**🔥 Fire Impact (up to -30 points):**
- 0-100 fires: No deduction
- 101-500 fires: -10 points  
- 501-1000 fires: -20 points
- 1000+ fires: -30 points

**🌬️ Air Quality Impact (up to -40 points):**
- 0-15 μg/m³ PM2.5: No deduction (WHO Good)
- 16-35 μg/m³: -10 points (Moderate)
- 36-55 μg/m³: -20 points (Unhealthy) 
- 56-75 μg/m³: -30 points (Very Unhealthy)
- 75+ μg/m³: -40 points (Hazardous)

**🌊 Ocean Temperature Impact (up to -20 points):**
- 18-25°C: No deduction (Normal range)
- 15-17°C or 26-28°C: -5 to -10 points (Mild deviation)
- <15°C or >25°C: -15 to -20 points (Concerning deviation)

**🎯 Final Score Ranges:**
- **80-100**: 🟢 **EXCELLENT** - Healthy planetary conditions
- **60-79**: 🟡 **GOOD** - Generally stable environment  
- **40-59**: 🟠 **MODERATE** - Some environmental stress
- **20-39**: 🔴 **POOR** - Significant environmental concerns
- **0-19**: 🚨 **CRITICAL** - Severe environmental crisis

### **🤖 Live Data Sources**
- **🔥 [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/)** - Fire Information for Resource Management System
  - **Coverage**: Global satellite fire detection via MODIS and VIIRS
  - **Updates**: Every 2 hours • **API**: [firms.modaps.eosdis.nasa.gov/api](https://firms.modaps.eosdis.nasa.gov/api/)
- **🌊 [NOAA Ocean Service](https://tidesandcurrents.noaa.gov/)** - Tides and Currents Real-Time Data
  - **Coverage**: 12 major US coastal monitoring stations 
  - **Updates**: Every 3 hours • **API**: [api.tidesandcurrents.noaa.gov](https://api.tidesandcurrents.noaa.gov/api/)
- **🌬️ [OpenAQ](https://openaq.org/)** - Open Air Quality Data Platform
  - **Coverage**: 10,000+ stations in 100+ countries worldwide
  - **Updates**: Hourly • **API**: [docs.openaq.org](https://docs.openaq.org/)
- **🆓 All Free** - No API costs, open data for environmental awareness

---

## 🔧 **Task Management System**

### **🌐 Web Interface (`/tasks`)**
- **Real-time monitoring** of all data collection tasks
- **Manual execution** - Run tasks on-demand via web interface
- **Enable/disable** tasks with toggle switches
- **View logs** - Complete execution history with stdout/stderr
- **Bulk operations** - Run all active tasks with one click
- **Auto-refresh** - Live updates every 30 seconds

### **📱 Features**
- **Status tracking** - Running, completed, failed states with visual indicators
- **Error handling** - Detailed error messages and troubleshooting
- **Performance metrics** - Duration, records processed, success rates
- **Mobile responsive** - Manage tasks from any device

---

## 🔧 **New in v2.3.0: Production Infrastructure**

### 🚀 **MAJOR UPGRADE: PostgreSQL + Railway Hosting**

**Infrastructure Changes:**
- **✅ PostgreSQL Production Database**: Migrated from SQLite to PostgreSQL for production
- **🚀 Railway Hosting**: Professional cloud hosting with auto-deployment
- **🔧 Dual Database Support**: SQLite for local development, PostgreSQL for production
- **📊 Task Management UI**: Web-based interface for monitoring data collection

**Benefits:**
- **🌍 Global Availability**: Hosted at [terrascan.io](https://terrascan.io) with 99.9% uptime
- **⚡ High Performance**: PostgreSQL with optimized queries and indexing
- **🔄 Auto Deployment**: Git push triggers automatic deployment via Railway
- **📈 Scalability**: Production-grade infrastructure ready for global usage
- **🛡️ Reliability**: Automated backups and monitoring

**Development Setup:**
- **💻 Local Development**: Supports both SQLite (zero-config) and PostgreSQL
- **🔧 Environment Detection**: Automatically uses appropriate database based on environment
- **📦 Easy Setup**: One-command database initialization for both environments

---

## 🎯 **Environmental Health Calculation Example**

**Based on Current Live Data:**

| **Factor** | **Current Value** | **Impact** | **Deduction** |
|------------|-------------------|------------|---------------|
| 🔥 **Fires** | 14,099 active fires | Extreme activity | -30 points |
| 🌬️ **Air Quality** | 75.5 μg/m³ PM2.5 | Hazardous levels | -40 points |
| 🌊 **Ocean Temp** | 18.2°C average | Normal range | 0 points |

**🧮 Calculation:** 100 - 30 (fires) - 40 (air) - 0 (ocean) = **30/100 🔴 POOR**

*This score reflects significant environmental stress from high fire activity and hazardous air pollution levels.*

---

## 🌍 **Global Coverage**

### **🔥 Fire Monitoring (NASA FIRMS)**
- **🌎 Americas**: California, Amazon rainforest, Canadian boreal forests
- **🌍 Europe/Africa**: Mediterranean, sub-Saharan Africa, Siberian forests  
- **🌏 Asia/Pacific**: Indonesia, Australia, Southeast Asian peat fires
- **📊 Data**: Fire brightness (Kelvin), confidence levels, satellite imagery
- **🕐 Real-time**: Updates every 2 hours from MODIS/VIIRS satellites

### **🌬️ Air Quality (OpenAQ)**
- **🏙️ Major Cities**: London, Delhi, Beijing, Mexico City, São Paulo, Cairo
- **🌐 Regions**: Europe (500+ stations), Asia (3000+ stations), Americas (2000+ stations)
- **📈 Pollutants**: PM2.5, PM10, NO2, SO2, O3, CO concentrations
- **🏥 Health Standards**: WHO, EPA, national air quality guidelines
- **📱 Real-time**: Hourly updates from government and research networks

### **🌊 Ocean Health (NOAA)**  
- **🇺🇸 East Coast**: Boston, New York, Virginia Beach, Charleston, Miami
- **🇺🇸 West Coast**: Seattle, San Francisco, Los Angeles, San Diego
- **🇺🇸 Gulf/Pacific**: New Orleans, Honolulu, Anchorage
- **🌡️ Climate Data**: Sea surface temperature, water levels, tidal patterns
- **⏰ Updates**: Every 3 hours from 12 primary monitoring stations

---

## 📍 **Current Geographic Coverage**

**🔥 Fire Data**: **14,099 active fire detections** globally (live data)
- Comprehensive satellite coverage of all continents
- Real-time detection from NASA MODIS/VIIRS satellites

**🌬️ Air Quality**: **1,908 monitoring stations** currently active
- **Global Coverage**: Major cities worldwide with real-time PM2.5 measurements
- **Expansion Goal**: Continue adding cities as OpenAQ network grows

**🌊 Ocean Monitoring**: **12 NOAA stations** across US coastlines
- **Pacific**: San Francisco (37.8°N), Seattle (47.6°N), Honolulu (21.3°N)
- **Atlantic**: Boston (42.3°N), New York (40.7°N), Charleston (32.8°N)
- **Gulf/Keys**: New Orleans (29.3°N), Key West (24.6°N), Galveston (29.3°N)

### **🚀 Expansion Roadmap**

**🌆 Priority Cities for Air Quality:**
- **Europe**: London, Paris, Berlin, Rome, Madrid
- **Asia**: Delhi, Beijing, Tokyo, Mumbai, Bangkok
- **Americas**: Mexico City, New York, Los Angeles, Toronto
- **Africa**: Cairo, Lagos, Johannesburg, Nairobi
- **Oceania**: Sydney, Melbourne, Auckland

**🌊 Ocean Monitoring Expansion:**
- **Global NOAA Stations**: Add Caribbean, Pacific islands
- **International Partners**: European Marine Data, Australian Bureau of Meteorology
- **New Metrics**: Coral reef health, marine biodiversity indicators

---

## 🛠️ **Tech Stack**

### **🏢 Production (Railway)**
- **Framework**: Python + Flask
- **Database**: PostgreSQL (managed)
- **Hosting**: Railway cloud platform
- **Deployment**: Git-based auto-deployment
- **Monitoring**: Built-in logging and metrics

### **💻 Development**
- **Framework**: Python + Flask
- **Database**: SQLite (default) or PostgreSQL (recommended)
- **Environment**: Local development server
- **Dependencies**: pip + requirements.txt

### **📦 Key Dependencies**
- **Flask 2.3.3** - Web framework
- **psycopg2-binary** - PostgreSQL driver
- **requests** - HTTP client for APIs
- **python-dotenv** - Environment configuration
- **python-crontab** - Task scheduling

**🎯 Design Philosophy:**
- Dual database support (SQLite for dev, PostgreSQL for prod)
- Environment auto-detection
- Zero-config local development
- Production-grade cloud deployment

---

## 🔑 **API Configuration**

**Required API Keys:**
- **NASA FIRMS**: Free registration at [firms.modaps.eosdis.nasa.gov/api](https://firms.modaps.eosdis.nasa.gov/api/)
- **OpenAQ**: Free registration at [openaq.org](https://openaq.org/)
- **NOAA Ocean Service**: No API key required (public data)

### **🏢 Production Setup (Railway)**
1. Fork this repository
2. Connect to Railway and deploy
3. Add PostgreSQL service: `railway add postgresql`
4. Set environment variables in Railway dashboard:
   - `OPENWEATHER_API_KEY`
   - `NASA_FIRMS_API_KEY` (optional)
   - `DATABASE_URL` (auto-generated)

### **💻 Local Development Setup**
1. Copy `.env.example` to `.env`
2. Add your API keys to the `.env` file
3. Start the application with `python3 run.py`

**Without API Keys:**
- Application will show clear error messages
- Existing database data will still display
- Helpful guidance on obtaining API keys

---

## 🚀 **Deployment Guide**

### **🌐 Production Deployment (Railway)**

1. **Fork Repository**
   ```bash
   # Fork the repo on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/terrascan.git
   ```

2. **Railway Setup**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and create project
   railway login
   railway init
   railway add postgresql
   ```

3. **Environment Variables**
   - Set in Railway dashboard under "Variables":
   - `OPENWEATHER_API_KEY`: Your OpenWeatherMap API key
   - `NASA_FIRMS_API_KEY`: Your NASA FIRMS API key (optional)
   - `DATABASE_URL`: Auto-generated by Railway PostgreSQL service

4. **Deploy**
   ```bash
   git push origin main  # Auto-deploys to Railway
   ```

### **💻 Local Development**

**Option 1: SQLite (Quick Start)**
```bash
pip install -r requirements.txt
cp .env.example .env
python3 run.py
```

**Option 2: PostgreSQL (Production-like)**
```bash
# Install PostgreSQL
brew install postgresql  # macOS
sudo apt install postgresql postgresql-contrib  # Ubuntu

# Create development database
createdb terrascan_dev
export DATABASE_URL="postgresql://username:password@localhost/terrascan_dev"

# Setup and run
python3 setup_production_railway.py
python3 run.py
```

---

## 🌱 **Environmental Impact**

**ECO WATCH TERRA SCAN** promotes environmental awareness by:

- 🔓 **Making Data Accessible** - Complex environmental data simplified
- 🌍 **Global Perspective** - See environmental conditions worldwide  
- 📱 **Instant Awareness** - Check planetary health as easily as weather
- 🔬 **Scientific Sources** - Trusted data from NASA, NOAA, OpenAQ
- 🆓 **Free & Open** - No paywalls, no tracking, open source
- 🚀 **Reliable Infrastructure** - Production-grade hosting ensures 24/7 availability

---

## 🤝 **Contributing**

Help make environmental data more accessible:

1. **Fork & Clone** the repository
2. **Setup Local Development** - Follow PostgreSQL setup guide above
3. **Improve the Dashboard** - Better visualizations, new indicators
4. **Add Data Sources** - More environmental monitoring APIs
5. **Test & Submit** - `python3 run.py` then pull request

**Most Wanted:**
- 🗺️ Interactive maps showing fire/pollution locations
- 📊 Historical trend indicators (24hr, 7day)
- ⚠️ Alert thresholds for dangerous conditions
- 🌐 Additional data sources (see expansion roadmap below)
- 📱 Mobile app development
- 🔔 Email/SMS alert system

### **🚀 Data Source Expansion Roadmap**

**🌡️ Climate & Weather:**
- **[ECMWF](https://www.ecmwf.int/)** - European weather forecasts and climate data
- **[Climate.gov](https://www.climate.gov/)** - NOAA climate monitoring and projections
- **[Global Temperature Anomaly](https://climate.nasa.gov/)** - NASA temperature trends

**🌿 Environmental Monitoring:**
- **[USGS Water Data](https://waterdata.usgs.gov/)** - River levels, groundwater, water quality
- **[EPA Air Quality](https://www.airnow.gov/)** - US air quality forecasts and alerts
- **[Copernicus Atmosphere](https://atmosphere.copernicus.eu/)** - European satellite atmospheric data

**🌊 Ocean & Marine:**
- **[NOAA Coral Reef Watch](https://coralreefwatch.noaa.gov/)** - Coral bleaching alerts
- **[Marine Traffic](https://www.marinetraffic.com/)** - Global shipping and ocean activity
- **[NOAA Fisheries](https://www.fisheries.noaa.gov/)** - Marine ecosystem health

**🌋 Natural Disasters:**
- **[USGS Earthquake](https://earthquake.usgs.gov/)** - Real-time seismic activity
- **[NOAA Storm Prediction](https://www.spc.noaa.gov/)** - Severe weather alerts
- **[Global Disaster Alert](https://www.gdacs.org/)** - Humanitarian disaster monitoring

---

## 📄 **License**

**MIT License** - Use ECO WATCH however you want, spread environmental awareness!

**Current Data Sources:**
- **[NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/)** - Fire detection via MODIS/VIIRS satellites
- **[NOAA Ocean Service](https://tidesandcurrents.noaa.gov/)** - Ocean temperature and water levels  
- **[OpenAQ](https://openaq.org/)** - Global air quality monitoring network

**Built by:** Stig Grindland & Claude (Anthropic)  
**Hosted on:** Railway with PostgreSQL  
**Live at:** [terrascan.io](https://terrascan.io)

---

**🌍 Keep watch on our planet. Every day. 🌍**

<!-- Railway deployment trigger: v2.3.0 - 2024-12-19 -->
