#!/usr/bin/env python3
"""
Database connection and operations for TERRASCAN
Supports both SQLite (local) and PostgreSQL (Railway production)
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# Check if we're in production (Railway) environment
DATABASE_URL = os.environ.get('DATABASE_URL')
IS_PRODUCTION = bool(DATABASE_URL)

if IS_PRODUCTION:
    import psycopg2
    import psycopg2.extras
    print("🚀 Using PostgreSQL for production")
else:
    print("🔧 Using SQLite for local development")

def get_db_connection():
    """Get database connection based on environment"""
    if IS_PRODUCTION:
        # PostgreSQL connection for Railway
        return psycopg2.connect(DATABASE_URL)
    else:
        # SQLite connection for local development
        db_path = os.path.join(os.path.dirname(__file__), 'terrascan.db')
        print(f"📁 Using database: {db_path}")
        return sqlite3.connect(db_path)

def execute_query(query: str, params: tuple = None) -> List[Dict[str, Any]]:
    """Execute a SELECT query and return results as list of dictionaries"""
    try:
        conn = get_db_connection()
        
        if IS_PRODUCTION:
            # PostgreSQL
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query, params or ())
            results = [dict(row) for row in cursor.fetchall()]
        else:
            # SQLite
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            results = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        return results
        
    except Exception as e:
        print(f"❌ Database query error: {e}")
        print(f"Query: {query}")
        if params:
            print(f"Params: {params}")
        return []

def execute_insert(query: str, params: tuple = None) -> bool:
    """Execute an INSERT/UPDATE/DELETE query with proper transaction handling"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Convert SQLite syntax to PostgreSQL if needed
        if IS_PRODUCTION and '?' in query:
            # Replace ? placeholders with %s for PostgreSQL
            query = query.replace('?', '%s')
        
        cursor.execute(query, params or ())
        conn.commit()
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database insert error: {e}")
        print(f"Query: {query}")
        if params:
            print(f"Params: {params}")
        return False

def execute_many(query: str, params_list: List[tuple]) -> bool:
    """Execute multiple INSERT queries in a single transaction"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if IS_PRODUCTION:
            # PostgreSQL
            psycopg2.extras.execute_batch(cursor, query, params_list)
        else:
            # SQLite
            cursor.executemany(query, params_list)
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database batch insert error: {e}")
        print(f"Query: {query}")
        print(f"Batch size: {len(params_list)}")
        return False

def init_database():
    """Initialize database schema based on environment"""
    if IS_PRODUCTION:
        # For production, run the Railway setup script
        print("🚀 Production database detected - use setup_production_railway.py for initialization")
        return True
    else:
        # For local development, create SQLite schema
        return init_sqlite_database()

def init_sqlite_database():
    """Initialize SQLite database for local development"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # System configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                data_type TEXT DEFAULT 'string',
                description TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Provider configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS provider_config (
                provider TEXT,
                key TEXT,
                value TEXT,
                data_type TEXT DEFAULT 'string',
                description TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (provider, key)
            )
        """)
        
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                task_type TEXT,
                command TEXT,
                cron_schedule TEXT,
                provider TEXT,
                dataset TEXT,
                parameters TEXT,
                active BOOLEAN DEFAULT 1,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Task logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER REFERENCES task(id),
                status TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                duration_seconds REAL,
                records_processed INTEGER DEFAULT 0,
                error_message TEXT,
                triggered_by TEXT,
                trigger_parameters TEXT
            )
        """)
        
        # Main environmental data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metric_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_key TEXT,
                metric_name TEXT,
                value REAL,
                unit TEXT,
                location_lat REAL,
                location_lng REAL,
                timestamp TIMESTAMP,
                metadata TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metric_data_provider ON metric_data(provider_key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metric_data_timestamp ON metric_data(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metric_data_location ON metric_data(location_lat, location_lng)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_log_task_id ON task_log(task_id)")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ SQLite database initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ SQLite database initialization failed: {e}")
        return False

def populate_sample_data():
    """Populate sample data for local development"""
    if IS_PRODUCTION:
        # Don't populate sample data in production
        return True
    
    # Check if we already have data
    existing_data = execute_query("SELECT COUNT(*) as count FROM metric_data")
    if existing_data and existing_data[0]['count'] > 0:
        return True
    
    print("📊 Populating sample environmental data...")
    
    # Sample fire data
    sample_fires = [
        ('nasa_firms', 'fire_brightness', 350.5, 'K', 37.7749, -122.4194, datetime.now(), '{"confidence": 85, "satellite": "MODIS"}'),
        ('nasa_firms', 'fire_brightness', 425.2, 'K', 34.0522, -118.2437, datetime.now(), '{"confidence": 92, "satellite": "VIIRS"}'),
    ]
    
    # Sample air quality data
    sample_air = [
        ('openaq', 'air_quality_pm25', 15.3, 'µg/m³', 40.7128, -74.0060, datetime.now(), '{"location": "New York", "station": "NYC_Central"}'),
        ('openaq', 'air_quality_pm25', 8.7, 'µg/m³', 51.5074, -0.1278, datetime.now(), '{"location": "London", "station": "LDN_Westminster"}'),
    ]
    
    # Sample ocean data
    sample_ocean = [
        ('noaa_ocean', 'water_temperature', 18.5, '°C', 36.8485, -75.9779, datetime.now(), '{"station": "Duck Pier", "station_id": "8651370"}'),
        ('noaa_ocean', 'water_level', 1.2, 'm', 25.7617, -80.1918, datetime.now(), '{"station": "Miami Beach", "station_id": "8723214"}'),
    ]
    
    all_samples = sample_fires + sample_air + sample_ocean
    
    for provider_key, metric_name, value, unit, lat, lng, timestamp, metadata in all_samples:
        execute_insert("""
            INSERT INTO metric_data (provider_key, metric_name, value, unit, location_lat, location_lng, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (provider_key, metric_name, value, unit, lat, lng, timestamp, metadata))
    
    print(f"✅ Added {len(all_samples)} sample environmental records")
    return True

def get_database_stats():
    """Get database statistics"""
    try:
        stats = {}
        
        # Total records
        total_records = execute_query("SELECT COUNT(*) as count FROM metric_data")
        stats['total_records'] = total_records[0]['count'] if total_records else 0
        
        # Records by provider
        provider_stats = execute_query("""
            SELECT provider_key, COUNT(*) as count 
            FROM metric_data 
            GROUP BY provider_key 
            ORDER BY count DESC
        """)
        stats['by_provider'] = {row['provider_key']: row['count'] for row in provider_stats}
        
        # Recent records (last 24 hours)
        if IS_PRODUCTION:
            recent_query = "SELECT COUNT(*) as count FROM metric_data WHERE created_date >= NOW() - INTERVAL '24 hours'"
        else:
            recent_query = "SELECT COUNT(*) as count FROM metric_data WHERE created_date >= datetime('now', '-24 hours')"
        
        recent_records = execute_query(recent_query)
        stats['recent_records'] = recent_records[0]['count'] if recent_records else 0
        
        # Database type
        stats['database_type'] = 'PostgreSQL' if IS_PRODUCTION else 'SQLite'
        stats['is_production'] = IS_PRODUCTION
        
        return stats
        
    except Exception as e:
        print(f"❌ Error getting database stats: {e}")
        return {
            'total_records': 0,
            'by_provider': {},
            'recent_records': 0,
            'database_type': 'Unknown',
            'is_production': IS_PRODUCTION,
            'error': str(e)
        }

# Backward compatibility functions
def store_metric_data(timestamp: str, provider_key: str, dataset: str, 
                     metric_name: str, value: float, unit: str = None,
                     location_lat: float = None, location_lng: float = None,
                     metadata: dict = None, task_log_id: int = None) -> bool:
    """Store environmental metric data (backward compatibility function)"""
    try:
        metadata_json = json.dumps(metadata) if metadata else None
        
        if IS_PRODUCTION:
            # PostgreSQL query
            query = """
                INSERT INTO metric_data 
                (provider_key, metric_name, value, unit, location_lat, location_lng, timestamp, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
        else:
            # SQLite query
            query = """
                INSERT INTO metric_data 
                (provider_key, metric_name, value, unit, location_lat, location_lng, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
        
        return execute_insert(query, (provider_key, metric_name, value, unit, 
                                    location_lat, location_lng, timestamp, metadata_json))
        
    except Exception as e:
        print(f"❌ Error storing metric data: {e}")
        return False

def get_tasks(active_only: bool = True) -> List[Dict[str, Any]]:
    """Get all tasks, optionally filtered by active status"""
    try:
        query = "SELECT * FROM task"
        if active_only:
            query += " WHERE active = true" if IS_PRODUCTION else " WHERE active = 1"
        query += " ORDER BY created_date DESC"
        
        return execute_query(query)
    except Exception as e:
        print(f"❌ Error getting tasks: {e}")
        return []

def get_task_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get a specific task by name"""
    try:
        if IS_PRODUCTION:
            query = "SELECT * FROM task WHERE name = %s"
        else:
            query = "SELECT * FROM task WHERE name = ?"
        
        results = execute_query(query, (name,))
        return results[0] if results else None
    except Exception as e:
        print(f"❌ Error getting task by name: {e}")
        return None

def start_task_run(task_id: int, triggered_by: str = 'manual', 
                   trigger_parameters: dict = None) -> Optional[int]:
    """Create a new task run record in 'running' status"""
    try:
        params_json = json.dumps(trigger_parameters) if trigger_parameters else None
        
        if IS_PRODUCTION:
            query = """
                INSERT INTO task_log (task_id, status, started_at, triggered_by, trigger_parameters) 
                VALUES (%s, %s, NOW(), %s, %s) RETURNING id
            """
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query, (task_id, 'running', triggered_by, params_json))
            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            return result[0] if result else None
        else:
            query = """
                INSERT INTO task_log (task_id, status, started_at, triggered_by, trigger_parameters) 
                VALUES (?, 'running', CURRENT_TIMESTAMP, ?, ?)
            """
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query, (task_id, triggered_by, params_json))
            lastrowid = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            return lastrowid
            
    except Exception as e:
        print(f"❌ Error starting task run: {e}")
        return None

def complete_task_run(run_id: int, exit_code: int, stdout: str = None, 
                     stderr: str = None, error_details: str = None, 
                     actual_cost_cents: int = 0, records_processed: int = 0):
    """Mark a task run as completed with results"""
    try:
        status = 'completed' if exit_code == 0 else 'failed'
        
        if IS_PRODUCTION:
            # Calculate duration using PostgreSQL
            query = """
                UPDATE task_log SET 
                completed_at = NOW(),
                duration_seconds = EXTRACT(EPOCH FROM (NOW() - started_at)),
                status = %s,
                records_processed = %s,
                error_message = %s
                WHERE id = %s
            """
            params = (status, records_processed, error_details, run_id)
        else:
            # Calculate duration using SQLite
            query = """
                UPDATE task_log SET 
                completed_at = CURRENT_TIMESTAMP,
                duration_seconds = (julianday(CURRENT_TIMESTAMP) - julianday(started_at)) * 86400,
                status = ?,
                records_processed = ?,
                error_message = ?
                WHERE id = ?
            """
            params = (status, records_processed, error_details, run_id)
        
        return execute_insert(query, params)
        
    except Exception as e:
        print(f"❌ Error completing task run: {e}")
        return False

def get_recent_task_runs(limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent task runs with task information"""
    try:
        query = """
            SELECT tl.*, t.name as task_name, t.description as task_description
            FROM task_log tl 
            JOIN task t ON tl.task_id = t.id 
            ORDER BY tl.started_at DESC 
            LIMIT %s
        """ if IS_PRODUCTION else """
            SELECT tl.*, t.name as task_name, t.description as task_description
            FROM task_log tl 
            JOIN task t ON tl.task_id = t.id 
            ORDER BY tl.started_at DESC 
            LIMIT ?
        """
        
        return execute_query(query, (limit,))
    except Exception as e:
        print(f"❌ Error getting recent task runs: {e}")
        return []

def get_running_tasks() -> List[Dict[str, Any]]:
    """Get currently running tasks"""
    try:
        if IS_PRODUCTION:
            query = """
                SELECT tl.*, t.name as task_name 
                FROM task_log tl 
                JOIN task t ON tl.task_id = t.id 
                WHERE tl.status = %s
                ORDER BY tl.started_at DESC
            """
            params = ('running',)
        else:
            query = """
                SELECT tl.*, t.name as task_name 
                FROM task_log tl 
                JOIN task t ON tl.task_id = t.id 
                WHERE tl.status = ?
                ORDER BY tl.started_at DESC
            """
            params = ('running',)
        
        return execute_query(query, params)
    except Exception as e:
        print(f"❌ Error getting running tasks: {e}")
        return []

def get_db_path():
    """Get database path (for SQLite only)"""
    if IS_PRODUCTION:
        return "PostgreSQL (Railway)"
    else:
        return os.path.join(os.path.dirname(__file__), 'terrascan.db')

if __name__ == "__main__":
    print("🔧 TERRASCAN Database Module")
    print(f"Environment: {'Production (PostgreSQL)' if IS_PRODUCTION else 'Development (SQLite)'}")
    
    if init_database():
        stats = get_database_stats()
        print(f"📊 Database Stats:")
        print(f"   • Type: {stats['database_type']}")
        print(f"   • Total Records: {stats['total_records']}")
        print(f"   • Recent Records (24h): {stats['recent_records']}")
        print(f"   • Providers: {list(stats['by_provider'].keys())}")
    else:
        print("❌ Database initialization failed") 
