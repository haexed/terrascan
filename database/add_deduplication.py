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
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found - cannot run migration")
        return False
    
    try:
        print("🔧 Adding deduplication constraints to metric_data table...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check if constraint already exists
        cursor.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'metric_data' 
            AND constraint_type = 'UNIQUE'
            AND constraint_name = 'unique_metric_measurement'
        """)
        
        if cursor.fetchone():
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
        
        # Add index for faster deduplication queries
        print("🚀 Creating performance index for deduplication...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_metric_dedup 
            ON metric_data (provider_key, metric_name, timestamp, location_lat, location_lng)
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Deduplication constraints added successfully!")
        print("🎯 TERRASCAN now prevents duplicate environmental data")
        return True
        
    except psycopg2.errors.UniqueViolation as e:
        print("⚠️ Existing duplicate data found - cleaning required first")
        print("💡 Run cleanup_duplicates() before adding constraints")
        return False
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
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
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        return None
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Total records
        cursor.execute("SELECT COUNT(*) FROM metric_data")
        total_records = cursor.fetchone()[0]
        
        # Unique records (what we should have)
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT DISTINCT provider_key, metric_name, timestamp, location_lat, location_lng
                FROM metric_data
            ) as unique_records
        """)
        unique_records = cursor.fetchone()[0]
        
        # Duplicate groups
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT provider_key, metric_name, timestamp, location_lat, location_lng, COUNT(*)
                FROM metric_data 
                GROUP BY provider_key, metric_name, timestamp, location_lat, location_lng
                HAVING COUNT(*) > 1
            ) as duplicates
        """)
        duplicate_groups = cursor.fetchone()[0]
        
        # Duplicate records
        duplicate_records = total_records - unique_records
        
        cursor.close()
        conn.close()
        
        return {
            'total_records': total_records,
            'unique_records': unique_records,
            'duplicate_records': duplicate_records,
            'duplicate_groups': duplicate_groups,
            'efficiency': f"{(unique_records/total_records*100):.1f}%" if total_records > 0 else "0%"
        }
        
    except Exception as e:
        print(f"❌ Error getting duplicate stats: {e}")
        return None

if __name__ == "__main__":
    print("🚀 TERRASCAN Database Deduplication Migration")
    print("=" * 50)
    
    # Get current duplicate statistics
    stats = get_duplicate_stats()
    if stats:
        print("📊 Current Database Statistics:")
        print(f"   Total records: {stats['total_records']:,}")
        print(f"   Unique records: {stats['unique_records']:,}")
        print(f"   Duplicate records: {stats['duplicate_records']:,}")
        print(f"   Duplicate groups: {stats['duplicate_groups']:,}")
        print(f"   Storage efficiency: {stats['efficiency']}")
        print()
        
        if stats['duplicate_records'] > 0:
            print("🧹 Step 1: Clean up existing duplicates...")
            if cleanup_existing_duplicates():
                print("\n🔧 Step 2: Add deduplication constraints...")
                add_deduplication_constraints()
            else:
                print("❌ Cannot proceed - cleanup failed")
        else:
            print("🔧 Adding deduplication constraints...")
            add_deduplication_constraints()
    else:
        print("❌ Cannot connect to database") 
