# 🌍 TERRASCAN

**Real-time environmental health dashboard showing what's happening to our planet right now.**

**🎯 Know your planet's pulse - fires, air quality, ocean temps - all in one view**

---

## 🌱 **Mission: Environmental Awareness Now**

**TERRASCAN** gives you instant access to current environmental conditions across the globe:

- 🔥 **Active Fires** - Live fire detection from NASA satellites
- 🌬️ **Air Quality** - Real-time pollution levels in major cities  
- 🌊 **Ocean Health** - Current water temperature and levels from NOAA
- 🌍 **Environmental Score** - Overall planetary health indicator

**Philosophy**: Keep it simple, keep it current, keep it accessible to everyone.

---

## 🚀 **Quick Start**

```bash
git clone https://github.com/haexed/terrascan.git
cd terrascan

# Install dependencies  
pip install -r requirements.txt

# Start the dashboard
python3 run.py

# Visit: http://localhost:5000
```

**That's it!** TERRASCAN works immediately with live data feeds.

---

## ✨ **What You See**

### **🌐 Single Dashboard View**
- **🔥 Fire Alert Status** - Global active fires with brightness levels
- **🌬️ Air Quality Index** - PM2.5 levels from cities worldwide
- **🌊 Ocean Conditions** - Water temperatures from 12 US coastal stations
- **🌍 Environmental Health Score** - Combined 0-100 planetary health indicator
- **📱 Mobile-Friendly** - Check planetary health from anywhere

### **📊 Environmental Health Score (0-100)**

The **Planetary Health Score** combines three critical environmental factors into a single 0-100 indicator:

**🔥 Fire Impact (up to -30 points):**
- 0-10 fires: No deduction
- 11-50 fires: -10 points  
- 51-100 fires: -20 points
- 100+ fires: -30 points

**🌬️ Air Quality Impact (up to -40 points):**
- 0-12 μg/m³ PM2.5: No deduction (WHO Good)
- 13-25 μg/m³: -10 points (Moderate)
- 26-35 μg/m³: -20 points (Unhealthy for Sensitive)
- 36-55 μg/m³: -30 points (Unhealthy) 
- 55+ μg/m³: -40 points (Dangerous)

**🌊 Ocean Temperature Impact (up to -20 points):**
- 15-25°C: No deduction (Normal range)
- 26-28°C: -10 points (Warming trend)
- 28°C+: -20 points (Concerning heat)

**🎯 Final Score Ranges:**
- **85-100**: 🟢 **EXCELLENT** - Healthy planetary conditions
- **70-84**: 🟡 **GOOD** - Generally stable environment  
- **50-69**: 🟠 **MODERATE** - Some environmental stress
- **30-49**: 🔴 **POOR** - Significant environmental concerns
- **0-29**: 🚨 **CRITICAL** - Severe environmental crisis

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

## 🔧 **New in v2.1.3: System Page & Advanced Debugging**

### ✨ **NEW: System Status Page** (`/system`)
- **📊 Complete System Overview**: 27,000+ environmental records, active tasks, recent runs
- **🔥 NASA FIRMS Status**: Fire detection monitoring with operational health
- **🌬️ OpenAQ Status**: Air quality network (65+ cities) with provider diagnostics  
- **🌊 NOAA Ocean Status**: Ocean monitoring (12 stations) with temperature/level data
- **📈 Live Task Execution Log**: Real-time task runs with timing and record counts
- **🐛 Advanced Debugging Tools**: Ocean data diagnostics, cache detection, API testing
- **🧹 Cache-Busting Solutions**: One-click refresh for browser caching issues

### 🛠️ **Production-Ready Debugging**
- **Debug Ocean API**: `/api/debug/ocean` - Detailed ocean data analysis and validation
- **Smart Cache Detection**: Automatic detection of 0°C temperature (indicates cache issues)
- **Force Refresh Buttons**: Cache-busting with timestamp parameters on homepage and system page
- **Real-time Testing**: Live API testing with temperature validation and error reporting

## 🐛 **Recent Bug Fixes (v2.1.2-2.1.3)**

### ✅ **Critical Production Issues Resolved:**
- **🌊 Ocean Temperature "NO DATA"**: Fixed browser caching showing old 0°C values
  - **Root Cause**: Browser displaying cached version instead of live 18.3°C data
  - **Solution**: Multiple cache-busting mechanisms and user-friendly refresh options
  - **Verification**: Debug tools confirm 1,296+ temperature records with 18.3°C average
  - **Final Fix**: Enhanced cache-busting with ETag headers and client-side cache detection
- **⏰ Time Display**: Fixed "Loading..." stuck state → Real-time updates on all pages
- **📊 Data Freshness**: Ensured all environmental metrics display current values
- **🔄 Data Collection**: Enhanced ocean monitoring with both water level + temperature
- **🔧 Cache Detection**: JavaScript automatically highlights cache issues with orange borders

### 🔧 **Technical Fixes:**
- Added `noaa_ocean_temperature` task for proper sea surface temperature collection
- Fixed duplicate HTML element IDs causing JavaScript conflicts
- Enhanced refresh API to collect complete ocean health data
- Improved time update functions for consistent UI behavior
- Added comprehensive cache detection and busting mechanisms
- Built production-ready debugging infrastructure

---

## 🎯 **Environmental Health Calculation Example**

**Based on Your Current Data (Score: 30/100 🔴 POOR):**

| **Factor** | **Current Value** | **Impact** | **Deduction** |
|------------|-------------------|------------|---------------|
| 🔥 **Fires** | 807 active fires | Extreme activity | -30 points |
| 🌬️ **Air Quality** | 78.3 μg/m³ PM2.5 | Dangerous levels | -40 points |
| 🌊 **Ocean Temp** | 20.0°C average | Normal range | 0 points |

**🧮 Calculation:** 100 - 30 (fires) - 40 (air) - 0 (ocean) = **30/100 🔴 POOR**

*This score reflects significant environmental stress from high fire activity and dangerous air pollution levels.*

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

**🔥 Fire Data**: **8,005 unique fire locations** globally (last 7 days)
- Comprehensive satellite coverage of all continents
- Real-time detection from NASA MODIS/VIIRS satellites

**🌬️ Air Quality**: **126 monitoring stations** currently active
- **Primary Coverage**: São Paulo, Brazil metropolitan area
- **Expansion Goal**: Add major cities worldwide (London, Delhi, Beijing, etc.)

**🌊 Ocean Monitoring**: **12 NOAA stations** across US coastlines
- **Pacific**: San Francisco (37.8°N), Seattle (47.6°N), Honolulu (21.3°N), Ketchikan (55.3°N)
- **Atlantic**: Boston (42.3°N), New York (40.7°N), Virginia Beach (36.8°N), Charleston (29.2°N)
- **Gulf/Keys**: New Orleans (29.3°N), Key West (24.6°N), Galveston (26.1°N)

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

**Simple & Reliable:**
- **Python + Flask** - Lightweight web framework
- **SQLite** - Zero-config database
- **Free APIs** - NASA, NOAA, OpenAQ (no costs!)
- **Responsive Design** - Works on all devices

**No Complexity:**
- No Docker required
- No cloud services needed
- No configuration files
- Works offline with cached data

---

## 🌱 **Environmental Impact**

**TERRASCAN** promotes environmental awareness by:

- 🔓 **Making Data Accessible** - Complex environmental data simplified
- 🌍 **Global Perspective** - See environmental conditions worldwide  
- 📱 **Instant Awareness** - Check planetary health as easily as weather
- 🔬 **Scientific Sources** - Trusted data from NASA, NOAA, OpenAQ
- 🆓 **Free & Open** - No paywalls, no tracking, open source

---

## 🤝 **Contributing**

Help make environmental data more accessible:

1. **Fork & Clone** the repository
2. **Improve the Dashboard** - Better visualizations, new indicators
3. **Add Data Sources** - More environmental monitoring APIs
4. **Test & Submit** - `python3 run.py` then pull request

**Most Wanted:**
- 🗺️ Interactive maps showing fire/pollution locations
- 📊 Historical trend indicators (24hr, 7day)
- ⚠️ Alert thresholds for dangerous conditions
- 🌐 Additional data sources (see expansion roadmap below)

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

**Planned Integrations:**
- **[USGS Water Data](https://waterdata.usgs.gov/)** - River levels and groundwater
- **[EPA AirNow](https://www.airnow.gov/)** - US air quality forecasts
- **[Climate.gov](https://www.climate.gov/)** - Climate monitoring and projections
- **[ECMWF](https://www.ecmwf.int/)** - European weather and climate data

**Built by:** Stig Grindland & Claude (Anthropic)

---

**🌍 Keep watch on our planet. Every day. 🌍**
