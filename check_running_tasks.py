#!/usr/bin/env python3

from dotenv import load_dotenv
load_dotenv()
from database.db import execute_query
import sys

# Check currently running tasks
running_tasks = execute_query('''
    SELECT tl.id, tl.task_id, t.name, tl.started_at, tl.status,
           EXTRACT(EPOCH FROM (NOW() - tl.started_at)) as running_seconds
    FROM task_log tl 
    JOIN task t ON tl.task_id = t.id 
    WHERE tl.status = %s
    ORDER BY tl.started_at DESC
''', ('running',))

print('Currently running tasks:')
if not running_tasks:
    print('  No tasks currently running')
else:
    for task in running_tasks:
        runtime = int(task['running_seconds']) if task['running_seconds'] else 0
        print(f'  {task["name"]} (Log ID: {task["id"]}) - Running for {runtime} seconds')
        print(f'    Started: {task["started_at"]}')
        
        # If running for more than 30 minutes, flag as potentially stuck
        if runtime > 1800:
            print(f'    ⚠️ WARNING: Task has been running for {runtime//60} minutes!')

# Also check recent task history for this specific task
print('\nRecent noaa_ocean_water_level task runs:')
noaa_history = execute_query('''
    SELECT tl.id, tl.started_at, tl.completed_at, tl.status, tl.duration_seconds, tl.records_processed
    FROM task_log tl 
    JOIN task t ON tl.task_id = t.id 
    WHERE t.name = %s
    ORDER BY tl.started_at DESC LIMIT 10
''', ('noaa_ocean_water_level',))

for run in noaa_history:
    duration = f"{run['duration_seconds']:.1f}s" if run['duration_seconds'] else "N/A"
    records = run['records_processed'] or 0
    print(f'  {run["started_at"]} - {run["status"]} ({duration}, {records} records)') 
