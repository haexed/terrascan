# 🌍 ECO WATCH TERRA SCAN

**Real-time environmental health dashboard showing what's happening to our planet right now.**

**🎯 Know your planet's pulse - fires, air quality, ocean temps - all in one view**

---

## 🌱 **Mission: Environmental Awareness Now**

**ECO WATCH TERRA SCAN** gives you instant access to current environmental conditions across the globe:

- 🔥 **Active Fires** - Live fire detection from NASA satellites
- 🌬️ **Air Quality** - Real-time pollution levels in major cities  
- 🌊 **Ocean Health** - Current water temperature and levels from NOAA
- 🌍 **Environmental Score** - Overall planetary health indicator

**Philosophy**: Real data only. Either it works with live APIs, or shows clear guidance on what's needed.

---

## 🚀 **Quick Start**

```bash
git clone https://github.com/haexed/terrascan.git
cd terrascan

# Install dependencies
pip install -r requirements.txt

# Configure API keys (copy .env.example to .env)
cp .env.example .env
# Edit .env with your API keys

# Start the dashboard
python3 run.py

# Visit: http://localhost:5000
```

**🔑 API Keys Required**: ECO WATCH works with real environmental data from NASA, NOAA, and OpenAQ APIs.

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

## 🔧 **New in v2.2.0: Real Data Only**

### 🚀 **MAJOR REFACTOR: Simulation Mode Removed**

**Breaking Changes:**
- **❌ Removed Simulation Mode**: Eliminated all simulation/mock data functionality
- **✅ Real Data Only**: System now works with live APIs or fails gracefully with clear error messages
- **🔧 Simplified Configuration**: No more simulation_mode settings or complex fallback logic

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

**Simple & Reliable:**
- **Python + Flask** - Lightweight web framework
- **SQLite** - Zero-config database
- **Free APIs** - NASA, NOAA, OpenAQ (no costs!)
- **Responsive Design** - Works on all devices

**No Complexity:**
- No Docker required
- No cloud services needed
- No simulation modes
- Real data or clear error messages

---

## 🔑 **API Configuration**

**Required API Keys:**
- **NASA FIRMS**: Free registration at [firms.modaps.eosdis.nasa.gov/api](https://firms.modaps.eosdis.nasa.gov/api/)
- **OpenAQ**: Free registration at [openaq.org](https://openaq.org/)
- **NOAA Ocean Service**: No API key required (public data)

**Setup:**
1. Copy `.env.example` to `.env`
2. Add your API keys to the `.env` file
3. Start the application with `python3 run.py`

**Without API Keys:**
- Application will show clear error messages
- Existing database data will still display
- Helpful guidance on obtaining API keys

---

## 🌱 **Environmental Impact**

**ECO WATCH TERRA SCAN** promotes environmental awareness by:

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

**Built by:** Stig Grindland & Claude (Anthropic)

---

**🌍 Keep watch on our planet. Every day. 🌍**

<!-- Railway deployment trigger: v2.2.2 - 2024-12-19 -->
