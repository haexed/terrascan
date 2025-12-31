#!/usr/bin/env python3
"""
Database Migration: Add Performance Indexes
Optimizes query performance for common access patterns
"""

import os
import psycopg2


def add_performance_indexes():
    """Add indexes to optimize common query patterns"""

    print("📋 Terrascan Performance Index Migration")
    print("=" * 50)

    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        print("✅ Connected to database")

        indexes = [
            # Index for filtering by provider (used in almost every query)
            ("idx_metric_provider",
             "CREATE INDEX IF NOT EXISTS idx_metric_provider ON metric_data(provider_key)"),

            # Index for timestamp filtering (used with INTERVAL queries)
            ("idx_metric_timestamp",
             "CREATE INDEX IF NOT EXISTS idx_metric_timestamp ON metric_data(timestamp DESC)"),

            # Composite index for provider + metric_name (common WHERE pattern)
            ("idx_metric_provider_metric",
             "CREATE INDEX IF NOT EXISTS idx_metric_provider_metric ON metric_data(provider_key, metric_name)"),

            # Composite index for provider + timestamp (viewport queries)
            ("idx_metric_provider_timestamp",
             "CREATE INDEX IF NOT EXISTS idx_metric_provider_timestamp ON metric_data(provider_key, timestamp DESC)"),

            # Index for task_log queries
            ("idx_task_log_task_started",
             "CREATE INDEX IF NOT EXISTS idx_task_log_task_started ON task_log(task_id, started_at DESC)"),

            # Index for spatial queries (lat/lng filtering)
            ("idx_metric_location",
             "CREATE INDEX IF NOT EXISTS idx_metric_location ON metric_data(location_lat, location_lng) WHERE location_lat IS NOT NULL AND location_lng IS NOT NULL"),
        ]

        for index_name, sql in indexes:
            print(f"🔧 Creating {index_name}...")
            try:
                cursor.execute(sql)
                print(f"   ✅ {index_name} created")
            except psycopg2.errors.DuplicateTable:
                print(f"   ⏭️  {index_name} already exists")
            except Exception as e:
                print(f"   ⚠️  {index_name} failed: {e}")

        conn.commit()
        cursor.close()
        conn.close()

        print()
        print("✅ Performance index migration complete!")
        print("🚀 Queries should now be significantly faster")
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    add_performance_indexes()
