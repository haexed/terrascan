#!/usr/bin/env python3
"""
Repair task.command values that point at modules which don't exist.

Six task rows were created with module paths that were never renamed when the
task files were: `tasks.fetch_biodiversity`, `tasks.fetch_weather`,
`tasks.fetch_fires`, `tasks.fetch_air_quality`. Running any of them fails with
"Could not import ...", which is why gbif and openweather never collected.

Only rows whose parameters match the real function signature are repaired here.
Idempotent - re-running is a no-op.
"""

import importlib
import sys

from database.db import execute_query, execute_insert

# task name -> corrected command (module.function)
COMMAND_FIXES = {
    'gbif_species_observations': 'tasks.fetch_gbif_biodiversity.fetch_biodiversity_data',
    'gbif_comprehensive': 'tasks.fetch_gbif_biodiversity.fetch_biodiversity_data',
    'openweather_current': 'tasks.fetch_openweathermap_weather.fetch_weather_data',
    'openweather_alerts': 'tasks.fetch_openweathermap_weather.fetch_weather_data',
}


def check_commands():
    """Report every task whose command can't be imported."""
    broken = []
    for task in execute_query("SELECT name, command, parameters FROM task ORDER BY name"):
        module_name, function_name = task['command'].rsplit('.', 1)
        try:
            module = importlib.import_module(module_name)
            getattr(module, function_name)
        except (ImportError, AttributeError) as e:
            broken.append((task['name'], task['command'], str(e)))
    return broken


def fix_task_commands(verbose: bool = True) -> bool:
    """Point the repairable tasks at their real module paths."""
    try:
        for name, command in COMMAND_FIXES.items():
            execute_insert(
                "UPDATE task SET command = %s, updated_date = CURRENT_TIMESTAMP "
                "WHERE name = %s AND command <> %s",
                (command, name, command)
            )

        if verbose:
            print(f"✅ Checked {len(COMMAND_FIXES)} task commands")
            broken = check_commands()
            if broken:
                print(f"⚠️ {len(broken)} task(s) still unrunnable:")
                for name, command, error in broken:
                    print(f"   {name}: {command} -> {error}")
            else:
                print("✅ Every task command imports")
        return True
    except Exception as e:
        print(f"❌ Error fixing task commands: {e}")
        return False


if __name__ == "__main__":
    if not fix_task_commands():
        sys.exit(1)
