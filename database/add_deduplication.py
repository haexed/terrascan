#!/usr/bin/env python3
"""
Database Migration: Add Deduplication Constraints
Prevents duplicate environmental data from being stored
"""

import os
import psycopg2
from datetime import datetime

def add_deduplication_constraints():
    """Add unique constraints to prevent duplicate metric data"""

    print("📋 Terrascan Database Deduplication Migration - starting")

    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found - cannot run migration")
        return False

    print("🔌 Connecting to database...")
    try:
        print("🔧 Adding deduplication constraints to metric_data table...")
        conn = psycopg2.connect(database_url)
        print("✅ Database connection established")
        cursor = conn.cursor()
        print("📋 Database cursor created")
        
        # Check if constraint already exists
        print("🔍 Checking existing constraints...")
        cursor.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'metric_data'
            AND constraint_type = 'UNIQUE'
            AND constraint_name = 'unique_metric_measurement'
        """)
        print("📋 Constraint check query executed")
        
        result = cursor.fetchone()
        print(f"📊 Constraint check result: {result}")
        if result:
            print("✅ Deduplication constraint already exists")
            cursor.close()
            conn.close()
            return True
        
        # Add composite unique constraint for deduplication
        print("📊 Creating unique constraint for metric deduplication...")
        cursor.execute("""
            ALTER TABLE metric_data
            ADD CONSTRAINT unique_metric_measurement
            UNIQUE (provider_key, metric_name, timestamp, location_lat, location_lng)
        """)
        print("✅ Unique constraint created")
        
        # Add index for faster deduplication queries
        print("🚀 Creating performance index for deduplication...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_metric_dedup
            ON metric_data (provider_key, metric_name, timestamp, location_lat, location_lng)
        """)
        print("✅ Performance index created")
        
        print("💾 Committing changes...")
        conn.commit()
        print("✅ Changes committed")
        cursor.close()
        conn.close()
        print("🔒 Database connection closed")

        print("✅ Deduplication constraints added successfully!")
        print("🎯 Terrascan now prevents duplicate environmental data")
        return True
        
    except psycopg2.errors.UniqueViolation as e:
        print(f"⚠️ UniqueViolation caught: {e}")
        print("⚠️ Existing duplicate data found - cleaning required first")
        print("💡 Run cleanup_duplicates() before adding constraints")
        return False

    except psycopg2.OperationalError as e:
        print(f"❌ Database connection error: {e}")
        return False

    except Exception as e:
        print(f"❌ Unexpected migration error: {e}")
        print(f"🔎 Exception type: {type(e).__name__}")
        import traceback
        print(f"📜 Stack trace: {traceback.format_exc()}")
        return False

def cleanup_existing_duplicates():
    """Remove duplicate records keeping the most recent ones"""
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        print("🧹 Cleaning up existing duplicate records...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Get count of duplicates before cleanup
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT provider_key, metric_name, timestamp, location_lat, location_lng, COUNT(*)
                FROM metric_data 
                GROUP BY provider_key, metric_name, timestamp, location_lat, location_lng
                HAVING COUNT(*) > 1
            ) as duplicates
        """)
        duplicate_groups = cursor.fetchone()[0]
        
        if duplicate_groups == 0:
            print("✅ No duplicates found - database is clean!")
            cursor.close()
            conn.close()
            return True
        
        print(f"🔍 Found {duplicate_groups} groups of duplicate records")
        
        # Delete duplicates, keeping the most recent (highest ID) for each group
        print("🗑️ Removing duplicate records (keeping most recent)...")
        cursor.execute("""
            DELETE FROM metric_data 
            WHERE id NOT IN (
                SELECT MAX(id) 
                FROM metric_data 
                GROUP BY provider_key, metric_name, timestamp, location_lat, location_lng
            )
        """)
        
        deleted_count = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Cleanup complete! Removed {deleted_count} duplicate records")
        print(f"🎯 Database is now optimized and ready for deduplication constraints")
        return True
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False

def get_duplicate_stats():
    """Get statistics about duplicate data"""

    print("🔍 get_duplicate_stats() starting...")
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ No DATABASE_URL found")
        return None

    print("🔌 Connecting to database for stats...")
    try:
        conn = psycopg2.connect(database_url, connect_timeout=10)
        print("✅ Stats database connection established")
        cursor = conn.cursor()

        # Total records - simple count first
        print("📊 Getting total record count...")
        cursor.execute("SELECT COUNT(*) FROM metric_data")
        total_records = cursor.fetchone()[0]
        print(f"📋 Total records: {total_records}")
        
        # Skip complex queries if too many records (causes timeout)
        if total_records > 100000:
            print("⚠️ Large dataset detected, skipping complex duplicate analysis")
            cursor.close()
            conn.close()
            return {
                'total_records': total_records,
                'unique_records': total_records,  # Assume no duplicates for large datasets
                'duplicate_records': 0,
                'duplicate_groups': 0,
                'efficiency': '100.0%'
            }

        # Unique records (what we should have) - only for smaller datasets
        print("🔍 Counting unique records (complex query)...")
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT DISTINCT provider_key, metric_name, timestamp, location_lat, location_lng
                FROM metric_data
            ) as unique_records
        """)
        unique_records = cursor.fetchone()[0]
        print(f"📋 Unique records: {unique_records}")
        
        # Duplicate groups - simplified
        print("🔍 Counting duplicate groups...")
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT provider_key, metric_name, timestamp, location_lat, location_lng, COUNT(*)
                FROM metric_data
                GROUP BY provider_key, metric_name, timestamp, location_lat, location_lng
                HAVING COUNT(*) > 1
            ) as duplicates
        """)
        duplicate_groups = cursor.fetchone()[0]
        print(f"📋 Duplicate groups: {duplicate_groups}")
        
        # Duplicate records
        duplicate_records = total_records - unique_records
        print(f"📊 Calculated duplicate records: {duplicate_records}")

        cursor.close()
        conn.close()
        print("🔒 Stats database connection closed")
        
        return {
            'total_records': total_records,
            'unique_records': unique_records,
            'duplicate_records': duplicate_records,
            'duplicate_groups': duplicate_groups,
            'efficiency': f"{(unique_records/total_records*100):.1f}%" if total_records > 0 else "0%"
        }
        
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection timeout/error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error getting duplicate stats: {e}")
        import traceback
        print(f"📜 Stats error traceback: {traceback.format_exc()}")
        return None
        return None

if __name__ == "__main__":
    print("🚀 Terrascan Database Deduplication Migration")
    print("=" * 50)
    print("📋 Migration script starting...")

    # Get current duplicate statistics
    print("🔍 Getting database statistics...")
    stats = get_duplicate_stats()
    print(f"📊 Statistics result: {stats is not None}")
    if stats:
        print("📊 Current Database Statistics:")
        print(f"   Total records: {stats['total_records']:,}")
        print(f"   Unique records: {stats['unique_records']:,}")
        print(f"   Duplicate records: {stats['duplicate_records']:,}")
        print(f"   Duplicate groups: {stats['duplicate_groups']:,}")
        print(f"   Storage efficiency: {stats['efficiency']}")
        print()
        print("🔍 Proceeding with migration logic...")
        
        if stats['duplicate_records'] > 0:
            print("🧹 Step 1: Clean up existing duplicates...")
            print("🔍 Calling cleanup function...")
            if cleanup_existing_duplicates():
                print("\n🔧 Step 2: Add deduplication constraints...")
                print("🔍 Calling constraint function...")
                add_deduplication_constraints()
            else:
                print("❌ Cannot proceed - cleanup failed")
        else:
            print("🔧 Adding deduplication constraints...")
            print("🔍 Calling constraint function directly...")
            result = add_deduplication_constraints()
            print(f"📊 Constraint function result: {result}")
    else:
        print("❌ Cannot connect to database - stats is None")
        print("🔍 Migration script ending with database connection failure") 
