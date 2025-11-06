#!/usr/bin/env python3
"""
Terrascan Database Schema Inspector
Self-documenting PostgreSQL schema introspection
"""

import os
import psycopg2
import psycopg2.extras
from typing import Dict, List, Any, Optional
from datetime import datetime

def get_database_schema() -> Dict[str, Any]:
    """
    Introspect PostgreSQL database to get complete schema information
    Returns comprehensive schema data for documentation
    """
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        return {'error': 'DATABASE_URL not configured'}
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        schema_data = {
            'database_info': get_database_info(cursor),
            'tables': get_table_info(cursor),
            'indexes': get_index_info(cursor),
            'constraints': get_constraint_info(cursor),
            'data_statistics': get_data_statistics(cursor),
            'generated_at': datetime.now().isoformat()
        }
        
        cursor.close()
        conn.close()
        
        return schema_data
        
    except Exception as e:
        return {'error': f'Schema introspection failed: {str(e)}'}

def get_database_info(cursor) -> Dict[str, Any]:
    """Get basic database information"""
    try:
        # Database version and settings
        cursor.execute("SELECT version()")
        version = cursor.fetchone()['version']
        
        cursor.execute("SELECT current_database(), current_user, inet_server_addr(), inet_server_port()")
        db_info = cursor.fetchone()
        
        cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
        db_size = cursor.fetchone()['pg_size_pretty']
        
        return {
            'version': version,
            'database': db_info['current_database'],
            'user': db_info['current_user'],
            'host': db_info['inet_server_addr'],
            'port': db_info['inet_server_port'],
            'size': db_size
        }
    except Exception as e:
        return {'error': str(e)}

def get_table_info(cursor) -> List[Dict[str, Any]]:
    """Get detailed information about all tables"""
    try:
        # Get all tables in public schema
        cursor.execute("""
            SELECT 
                t.table_name,
                obj_description(c.oid) as table_comment,
                pg_size_pretty(pg_total_relation_size(c.oid)) as table_size,
                pg_stat_get_tuples_inserted(c.oid) as inserts,
                pg_stat_get_tuples_updated(c.oid) as updates,
                pg_stat_get_tuples_deleted(c.oid) as deletes,
                pg_stat_get_live_tuples(c.oid) as live_tuples
            FROM information_schema.tables t
            LEFT JOIN pg_class c ON c.relname = t.table_name
            WHERE t.table_schema = 'public' 
            AND t.table_type = 'BASE TABLE'
            ORDER BY t.table_name
        """)
        
        tables = []
        for table in cursor.fetchall():
            table_dict = dict(table)
            table_dict['columns'] = get_table_columns(cursor, table['table_name'])
            tables.append(table_dict)
        
        return tables
        
    except Exception as e:
        return [{'error': str(e)}]

def get_table_columns(cursor, table_name: str) -> List[Dict[str, Any]]:
    """Get detailed column information for a specific table"""
    try:
        cursor.execute("""
            SELECT 
                c.column_name,
                c.data_type,
                c.character_maximum_length,
                c.numeric_precision,
                c.numeric_scale,
                c.is_nullable,
                c.column_default,
                c.ordinal_position,
                col_description(pgc.oid, c.ordinal_position) as column_comment
            FROM information_schema.columns c
            LEFT JOIN pg_class pgc ON pgc.relname = c.table_name
            WHERE c.table_name = %s
            AND c.table_schema = 'public'
            ORDER BY c.ordinal_position
        """, (table_name,))
        
        columns = []
        for col in cursor.fetchall():
            col_dict = dict(col)
            
            # Build readable data type
            if col['character_maximum_length']:
                col_dict['full_type'] = f"{col['data_type']}({col['character_maximum_length']})"
            elif col['numeric_precision'] and col['numeric_scale']:
                col_dict['full_type'] = f"{col['data_type']}({col['numeric_precision']},{col['numeric_scale']})"
            elif col['numeric_precision']:
                col_dict['full_type'] = f"{col['data_type']}({col['numeric_precision']})"
            else:
                col_dict['full_type'] = col['data_type']
            
            columns.append(col_dict)
        
        return columns
        
    except Exception as e:
        return [{'error': str(e)}]

def get_index_info(cursor) -> List[Dict[str, Any]]:
    """Get information about all indexes"""
    try:
        cursor.execute("""
            SELECT 
                i.indexname,
                i.tablename,
                i.indexdef,
                pg_size_pretty(pg_relation_size(c.oid)) as index_size,
                s.idx_tup_read,
                s.idx_tup_fetch
            FROM pg_indexes i
            LEFT JOIN pg_class c ON c.relname = i.indexname
            LEFT JOIN pg_stat_user_indexes s ON s.indexrelname = i.indexname
            WHERE i.schemaname = 'public'
            ORDER BY i.tablename, i.indexname
        """)
        
        return [dict(row) for row in cursor.fetchall()]
        
    except Exception as e:
        return [{'error': str(e)}]

def get_constraint_info(cursor) -> List[Dict[str, Any]]:
    """Get information about table constraints"""
    try:
        cursor.execute("""
            SELECT 
                tc.constraint_name,
                tc.table_name,
                tc.constraint_type,
                tc.is_deferrable,
                tc.initially_deferred,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            LEFT JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            LEFT JOIN information_schema.constraint_column_usage ccu 
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.table_schema = 'public'
            ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name
        """)
        
        return [dict(row) for row in cursor.fetchall()]
        
    except Exception as e:
        return [{'error': str(e)}]

def get_data_statistics(cursor) -> Dict[str, Any]:
    """Get data statistics and insights"""
    try:
        stats = {}
        
        # Overall record counts
        cursor.execute("""
            SELECT 
                'metric_data' as table_name,
                COUNT(*) as total_records,
                COUNT(DISTINCT provider_key) as unique_providers,
                COUNT(DISTINCT metric_name) as unique_metrics,
                MIN(timestamp) as earliest_data,
                MAX(timestamp) as latest_data,
                MAX(created_date) as last_insert
            FROM metric_data
            UNION ALL
            SELECT 
                'task' as table_name,
                COUNT(*) as total_records,
                COUNT(CASE WHEN active THEN 1 END) as active_tasks,
                NULL as unique_metrics,
                MIN(created_date) as earliest_data,
                MAX(updated_date) as latest_data,
                MAX(created_date) as last_insert
            FROM task
            UNION ALL
            SELECT 
                'task_log' as table_name,
                COUNT(*) as total_records,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_runs,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_runs,
                MIN(started_at) as earliest_data,
                MAX(started_at) as latest_data,
                MAX(started_at) as last_insert
            FROM task_log
        """)
        
        stats['table_stats'] = [dict(row) for row in cursor.fetchall()]
        
        # Provider breakdown
        cursor.execute("""
            SELECT 
                provider_key,
                COUNT(*) as record_count,
                COUNT(DISTINCT metric_name) as metric_types,
                MIN(timestamp) as first_data,
                MAX(timestamp) as last_data,
                COUNT(DISTINCT DATE(timestamp)) as active_days
            FROM metric_data 
            GROUP BY provider_key 
            ORDER BY record_count DESC
        """)
        
        stats['provider_stats'] = [dict(row) for row in cursor.fetchall()]
        
        # Recent activity
        cursor.execute("""
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as records,
                COUNT(DISTINCT provider_key) as active_providers
            FROM metric_data 
            WHERE timestamp >= NOW() - INTERVAL '7 days'
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """)
        
        stats['recent_activity'] = [dict(row) for row in cursor.fetchall()]
        
        return stats
        
    except Exception as e:
        return {'error': str(e)}

def get_sample_data(cursor, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get sample data from a table"""
    try:
        cursor.execute(f"""
            SELECT * FROM {table_name} 
            ORDER BY 
                CASE WHEN '{table_name}' = 'metric_data' THEN timestamp
                     WHEN '{table_name}' = 'task_log' THEN started_at
                     ELSE created_date
                END DESC 
            LIMIT %s
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
        
    except Exception as e:
        return [{'error': str(e)}]

def get_schema_documentation() -> Dict[str, Any]:
    """Get comprehensive schema documentation with business context"""
    
    schema_data = get_database_schema()
    
    # Add business context and documentation
    table_descriptions = {
        'metric_data': {
            'purpose': 'Core environmental monitoring data storage',
            'description': 'Stores all environmental measurements from various data providers (NASA, NOAA, OpenAQ, etc.)',
            'key_features': [
                'UPSERT deduplication via composite unique constraint',
                'Supports geospatial data with lat/lng coordinates',
                'JSON metadata for flexible provider-specific data',
                'Temporal data with both measurement time and insertion time'
            ],
            'data_sources': ['NASA FIRMS (fires)', 'OpenAQ (air quality)', 'NOAA (ocean)', 'OpenWeatherMap (weather)', 'GBIF (biodiversity)']
        },
        'task': {
            'purpose': 'Environmental data collection task definitions',
            'description': 'Defines automated tasks for collecting environmental data from various APIs',
            'key_features': [
                'Cron-based scheduling for automated execution',
                'Provider-specific configuration parameters',
                'Active/inactive task management',
                'Command-based execution with JSON parameters'
            ]
        },
        'task_log': {
            'purpose': 'Task execution history and monitoring',
            'description': 'Tracks all task executions with performance metrics and error logging',
            'key_features': [
                'Execution timing and duration tracking',
                'Success/failure status with error details',
                'Records processed counting for data validation',
                'Triggered by tracking for audit purposes'
            ]
        },
        'system_config': {
            'purpose': 'Application configuration management',
            'description': 'Stores system-wide configuration settings with type validation',
            'key_features': [
                'Type-safe configuration with data_type field',
                'Description and documentation for each setting',
                'Timestamp tracking for configuration changes'
            ]
        },
        'provider_config': {
            'purpose': 'Data provider specific configuration',
            'description': 'Provider-specific settings like API timeouts, rate limits, and data collection parameters',
            'key_features': [
                'Per-provider configuration isolation',
                'Type validation and documentation',
                'Runtime configuration updates'
            ]
        }
    }
    
    # Add table descriptions to schema data
    if 'tables' in schema_data:
        for table in schema_data['tables']:
            table_name = table.get('table_name', '')
            if table_name in table_descriptions:
                table.update(table_descriptions[table_name])
    
    return schema_data

if __name__ == "__main__":
    """CLI tool for schema inspection"""
    import json
    
    print("🔍 Terrascan Database Schema Inspector")
    print("=" * 50)
    
    schema = get_schema_documentation()
    
    if 'error' in schema:
        print(f"❌ Error: {schema['error']}")
    else:
        print(f"✅ Database: {schema['database_info']['database']}")
        print(f"📊 Tables: {len(schema['tables'])}")
        print(f"🔗 Indexes: {len(schema['indexes'])}")
        print(f"🛡️ Constraints: {len(schema['constraints'])}")
        
        # Show table summary
        print("\n📋 Table Summary:")
        for table in schema['tables']:
            print(f"  • {table['table_name']}: {len(table['columns'])} columns, {table.get('live_tuples', 0)} records") 
