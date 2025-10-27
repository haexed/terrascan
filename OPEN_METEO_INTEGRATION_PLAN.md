# Open-Meteo Integration Plan for Terrascan Global Expansion

## Executive Summary

Open-Meteo provides a **free, open-source, no-API-key** weather and environmental data platform with **global coverage**. This is perfect for expanding Terrascan from US-focused to truly global environmental monitoring.

### Why Open-Meteo?

1. ✅ **100% Free** - No API keys, no rate limits for non-commercial use
2. ✅ **Global Coverage** - Works anywhere with lat/lng coordinates
3. ✅ **No Authentication** - Simpler than OpenWeatherMap (which needs API keys)
4. ✅ **High Resolution** - 1-25km depending on model
5. ✅ **Comprehensive Data** - Weather, air quality, climate projections
6. ✅ **Historical Data** - 80+ years of weather history
7. ✅ **Open Source** - AGPLv3 licensed, can self-host if needed

---

## Current State Analysis

### What We Have Now (US-Focused)
| Data Source | Coverage | Records | Status |
|-------------|----------|---------|--------|
| NASA FIRMS | Global | 638 | ✅ Active |
| OpenAQ | 65+ cities | 341 | ✅ Active |
| NOAA Ocean | 12 US stations | 3,729 | ✅ Active |
| OpenWeather | 24 cities | 0 | ❌ Not running |
| GBIF | 18 hotspots | 0 | ❌ Not running |

### The Problem
- **OpenWeather requires API key** and has rate limits
- **Limited station coverage** - only works where stations exist
- **No global weather** - can't show weather for arbitrary locations
- **US-centric data** - NOAA stations only in US waters

---

## Open-Meteo APIs We Should Integrate

### 1. **Air Quality API** (HIGHEST PRIORITY)
**Replace/Supplement**: OpenAQ

**What It Provides:**
- PM2.5, PM10 (particulate matter)
- NO2, SO2, CO, O3 (gases)
- European AQI and US AQI indices
- Pollen data (6 types, Europe only)

**Coverage:**
- **Global**: 25km resolution, 3-hourly data since Aug 2022
- **Europe**: 11km resolution, hourly data since Oct 2023
- **Historical**: Back to 2013 for Europe

**Endpoint:** `https://air-quality-api.open-meteo.com/v1/air-quality`

**Why It's Better:**
- ✅ Global coverage (OpenAQ only has ~65 cities)
- ✅ No API key needed (vs OpenAQ/WAQI)
- ✅ Forecast capability (7 days ahead)
- ✅ Standardized AQI indices
- ✅ Can query ANY location, not just stations

**Use Cases for Terrascan:**
- Show air quality for any region user zooms to
- Display AQI heatmap globally
- Alert on forecast poor air quality
- Track pollen levels in Europe

---

### 2. **Weather Forecast API** (HIGH PRIORITY)
**Replace**: OpenWeatherMap (which requires API key)

**What It Provides:**
- Temperature (2m, soil at multiple depths)
- Wind speed/direction
- Precipitation (rain, snow, probability)
- Humidity, pressure, cloud cover
- Solar radiation, UV index
- Weather codes (clear, cloudy, rain, snow, etc.)

**Coverage:**
- **Global**: 11km resolution
- **High-res regions**: 1-3km for Europe/North America
- **Forecast**: 7-16 days ahead
- **Update frequency**: Hourly

**Endpoint:** `https://api.open-meteo.com/v1/forecast`

**Why It's Better:**
- ✅ No API key needed (OpenWeather requires key)
- ✅ Higher resolution models
- ✅ More weather variables
- ✅ Can query any coordinate
- ✅ Free unlimited calls

**Use Cases for Terrascan:**
- Show current weather for any location
- Display temperature/precipitation forecasts
- Alert on extreme weather events
- Track global temperature patterns

---

### 3. **Historical Weather API** (MEDIUM PRIORITY)

**What It Provides:**
- 80+ years of hourly weather data (1940-present)
- Same variables as forecast API
- Can query any date range

**Coverage:**
- **Global**: 10km resolution
- **Recent data**: 1km resolution
- **Time range**: 1940 to present

**Endpoint:** `https://archive-api.open-meteo.com/v1/archive`

**Use Cases for Terrascan:**
- Show historical trends for a region
- Compare current vs historical averages
- Generate climate baseline reports
- Track temperature changes over decades

---

### 4. **Climate Change API** (MEDIUM PRIORITY)

**What It Provides:**
- Climate projections 1950-2050
- 7 different climate models
- Daily temperature extremes
- Precipitation patterns
- Drought frequency
- Heat wave analysis

**Coverage:**
- **Global**: 10km downscaled resolution
- **Models**: CMCC, FGOALS, MRI-AGCM, etc.
- **Scenarios**: Different emission scenarios

**Use Cases for Terrascan:**
- Show future climate projections
- Display vulnerability maps
- Track "days above 30°C" trends
- Predict drought-prone regions

---

### 5. **Marine Weather API** (LOW PRIORITY for now)

**What It Provides:**
- Wave height, direction, period
- Ocean currents
- Sea surface temperature

**Coverage:**
- **Global oceans**: ~5km resolution

**Could Replace**: Partially supplement NOAA ocean data

**Use Cases:**
- Show wave conditions
- Track ocean surface temperature globally
- Marine navigation information

---

## Implementation Phases

### Phase 1: Core Global Weather (Week 1-2)
**Goal**: Replace OpenWeather with Open-Meteo, enable global weather

**Tasks:**
1. ✅ Create `tasks/fetch_openmeteo_weather.py`
   - Query weather for key global cities
   - Store temperature, humidity, wind, pressure
   - Update every 1 hour

2. ✅ Create `tasks/fetch_openmeteo_air_quality.py`
   - Query air quality for global cities
   - Store PM2.5, PM10, AQI
   - Supplement OpenAQ data
   - Update every 3 hours

3. ✅ Update database schema
   - Add `open_meteo_weather` provider
   - Add `open_meteo_air` provider
   - Store forecasts (not just current)

4. ✅ Update UI
   - Display Open-Meteo data on dashboard
   - Show global coverage map
   - Add forecast capability

**Deliverable**: Global weather and air quality with no API keys needed

---

### Phase 2: Regional Scanning Enhancement (Week 3)
**Goal**: Use Open-Meteo for regional zoom-in data

**Tasks:**
1. ✅ Enhance regional scanner
   - When user zooms to any region, fetch Open-Meteo data
   - Get current weather + 7-day forecast
   - Get air quality + forecast
   - Cache results

2. ✅ Smart data merging
   - Use OpenAQ where available (higher precision)
   - Fall back to Open-Meteo for coverage
   - Prioritize station data over model data

3. ✅ UI improvements
   - Show weather forecast in region view
   - Display AQI forecast
   - Add weather alerts

**Deliverable**: Weather/AQ data for ANY region user explores

---

### Phase 3: Historical Analysis (Week 4)
**Goal**: Add historical comparison and trends

**Tasks:**
1. ✅ Create `tasks/fetch_openmeteo_historical.py`
   - Fetch historical averages for monitored regions
   - Store 30-year climate normals
   - Update monthly

2. ✅ Add trend analysis
   - Compare current vs historical
   - Show "X degrees above normal"
   - Track anomalies

3. ✅ UI: Historical comparison view
   - Show temperature trends over time
   - Display precipitation anomalies
   - Climate baseline charts

**Deliverable**: Historical context for current conditions

---

### Phase 4: Climate Projections (Optional, Week 5+)
**Goal**: Add future climate scenario visualization

**Tasks:**
1. ✅ Integrate Climate Change API
   - Fetch projections for key regions
   - Store multiple model scenarios
   - Update quarterly

2. ✅ UI: Climate future view
   - Show 2030/2050 projections
   - Display heat wave frequency
   - Drought risk maps

**Deliverable**: Future climate risk assessment

---

## Technical Implementation Details

### API Integration Pattern

```python
# tasks/fetch_openmeteo_weather.py
import requests
from datetime import datetime
from database.db import execute_insert

def fetch_weather_for_city(lat, lon, city_name):
    """Fetch current weather from Open-Meteo"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': lat,
        'longitude': lon,
        'current': 'temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,pressure_msl',
        'timezone': 'auto',
        'forecast_days': 1
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Store in database
    timestamp = datetime.utcnow()

    # Temperature
    execute_insert("""
        INSERT INTO metric_data
        (provider_key, metric_name, value, location_lat, location_lng,
         timestamp, metadata)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
    """, (
        'open_meteo_weather',
        'temperature',
        data['current']['temperature_2m'],
        lat, lon,
        timestamp,
        json.dumps({'city': city_name, 'source': 'open-meteo'})
    ))

    # Similar for humidity, wind, pressure...
```

### Global Cities List

Start with ~100 major cities globally:
```python
GLOBAL_CITIES = [
    # Europe
    {"name": "London", "lat": 51.5074, "lon": -0.1278, "country": "UK"},
    {"name": "Paris", "lat": 48.8566, "lon": 2.3522, "country": "France"},
    {"name": "Berlin", "lat": 52.5200, "lon": 13.4050, "country": "Germany"},

    # Asia
    {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503, "country": "Japan"},
    {"name": "Beijing", "lat": 39.9042, "lon": 116.4074, "country": "China"},
    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777, "country": "India"},
    {"name": "Singapore", "lat": 1.3521, "lon": 103.8198, "country": "Singapore"},

    # Americas
    {"name": "New York", "lat": 40.7128, "lon": -74.0060, "country": "USA"},
    {"name": "São Paulo", "lat": -23.5505, "lon": -46.6333, "country": "Brazil"},
    {"name": "Mexico City", "lat": 19.4326, "lon": -99.1332, "country": "Mexico"},

    # Africa
    {"name": "Cairo", "lat": 30.0444, "lon": 31.2357, "country": "Egypt"},
    {"name": "Lagos", "lat": 6.5244, "lon": 3.3792, "country": "Nigeria"},
    {"name": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "country": "South Africa"},

    # Oceania
    {"name": "Sydney", "lat": -33.8688, "lon": 151.2093, "country": "Australia"},
    {"name": "Auckland", "lat": -36.8485, "lon": 174.7633, "country": "New Zealand"},

    # ... expand to ~100 cities
]
```

---

## Database Schema Updates

### New Provider Keys
```sql
-- Add to valid provider keys
'open_meteo_weather'   -- Weather data
'open_meteo_air'       -- Air quality data
'open_meteo_historical' -- Historical climate
'open_meteo_climate'   -- Climate projections
```

### New Metric Names
```sql
-- Weather metrics
'temperature'          -- °C
'humidity'             -- %
'wind_speed'           -- km/h
'pressure'             -- hPa
'precipitation'        -- mm
'cloud_cover'          -- %
'uv_index'             -- 0-11

-- Air quality metrics (already have pm25)
'pm10'                 -- μg/m³
'no2'                  -- μg/m³
'so2'                  -- μg/m³
'co'                   -- μg/m³
'o3'                   -- μg/m³
'aqi_us'               -- 0-500 (US AQI)
'aqi_eu'               -- 0-100+ (European AQI)
```

---

## Cost & Rate Limit Analysis

### Open-Meteo vs Current Sources

| Source | Cost | Rate Limit | Coverage |
|--------|------|------------|----------|
| **Open-Meteo** | FREE | Unlimited* | Global |
| OpenWeather | FREE tier: 1k calls/day | 60 calls/min | Global but needs key |
| OpenAQ | FREE | ~10k calls/day | 65+ cities only |
| WAQI | FREE tier: 1k calls/day | - | Limited stations |
| NASA FIRMS | FREE | Unlimited | Global |

\* *For non-commercial use; self-hostable for commercial*

**Winner**: Open-Meteo is clearly superior for non-commercial use

---

## Migration Strategy

### Option A: Full Replacement (Recommended)
- Remove OpenWeather dependency entirely
- Use Open-Meteo for all weather data
- Keep OpenAQ as supplementary high-precision source
- **Advantage**: Simpler, no API keys, better coverage
- **Risk**: Lower - Open-Meteo is well-established

### Option B: Hybrid Approach
- Keep OpenWeather for cities where we have API quota
- Use Open-Meteo for additional global coverage
- **Advantage**: Redundancy
- **Risk**: More complexity, still need API key management

**Recommendation**: Option A (Full Replacement)

---

## UI/UX Improvements for Global View

### 1. Global Map Enhancements
```javascript
// Show weather layer on map
map.addLayer(weatherLayer);  // Temperature heatmap
map.addLayer(aqiLayer);      // AQI heatmap
map.addLayer(precipLayer);   // Precipitation forecast
```

### 2. City Selection
- Add dropdown: "Select Major City"
- Auto-zoom to selected city
- Show detailed weather + AQ data
- Display 7-day forecast

### 3. Regional Weather Widget
When user zooms to any region:
```
┌─────────────────────────────────┐
│ 🌍 Munich, Germany              │
│ 🌡️ 18°C | 🌬️ PM2.5: 12 μg/m³   │
│                                 │
│ 7-Day Forecast:                 │
│ Mon: ☀️ 22°C | AQI: Good        │
│ Tue: ⛅ 20°C | AQI: Good        │
│ Wed: 🌧️ 16°C | AQI: Moderate   │
└─────────────────────────────────┘
```

### 4. Comparison View
```
Current vs Historical Average:
Temperature: 22°C (+3.5°C above normal)
Precipitation: 45mm (-12mm below normal)
```

---

## Success Metrics

### Phase 1 Success Criteria
- ✅ 100+ global cities monitored
- ✅ Weather data refreshing hourly
- ✅ Air quality data refreshing every 3 hours
- ✅ No API key errors
- ✅ Global coverage visible on map
- ✅ Response time < 2 seconds

### Phase 2 Success Criteria
- ✅ Any region shows weather on zoom
- ✅ 7-day forecast available
- ✅ AQI forecast displayed
- ✅ Smart data source merging working

### Long-term Goals
- 📊 10,000+ locations monitored globally
- 🌍 True "any location" capability
- 📈 Historical trend analysis
- 🔮 Climate projection visualization
- 🚀 Sub-second global queries

---

## Timeline

| Phase | Duration | Start | Deliverable |
|-------|----------|-------|-------------|
| Phase 1: Core Integration | 2 weeks | Week 1 | Global weather + AQ |
| Phase 2: Regional Enhancement | 1 week | Week 3 | Zoom-to-region data |
| Phase 3: Historical | 1 week | Week 4 | Trend analysis |
| Phase 4: Climate (Optional) | 2+ weeks | Week 5+ | Future projections |

**Total**: 4-6 weeks for full global capability

---

## Next Steps

### Immediate Actions (This Week)

1. **Create Open-Meteo task files**
   ```bash
   tasks/fetch_openmeteo_weather.py
   tasks/fetch_openmeteo_air_quality.py
   ```

2. **Test API endpoints**
   - Verify data quality
   - Check response times
   - Test global coverage

3. **Update database**
   - Add new provider keys
   - Create metadata schema
   - Test data insertion

4. **Create global cities list**
   - Compile ~100 major cities
   - Balance geographic coverage
   - Include different climate zones

### Questions to Resolve

1. **How many cities should we start with?**
   - Recommendation: Start with 50-100, expand based on usage

2. **Update frequency?**
   - Weather: Every 1 hour (matches model updates)
   - Air quality: Every 3 hours (model frequency)

3. **Should we store forecasts or just current?**
   - Recommendation: Store 7-day forecast for trending

4. **Keep OpenWeather or remove completely?**
   - Recommendation: Remove, use Open-Meteo exclusively

---

## Conclusion

Open-Meteo is the **perfect solution** for Terrascan's global expansion:

✅ **Zero cost** - No API keys, unlimited calls
✅ **Global coverage** - Works anywhere with coordinates
✅ **Comprehensive** - Weather + Air Quality + Climate
✅ **Well-documented** - Excellent API docs
✅ **Reliable** - Used by major organizations
✅ **Open source** - Can self-host if needed

**This integration will transform Terrascan from US-focused to truly global environmental monitoring platform.**

---

## References

- Open-Meteo Homepage: https://open-meteo.com/
- Weather API Docs: https://open-meteo.com/en/docs
- Air Quality API: https://open-meteo.com/en/docs/air-quality-api
- Climate API: https://open-meteo.com/en/docs/climate-api
- GitHub: https://github.com/open-meteo/open-meteo
