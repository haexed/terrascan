# 🔧 TERRASCAN Development Guide

This guide helps you set up TERRASCAN for local development using PostgreSQL.

## 🚀 Quick Start

```bash
# 1. Clone and install
git clone https://github.com/haexed/terrascan.git
cd terrascan
pip install -r requirements.txt

# 2. Set up PostgreSQL (see detailed setup below)
# Create database: terrascan_dev
# Create user: terrascan_user

# 3. Configure environment
cp .env.example .env
export DATABASE_URL="postgresql://terrascan_user:your_password@localhost/terrascan_dev"

# 4. Initialize database schema
python3 setup_production_railway.py

# 5. Start development server
python3 run.py
```

## 🗄️ Detailed PostgreSQL Setup

TERRASCAN uses PostgreSQL for both development and production environments.

### 1. Install PostgreSQL

**macOS (Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Windows:**
- Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- Run installer and follow setup wizard

### 2. Create Development Database

```bash
# Connect to PostgreSQL as superuser
sudo -u postgres psql

# Create database and user
CREATE DATABASE terrascan_dev;
CREATE USER terrascan_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE terrascan_dev TO terrascan_user;

# Exit PostgreSQL
\q
```

### 3. Configure Environment

```bash
# Set database URL for PostgreSQL
export DATABASE_URL="postgresql://terrascan_user:your_secure_password@localhost/terrascan_dev"

# Or add to your .env file
echo 'DATABASE_URL=postgresql://terrascan_user:your_secure_password@localhost/terrascan_dev' >> .env
```

### 4. Initialize Database Schema

```bash
# Run the production setup script to create tables
python3 setup_production_railway.py
```

### 5. Start Development Server

```bash
python3 run.py
```

## 🔄 Database Configuration

TERRASCAN requires PostgreSQL for both development and production. The `DATABASE_URL` environment variable must be set to connect to your PostgreSQL database.

## 🧪 Testing API Integrations

### Required API Keys

Get these free API keys for full functionality:

1. **NASA FIRMS API Key**
   - Register at: https://firms.modaps.eosdis.nasa.gov/api/
   - Add to `.env`: `NASA_FIRMS_API_KEY=your_key_here`

2. **OpenAQ API Key** 
   - Register at: https://openaq.org/
   - Add to `.env`: `OPENAQ_API_KEY=your_key_here`

3. **OpenWeatherMap API Key**
   - Register at: https://openweathermap.org/api
   - Add to `.env`: `OPENWEATHER_API_KEY=your_key_here`

### Testing Tasks

Access the task management interface at: http://localhost:5000/tasks

- **Run individual tasks** manually to test API integrations
- **View logs** to debug any issues
- **Monitor performance** and data collection rates

## 📂 Project Structure

```
terrascan/
├── database/              # Database connection and schema
│   ├── db.py             # PostgreSQL database module
│   └── config_manager.py # Configuration management
├── tasks/                # Data collection tasks
│   ├── fetch_nasa_fires.py
│   ├── fetch_openaq_latest.py
│   ├── fetch_noaa_ocean.py
│   ├── fetch_openweathermap_weather.py
│   ├── fetch_gbif_biodiversity.py
│   ├── runner.py
│   └── __init__.py
├── web/                  # Flask web application
│   ├── app.py           # Main application
│   ├── static/          # CSS, JS, images
│   └── templates/       # HTML templates
├── setup_production_railway.py  # Database schema setup
├── requirements.txt      # Python dependencies
└── run.py               # Application entry point
```

## 🔧 Development Tasks

### Database Management

**View current database:**
```bash
# Check database connection details
python3 -c "from database.db import get_database_info; print(get_database_info())"
```

**Reset PostgreSQL database:**
```bash
# Drop and recreate database
sudo -u postgres psql -c "DROP DATABASE IF EXISTS terrascan_dev;"
sudo -u postgres psql -c "CREATE DATABASE terrascan_dev;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE terrascan_dev TO terrascan_user;"
python3 setup_production_railway.py
```

### Running Tasks

**Manual task execution:**
```bash
# Run specific task
python3 tasks/runner.py run nasa_fires_global

# Check task status
python3 tasks/runner.py status

# List all tasks
python3 tasks/runner.py list
```

**Web interface:**
- Visit: http://localhost:5000/tasks
- Monitor real-time task execution
- View detailed logs and error messages

## 🐛 Common Issues

### Database Connection Errors

**PostgreSQL connection failed:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS

# Check if database exists
sudo -u postgres psql -l | grep terrascan_dev
```

**Permission denied:**
```bash
# Make sure user has correct permissions
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE terrascan_dev TO terrascan_user;"
```

### API Integration Issues

**API key not working:**
- Verify key is correct in `.env` file
- Check API provider documentation for rate limits
- Test API key directly with curl/browser

**Rate limiting:**
- NASA FIRMS: 1000 requests/hour
- OpenAQ: 10,000 requests/month (free tier)
- OpenWeatherMap: 1000 requests/day (free tier)

### Performance Issues

**Slow data loading:**
- Check database indexing (automatically created)
- Monitor API response times
- Use PostgreSQL for better performance with large datasets

## 🚀 Deployment Testing

To test your changes work in a production-like environment:

1. **Set up PostgreSQL locally** (follow setup above)
2. **Test with real API keys** (not simulation mode)
3. **Run all tasks** via web interface
4. **Check system status** at `/system`
5. **Verify data collection** in dashboard

## 🤝 Contributing

1. **Setup development environment** with PostgreSQL
2. **Create feature branch** from `main`
3. **Test thoroughly** with real API integrations
4. **Update documentation** if needed
5. **Submit pull request** with clear description

### Code Style

- Follow PEP 8 Python style guide
- Use type hints for function parameters
- Add docstrings to functions
- Comment complex logic
- Use descriptive variable names

### Testing Checklist

- [ ] Application starts without errors
- [ ] Database schema creates successfully
- [ ] All API integrations work with real keys
- [ ] Tasks can be run manually and via web interface
- [ ] Data appears correctly in dashboard
- [ ] No console errors in browser
- [ ] Mobile responsive design works

---

**Need help?** Check the main [README.md](README.md) or open an issue on GitHub. 
