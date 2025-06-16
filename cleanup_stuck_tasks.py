#!/usr/bin/env python3

from dotenv import load_dotenv
load_dotenv()
from database.db import execute_query, execute_insert
from datetime import datetime

def cleanup_stuck_tasks():
    """Mark hung tasks as failed to clean up the database state"""
    
    # Get tasks that have been running for more than 30 minutes (1800 seconds)
    stuck_tasks = execute_query('''
        SELECT tl.id, tl.task_id, t.name, tl.started_at,
               EXTRACT(EPOCH FROM (NOW() - tl.started_at)) as running_seconds
        FROM task_log tl 
        JOIN task t ON tl.task_id = t.id 
        WHERE tl.status = %s
        AND EXTRACT(EPOCH FROM (NOW() - tl.started_at)) > 1800
        ORDER BY tl.started_at ASC
    ''', ('running',))
    
    if not stuck_tasks:
        print("✅ No stuck tasks found")
        return
    
    print(f"🔍 Found {len(stuck_tasks)} stuck tasks:")
    for task in stuck_tasks:
        runtime_minutes = int(task['running_seconds']) // 60
        print(f"  - {task['name']} (Log ID: {task['id']}) - stuck for {runtime_minutes} minutes")
    
    # Ask for confirmation
    response = input(f"\n❓ Mark {len(stuck_tasks)} stuck tasks as FAILED? (y/N): ").strip().lower()
    
    if response != 'y':
        print("❌ Cancelled - no changes made")
        return
    
    # Mark each stuck task as failed
    failed_count = 0
    for task in stuck_tasks:
        success = execute_insert('''
            UPDATE task_log SET 
                completed_at = NOW(),
                duration_seconds = EXTRACT(EPOCH FROM (NOW() - started_at)),
                status = 'failed',
                error_message = 'Task marked as failed due to timeout (hung for >30 minutes)'
            WHERE id = %s AND status = 'running'
        ''', (task['id'],))
        
        if success:
            failed_count += 1
            runtime_minutes = int(task['running_seconds']) // 60
            print(f"  ✅ Marked {task['name']} (Log ID: {task['id']}) as failed ({runtime_minutes}m runtime)")
        else:
            print(f"  ❌ Failed to update {task['name']} (Log ID: {task['id']})")
    
    print(f"\n🎉 Successfully marked {failed_count}/{len(stuck_tasks)} tasks as failed")
    
    if failed_count > 0:
        print("\n📋 Next steps:")
        print("  1. Check Railway production deployment for hung processes")
        print("  2. Restart Railway deployment if needed") 
        print("  3. Review NOAA ocean task for hanging issues")

if __name__ == "__main__":
    cleanup_stuck_tasks() 
