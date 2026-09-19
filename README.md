# Terrascan

Monitor Earth's environmental health in real-time — [terrascan.io](https://terrascan.io)

![Database](https://img.shields.io/badge/database-PostgreSQL-green)
![License](https://img.shields.io/badge/license-MIT-blue)

Terrascan collects and displays current environmental conditions across the globe:

- 🔥 **Active wildfires** — live fire detection from NASA satellites
- 🌬️ **Air quality** — pollution levels from global monitoring stations
- 🌊 **Ocean health** — sea surface temperature, waves and currents
- 🌌 **Aurora** — forecast and geomagnetic activity
- 🦋 **Biodiversity** — species observations from 18 hotspots
- ⚔️ **Conflicts** — georeferenced armed conflict events
- **Health score** — combined environmental indicator (0-100)

Metrics are NULL when a source has no data; the UI shows "No data" rather than a zero.

---

## Quick start

```bash
git clone https://github.com/haexed/terrascan.git
cd terrascan
pip install -r requirements.txt
cp .env.example .env     # add DATABASE_URL and any API keys
python run.py            # http://localhost:5000
```

PostgreSQL is required for both development and production. To set up a local database:

```bash
sudo -u postgres psql -c "CREATE DATABASE terrascan_dev;"
sudo -u postgres psql -c "CREATE USER terrascan_user WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE terrascan_dev TO terrascan_user;"

echo 'DATABASE_URL=postgresql://terrascan_user:your_secure_password@localhost/terrascan_dev' >> .env

python3 setup_production_railway.py   # creates the schema
```

The live schema is documented at `/system/schema`.

### API keys

| Provider | Key | Free tier | Sign up |
|----------|-----|-----------|---------|
| 🔥 NASA FIRMS | Required | 5,000 transactions/10 min | [firms.modaps.eosdis.nasa.gov](https://firms.modaps.eosdis.nasa.gov/api/) |
| 🌬️ World AQI | Recommended | 1,000 requests/sec | [aqicn.org](https://aqicn.org/api/) |
| 🌬️ OpenAQ | Optional fallback | Limited | [openaq.org](https://openaq.org/) |
| ⚔️ UCDP | Required | 5,000/day | [ucdp.uu.se](https://ucdp.uu.se/apidocs/) (email for token) |
| 🌡️ OpenWeatherMap | Optional, set in DB config | 1,000/day | [openweathermap.org](https://openweathermap.org/api) |
| 🌊 NOAA | None needed | Unlimited | — |
| 🌌 NOAA SWPC | None needed | Unlimited | — |
| 🌐 Open-Meteo | None needed | Unlimited (CC-BY 4.0) | — |
| 🦋 GBIF | None needed | Unlimited | — |

Provider display metadata (names, icons, links, coverage, freshness thresholds) lives in the
`provider_config` table, seeded from `setup_providers.py`. Nothing else hardcodes it.

---

## Data collection

Data is collected on demand rather than on a cron schedule, which keeps costs low for a
low-traffic deployment:

- **Smart refresh** — the app detects stale data and prompts for a refresh
- **Manual refresh** — trigger collection from the `/tasks` page
- **Scan on explore** — panning the map fetches data for the viewed region

| Task | Source | Freshness TTL |
|------|--------|---------------|
| 🔥 `nasa_fires_global` | Active fire detection | 3 hours |
| 🌬️ `openaq_latest` | Air quality stations | 12 hours |
| 🌊 `noaa_ocean_temperature` | Coastal water temperature | 24 hours |
| 🌐 `openmeteo_marine` | Sea surface temperature | 24 hours |
| 🌌 `noaa_aurora` | Aurora forecast | 1 hour |
| 🦋 `gbif_species_observations` | Species observations | 168 hours |
| ⚔️ `ucdp_conflicts` | Armed conflicts (monthly candidate release) | 168 hours |
| 🌡️ `openweather_current` | Current conditions | 6 hours |

Run tasks from the command line:

```bash
python3 tasks/runner.py list
python3 tasks/runner.py run nasa_fires_global
python3 tasks/runner.py status
```

Or from `/tasks` in the web UI, which shows live logs. A task that is already running cannot
be started again.

---

## Deployment

Deployed on Railway.

```bash
railway login
railway init
railway add postgresql

railway variables set FLASK_SECRET_KEY=your_secret   # required, app won't start without it
railway variables set NASA_FIRMS_API_KEY=your_key
railway variables set WORLD_AQI_API_KEY=your_key   # or OPENAQ_API_KEY
railway variables set UCDP_API_TOKEN=your_token

railway up
```

---

## Endpoints

### Pages

| Path | Description |
|------|-------------|
| `/` | Interactive map (main view) |
| `/status` | Environmental dashboard |
| `/tasks` | Task monitoring and logs |
| `/system` | System status and data providers |
| `/system/schema` | Database schema |
| `/about` | Project information |

### API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/map-data` | GET | Map markers |
| `/api/providers` | GET | Provider metadata |
| `/api/freshness` | GET | Data freshness per source |
| `/api/scan-area` | POST | Fetch data for a map region |
| `/api/refresh` | POST | Run every collection task |
| `/api/smart-refresh` | POST | Run only the stale sources |
| `/api/tasks` | GET | Task list and status |
| `/api/tasks/<name>/logs` | GET | Task execution logs |
| `/api/tasks/<name>/run` | POST | Run one task |

Task control is environment-based; there is no public API for managing task definitions.

---

## Contributing

Fork, branch, and open a pull request:

```bash
git clone https://github.com/your-username/terrascan.git
cd terrascan
git checkout -b feature/your-feature-name
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Useful areas: additional environmental data sources, visualizations, tests, mobile layout,
and documentation.

---

## Credits

Built by [Stig Grindland](https://hæx.com) with Claude (Anthropic).

## License

MIT — see [LICENSE](LICENSE).

## Links

- [Live site](https://terrascan.io)
- [Source](https://github.com/haexed/terrascan)
- [Issues](https://github.com/haexed/terrascan/issues)
- [Discussions](https://github.com/haexed/terrascan/discussions)
