#!/usr/bin/env python3
"""
Terrascan Database Module
Simple SQLite database connection and setup
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

DB_PATH = os.path.join(os.path.dirname(__file__), 'terrascan.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

def get_db_connection():
    """Get SQLite database connection with proper settings"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    return conn

def init_database():
    """Initialize database with schema if it doesn't exist"""
    if not os.path.exists(DB_PATH):
        print(f"📁 Creating new database: {DB_PATH}")
        with open(SCHEMA_PATH, 'r') as f:
            schema = f.read()
        
        conn = get_db_connection()
        conn.executescript(schema)
        conn.close()
        print("✅ Database initialized with schema")
    else:
        print(f"📁 Using existing database: {DB_PATH}")
        # Check if metric_data table exists, if not, apply schema
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metric_data'")
            if not cursor.fetchone():
                print("🔧 metric_data table missing, applying schema...")
                with open(SCHEMA_PATH, 'r') as f:
                    schema = f.read()
                conn.executescript(schema)
                print("✅ Schema applied to existing database")
            conn.close()
        except Exception as e:
            print(f"⚠️ Database check failed: {e}")
            # If there's any issue, recreate the database
            print("🔄 Recreating database with fresh schema...")
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
            with open(SCHEMA_PATH, 'r') as f:
                schema = f.read()
            conn = get_db_connection()
            conn.executescript(schema)
            conn.close()
            print("✅ Database recreated with schema")

def execute_query(query: str, params: tuple = None) -> List[Dict]:
    """Execute a query and return results as list of dicts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return results

def execute_insert(query: str, params: tuple = None) -> int:
    """Execute insert/update/delete and return lastrowid"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    lastrowid = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return lastrowid

# Task management functions
def create_task(name: str, description: str, task_type: str, command: str, 
                cron_schedule: str = None, provider: str = None, 
                dataset: str = None, parameters: Dict = None) -> int:
    """Create a new task definition"""
    params_json = json.dumps(parameters) if parameters else None
    
    return execute_insert(
        """INSERT INTO task (name, description, task_type, command, cron_schedule, 
                            provider, dataset, parameters) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, description, task_type, command, cron_schedule, provider, dataset, params_json)
    )

def get_tasks(active_only: bool = True) -> List[Dict]:
    """Get all tasks, optionally filtered by active status"""
    query = "SELECT * FROM task"
    if active_only:
        query += " WHERE active = 1"
    query += " ORDER BY created_date DESC"
    
    return execute_query(query)

def get_task_by_name(name: str) -> Optional[Dict]:
    """Get a specific task by name"""
    results = execute_query("SELECT * FROM task WHERE name = ?", (name,))
    return results[0] if results else None

def start_task_run(task_id: int, triggered_by: str = 'manual', 
                   trigger_parameters: Dict = None) -> int:
    """Create a new task run record in 'running' status"""
    params_json = json.dumps(trigger_parameters) if trigger_parameters else None
    
    return execute_insert(
        """INSERT INTO task_log (task_id, status, triggered_by, trigger_parameters) 
           VALUES (?, 'running', ?, ?)""",
        (task_id, triggered_by, params_json)
    )

def complete_task_run(run_id: int, exit_code: int, stdout: str = None, 
                     stderr: str = None, error_details: str = None, 
                     actual_cost_cents: int = 0, records_processed: int = 0):
    """Mark a task run as completed with results"""
    status = 'completed' if exit_code == 0 else 'failed'
    completed_at = datetime.now().isoformat()
    
    # Calculate duration from started_at
    run_info = execute_query("SELECT started_at FROM task_log WHERE id = ?", (run_id,))
    if run_info:
        started_at = datetime.fromisoformat(run_info[0]['started_at'])
        duration = (datetime.now() - started_at).total_seconds()
    else:
        duration = 0
    
    execute_insert(
        """UPDATE task_log SET 
           completed_at = ?, duration_seconds = ?, status = ?, exit_code = ?,
           stdout = ?, stderr = ?, error_details = ?, 
           actual_cost_cents = ?, records_processed = ?
           WHERE id = ?""",
        (completed_at, duration, status, exit_code, stdout, stderr, 
         error_details, actual_cost_cents, records_processed, run_id)
    )

def get_recent_task_runs(limit: int = 50) -> List[Dict]:
    """Get recent task runs with task information"""
    return execute_query(
        """SELECT tl.*, t.name as task_name, t.description as task_description
           FROM task_log tl 
           JOIN task t ON tl.task_id = t.id 
           ORDER BY tl.started_at DESC 
           LIMIT ?""", 
        (limit,)
    )

def get_running_tasks() -> List[Dict]:
    """Get currently running tasks"""
    return execute_query(
        """SELECT tl.*, t.name as task_name 
           FROM task_log tl 
           JOIN task t ON tl.task_id = t.id 
           WHERE tl.status = 'running'
           ORDER BY tl.started_at DESC"""
    )

def store_metric_data(timestamp: str, provider_key: str, dataset: str, 
                     metric_name: str, value: float, unit: str = None,
                     location_lat: float = None, location_lng: float = None,
                     metadata: Dict = None, task_log_id: int = None) -> int:
    """Store environmental metric data"""
    metadata_json = json.dumps(metadata) if metadata else None
    
    return execute_insert(
        """INSERT INTO metric_data 
           (timestamp, provider_key, dataset, metric_name, value, unit,
            location_lat, location_lng, metadata, task_log_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (timestamp, provider_key, dataset, metric_name, value, unit,
         location_lat, location_lng, metadata_json, task_log_id)
    )

def get_daily_costs() -> List[Dict]:
    """Get daily cost summary"""
    return execute_query(
        """SELECT DATE(started_at) as date,
                  SUM(actual_cost_cents) as total_cost_cents,
                  COUNT(*) as total_runs,
                  SUM(records_processed) as total_records
           FROM task_log 
           WHERE status = 'completed'
           GROUP BY DATE(started_at)
           ORDER BY date DESC
           LIMIT 30"""
    )

def populate_sample_data():
    """Populate database with sample environmental data for demonstration"""
    try:
        # Check if we already have data
        existing_data = execute_query("SELECT COUNT(*) as count FROM metric_data")
        if existing_data and existing_data[0]['count'] > 0:
            print(f"📊 Database already has {existing_data[0]['count']} records")
            return
        
        print("📊 Populating sample environmental data...")
        from datetime import datetime, timedelta
        
        # Sample fire data (NASA FIRMS)
        base_time = datetime.now()
        for i in range(100):
            timestamp = (base_time - timedelta(hours=i)).isoformat()
            store_metric_data(
                timestamp=timestamp,
                provider_key='nasa_firms',
                dataset='active_fires',
                metric_name='fire_brightness',
                value=300 + (i * 2),  # Brightness in Kelvin
                unit='K',
                location_lat=40.0 + (i * 0.1),
                location_lng=-120.0 + (i * 0.1),
                metadata={'confidence': 85, 'satellite': 'MODIS'}
            )
        
        # Sample air quality data (OpenAQ)
        for i in range(50):
            timestamp = (base_time - timedelta(hours=i)).isoformat()
            store_metric_data(
                timestamp=timestamp,
                provider_key='openaq',
                dataset='measurements',
                metric_name='air_quality_pm25',
                value=75.5 - (i * 0.5),  # PM2.5 in μg/m³
                unit='μg/m³',
                location_lat=37.7749 + (i * 0.01),
                location_lng=-122.4194 + (i * 0.01),
                metadata={'city': 'San Francisco', 'station': f'Station_{i}'}
            )
        
        # Sample ocean temperature data (NOAA)
        for i in range(30):
            timestamp = (base_time - timedelta(hours=i * 3)).isoformat()
            store_metric_data(
                timestamp=timestamp,
                provider_key='noaa_ocean',
                dataset='oceanographic',
                metric_name='water_temperature',
                value=18.2 + (i * 0.1),  # Temperature in Celsius
                unit='°C',
                location_lat=37.8 + (i * 0.01),
                location_lng=-122.5 + (i * 0.01),
                metadata={'station': f'NOAA_{i}', 'depth': '0m'}
            )
        
        print("✅ Sample environmental data populated")
        
    except Exception as e:
        print(f"❌ Error populating sample data: {e}")

if __name__ == "__main__":
    # Initialize database when run directly
    init_database()
    populate_sample_data()
    print("🚀 Database ready!") 
