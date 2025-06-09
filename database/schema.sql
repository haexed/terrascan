-- Terrascan Python SQLite Schema
-- Task system with normalized tables

-- Task definitions (what to run)
CREATE TABLE task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    
    task_type TEXT NOT NULL,           -- 'fetch_data', 'process_data', 'cleanup'
    command TEXT NOT NULL,             -- Python function/script to run
    cron_schedule TEXT,                -- '0 * * * *' or 'on_demand' 
    
    provider TEXT,                     -- 'nasa_fires', 'noaa_ocean'
    dataset TEXT,                      -- 'active_fires', 'sea_temp'
    parameters TEXT,                   -- JSON string with default parameters
    
    cost_estimate_cents INTEGER DEFAULT 0,  -- Expected cost per run
    timeout_seconds INTEGER DEFAULT 300,    -- Max execution time
    
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Task execution history (what happened when we ran tasks)
CREATE TABLE task_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    
    status TEXT NOT NULL,              -- 'running', 'completed', 'failed', 'timeout'
    exit_code INTEGER,                 -- 0=success, 1=error, etc.
    
    stdout TEXT,                       -- Command output
    stderr TEXT,                       -- Error output  
    error_details TEXT,                -- Stack trace if failed
    
    actual_cost_cents INTEGER DEFAULT 0,   -- Real cost after completion
    records_processed INTEGER DEFAULT 0,   -- How much data was fetched/processed
    
    triggered_by TEXT,                 -- 'cron', 'user_request', 'manual'
    trigger_parameters TEXT,           -- JSON with override parameters for this run
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Providers (data sources we can fetch from)
CREATE TABLE provider (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,          -- 'nasa_firms', 'openaq'
    name TEXT NOT NULL,                -- 'NASA FIRMS', 'OpenAQ'
    description TEXT,
    base_url TEXT,
    api_key_required BOOLEAN DEFAULT 0,
    cost_per_request_cents INTEGER DEFAULT 0,
    rate_limit_per_hour INTEGER,
    documentation_url TEXT,
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Environmental metrics (the actual data we collect)
CREATE TABLE metric_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL,
    provider_key TEXT NOT NULL,
    dataset TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    value REAL,
    unit TEXT,
    location_lat REAL,
    location_lng REAL,
    metadata TEXT,                     -- JSON with additional context
    confidence REAL DEFAULT 1.0,
    task_log_id INTEGER REFERENCES task_log(id),  -- Which task run collected this
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Public cost tracking for transparency
CREATE TABLE cost_summary (
    date DATE PRIMARY KEY,
    total_cost_cents INTEGER DEFAULT 0,
    total_requests INTEGER DEFAULT 0,
    total_records INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_task_log_status ON task_log(status);
CREATE INDEX idx_task_log_task_id ON task_log(task_id);
CREATE INDEX idx_task_log_started_at ON task_log(started_at);
CREATE INDEX idx_metric_data_timestamp ON metric_data(timestamp);
CREATE INDEX idx_metric_data_provider ON metric_data(provider_key, dataset);
CREATE INDEX idx_metric_data_location ON metric_data(location_lat, location_lng);

-- Sample data to get started
INSERT INTO provider (key, name, description, base_url, api_key_required, cost_per_request_cents) VALUES
('nasa_firms', 'NASA FIRMS', 'Fire Information for Resource Management System', 'https://firms.modaps.eosdis.nasa.gov/api/', 1, 0),
('openaq', 'OpenAQ', 'Open air quality data platform', 'https://api.openaq.org/v2/', 0, 0),
('noaa_ocean', 'NOAA Ocean Service', 'Ocean and coastal data', 'https://tidesandcurrents.noaa.gov/api/', 0, 0);

INSERT INTO task (name, description, task_type, command, cron_schedule, provider, dataset) VALUES
('nasa_fires_global', 'Fetch global active fires from NASA FIRMS', 'fetch_data', 'tasks.fetch_nasa_fires', '0 */2 * * *', 'nasa_firms', 'active_fires'),
('openaq_latest', 'Get latest air quality measurements', 'fetch_data', 'tasks.fetch_openaq_latest', '0 * * * *', 'openaq', 'measurements'),
('noaa_ocean_water_level', 'Fetch water level data from NOAA Ocean Service', 'fetch_data', 'tasks.fetch_noaa_ocean', '0 */3 * * *', 'noaa_ocean', 'oceanographic'),
('cost_summary_daily', 'Calculate daily cost summary', 'process_data', 'tasks.calculate_daily_costs', '0 0 * * *', NULL, NULL); 
