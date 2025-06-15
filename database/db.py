#!/usr/bin/env python3
"""
Database connection and operations for TERRASCAN
Python/PostgreSQL production platform
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# PostgreSQL connection (required for both development and production)
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL environment variable is required. TERRASCAN uses PostgreSQL for both development and production. See DEVELOPMENT.md for setup instructions.")

import psycopg2
import psycopg2.extras

print("🚀 TERRASCAN - PostgreSQL Platform")

def get_db_connection():
    """Get PostgreSQL database connection"""
    return psycopg2.connect(DATABASE_URL)

def execute_query(query: str, params: tuple = None) -> List[Dict[str, Any]]:
    """Execute a SELECT query and return results as list of dictionaries"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
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
        psycopg2.extras.execute_batch(cursor, query, params_list)
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
    """Initialize PostgreSQL database - use setup_production_railway.py for schema setup"""
    print("🚀 PostgreSQL database - use setup_production_railway.py for initialization")
    return True

def get_database_stats():
    """Get PostgreSQL database statistics"""
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
        recent_records = execute_query("""
            SELECT COUNT(*) as count 
            FROM metric_data 
            WHERE created_date >= NOW() - INTERVAL '24 hours'
        """)
        stats['recent_records'] = recent_records[0]['count'] if recent_records else 0
        
        # Database info
        stats['database_type'] = 'PostgreSQL'
        
        return stats
        
    except Exception as e:
        print(f"❌ Error getting database stats: {e}")
        return {
            'total_records': 0,
            'by_provider': {},
            'recent_records': 0,
            'database_type': 'PostgreSQL',
            'error': str(e)
        }

def store_metric_data(timestamp: str, provider_key: str, dataset: str, 
                     metric_name: str, value: float, unit: str = None,
                     location_lat: float = None, location_lng: float = None,
                     metadata: dict = None, task_log_id: int = None) -> bool:
    """
    Store environmental metric data with automatic deduplication
    Uses UPSERT to prevent duplicate data while updating existing records
    """
    try:
        metadata_json = json.dumps(metadata) if metadata else None
        
        # UPSERT query with deduplication - updates if exists, inserts if new
        query = """
            INSERT INTO metric_data 
            (provider_key, metric_name, value, unit, location_lat, location_lng, timestamp, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (provider_key, metric_name, timestamp, location_lat, location_lng)
            DO UPDATE SET
                value = EXCLUDED.value,
                unit = EXCLUDED.unit,
                metadata = EXCLUDED.metadata,
                created_date = NOW()
        """
        
        return execute_insert(query, (provider_key, metric_name, value, unit, 
                                    location_lat, location_lng, timestamp, metadata_json))
        
    except Exception as e:
        print(f"❌ Error storing metric data: {e}")
        # Fallback for databases without deduplication constraint yet
        try:
            fallback_query = """
                INSERT INTO metric_data 
                (provider_key, metric_name, value, unit, location_lat, location_lng, timestamp, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            return execute_insert(fallback_query, (provider_key, metric_name, value, unit, 
                                                 location_lat, location_lng, timestamp, metadata_json))
        except Exception as fallback_error:
            print(f"❌ Fallback insert also failed: {fallback_error}")
            return False

def get_tasks(active_only: bool = True) -> List[Dict[str, Any]]:
    """Get all tasks, optionally filtered by active status"""
    try:
        query = "SELECT * FROM task"
        if active_only:
            query += " WHERE active = true"
        query += " ORDER BY created_date DESC"
        
        return execute_query(query)
    except Exception as e:
        print(f"❌ Error getting tasks: {e}")
        return []

def get_task_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get a specific task by name"""
    try:
        query = "SELECT * FROM task WHERE name = %s"
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
            
    except Exception as e:
        print(f"❌ Error starting task run: {e}")
        return None

def complete_task_run(run_id: int, exit_code: int, stdout: str = None, 
                     stderr: str = None, error_details: str = None, 
                     actual_cost_cents: int = 0, records_processed: int = 0):
    """Mark a task run as completed with results"""
    try:
        status = 'completed' if exit_code == 0 else 'failed'
        
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
        """
        
        return execute_query(query, (limit,))
    except Exception as e:
        print(f"❌ Error getting recent task runs: {e}")
        return []

def get_running_tasks() -> List[Dict[str, Any]]:
    """Get currently running tasks"""
    try:
        query = """
            SELECT tl.*, t.name as task_name 
            FROM task_log tl 
            JOIN task t ON tl.task_id = t.id 
            WHERE tl.status = %s
            ORDER BY tl.started_at DESC
        """
        
        return execute_query(query, ('running',))
    except Exception as e:
        print(f"❌ Error getting running tasks: {e}")
        return []

def get_latest_timestamp(provider_key: str, metric_name: str = None) -> Optional[str]:
    """
    Get the most recent timestamp for a provider/metric combination
    Used for incremental data fetching to avoid re-fetching existing data
    """
    try:
        if metric_name:
            query = """
                SELECT MAX(timestamp) as latest_timestamp 
                FROM metric_data 
                WHERE provider_key = %s AND metric_name = %s
            """
            params = (provider_key, metric_name)
        else:
            query = """
                SELECT MAX(timestamp) as latest_timestamp 
                FROM metric_data 
                WHERE provider_key = %s
            """
            params = (provider_key,)
        
        result = execute_query(query, params)
        return result[0]['latest_timestamp'] if result and result[0]['latest_timestamp'] else None
        
    except Exception as e:
        print(f"❌ Error getting latest timestamp: {e}")
        return None

def get_data_coverage_stats(provider_key: str) -> Dict[str, Any]:
    """Get data coverage statistics for a provider"""
    try:
        query = """
            SELECT 
                MIN(timestamp) as earliest_data,
                MAX(timestamp) as latest_data,
                COUNT(*) as total_records,
                COUNT(DISTINCT metric_name) as unique_metrics,
                COUNT(DISTINCT DATE(timestamp)) as days_covered
            FROM metric_data 
            WHERE provider_key = %s
        """
        
        result = execute_query(query, (provider_key,))
        return result[0] if result else {}
        
    except Exception as e:
        print(f"❌ Error getting coverage stats: {e}")
        return {}

def batch_store_metric_data(data_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Store multiple metric data points in a single transaction
    More efficient for bulk operations
    """
    try:
        if not data_batch:
            return {'success': True, 'inserted': 0, 'updated': 0}
        
        # Prepare batch query with UPSERT
        query = """
            INSERT INTO metric_data 
            (provider_key, metric_name, value, unit, location_lat, location_lng, timestamp, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (provider_key, metric_name, timestamp, location_lat, location_lng)
            DO UPDATE SET
                value = EXCLUDED.value,
                unit = EXCLUDED.unit,
                metadata = EXCLUDED.metadata,
                created_date = NOW()
        """
        
        # Prepare parameters for batch
        params_list = []
        for data in data_batch:
            metadata_json = json.dumps(data.get('metadata')) if data.get('metadata') else None
            params_list.append((
                data['provider_key'],
                data['metric_name'], 
                data['value'],
                data.get('unit'),
                data.get('location_lat'),
                data.get('location_lng'),
                data['timestamp'],
                metadata_json
            ))
        
        success = execute_many(query, params_list)
        
        return {
            'success': success,
            'processed': len(data_batch),
            'message': f"Batch stored {len(data_batch)} records with deduplication"
        }
        
    except Exception as e:
        print(f"❌ Error in batch store: {e}")
        return {'success': False, 'error': str(e), 'processed': 0}

def get_database_info():
    """Get database connection information"""
    try:
        # Parse DATABASE_URL to show connection details (without password)
        from urllib.parse import urlparse
        parsed = urlparse(DATABASE_URL)
        
        info = {
            'type': 'PostgreSQL',
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 5432,
            'database': parsed.path.lstrip('/') if parsed.path else 'unknown',
            'username': parsed.username or 'unknown'
        }
        
        return f"PostgreSQL: {info['username']}@{info['host']}:{info['port']}/{info['database']}"
        
    except Exception as e:
        return f"PostgreSQL (connection parse error: {e})"

if __name__ == "__main__":
    print("🔧 TERRASCAN Database Module")
    print("🚀 PostgreSQL Platform")
    
    if init_database():
        print("✅ Database module loaded successfully")
        print(f"📊 Stats: {get_database_stats()}")
    else:
        print("❌ Database initialization failed") 
