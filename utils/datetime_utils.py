#!/usr/bin/env python3
"""
Terrascan Datetime Utilities
Centralized datetime formatting with consistent ISO standards and timezone support
"""

from datetime import datetime, timezone
from typing import Optional, Union


# Standard Terrascan datetime formats (ISO 8601 compliant)
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"  # 2025-06-14 10:30:45
DATETIME_FORMAT_TZ = "%Y-%m-%d %H:%M:%S %z"  # 2025-06-14 10:30:45 +0000
DATE_FORMAT = "%Y-%m-%d"  # 2025-06-14
TIME_FORMAT = "%H:%M:%S"  # 10:30:45
ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"  # 2025-06-14T10:30:45.123456Z


def format_datetime(dt: Union[datetime, str, None], 
                   include_timezone: bool = True,
                   format_type: str = 'standard') -> str:
    """
    Format datetime with consistent Terrascan styling
    
    Args:
        dt: Datetime object, ISO string, or None
        include_timezone: Whether to include timezone info
        format_type: 'standard', 'iso', 'date_only', 'time_only'
    
    Returns:
        Formatted datetime string or 'Unknown' if None/invalid
    """
    if dt is None:
        return 'Unknown'
    
    # Convert string to datetime if needed
    if isinstance(dt, str):
        try:
            # Try parsing common formats
            for fmt in [ISO_FORMAT, DATETIME_FORMAT_TZ, DATETIME_FORMAT, "%Y-%m-%dT%H:%M:%S"]:
                try:
                    dt = datetime.strptime(dt, fmt)
                    break
                except ValueError:
                    continue
            else:
                # If no format matches, try fromisoformat
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return 'Invalid Date'
    
    # Ensure UTC timezone if none specified
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Format based on type requested
    if format_type == 'iso':
        return dt.isoformat()
    elif format_type == 'date_only':
        return dt.strftime(DATE_FORMAT)
    elif format_type == 'time_only':
        return dt.strftime(TIME_FORMAT)
    else:  # standard
        if include_timezone:
            # Format timezone as ±HH:MM
            tz_offset = dt.strftime('%z')
            if tz_offset:
                tz_formatted = f"{tz_offset[:3]}:{tz_offset[3:]}"
                return f"{dt.strftime(DATETIME_FORMAT)} ({tz_formatted})"
            else:
                return f"{dt.strftime(DATETIME_FORMAT)} (UTC)"
        else:
            return dt.strftime(DATETIME_FORMAT)


def format_datetime_utc(dt: Union[datetime, str, None]) -> str:
    """
    Format datetime as UTC with timezone indicator
    Standard format: YYYY-MM-DD HH:MM:SS (UTC+00:00)
    """
    return format_datetime(dt, include_timezone=True, format_type='standard')


def format_date_only(dt: Union[datetime, str, None]) -> str:
    """
    Format as date only: YYYY-MM-DD
    """
    return format_datetime(dt, include_timezone=False, format_type='date_only')


def format_time_only(dt: Union[datetime, str, None]) -> str:
    """
    Format as time only: HH:MM:SS
    """
    return format_datetime(dt, include_timezone=False, format_type='time_only')


def format_iso(dt: Union[datetime, str, None]) -> str:
    """
    Format as strict ISO 8601: YYYY-MM-DDTHH:MM:SS.ssssssZ
    """
    return format_datetime(dt, include_timezone=True, format_type='iso')


def time_ago(dt: Union[datetime, str, None]) -> str:
    """
    Format as relative time (e.g., "2 hours ago", "Just now")
    """
    if dt is None:
        return 'Never'
    
    # Convert to datetime if string
    if isinstance(dt, str):
        dt = format_datetime(dt, format_type='iso')
        if dt in ['Unknown', 'Invalid Date']:
            return 'Never'
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
    
    # Ensure timezone
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    diff = now - dt
    seconds = int(diff.total_seconds())
    
    if seconds < 60:
        return 'Just now'
    elif seconds < 3600:  # < 1 hour
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:  # < 1 day
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 2592000:  # < 30 days
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        return format_date_only(dt)


def current_utc() -> datetime:
    """
    Get current UTC datetime with timezone info
    """
    return datetime.now(timezone.utc)


def current_utc_formatted(include_timezone: bool = True) -> str:
    """
    Get current UTC datetime as formatted string
    """
    return format_datetime_utc(current_utc()) if include_timezone else format_datetime(current_utc(), include_timezone=False)


# Data display utilities
def format_nullable_display(value, no_data_text="NO DATA", emoji="🤷"):
    """
    Format nullable values for display with consistent 'no data' indicators

    Args:
        value: The value to format (could be None, 0, or actual data)
        no_data_text: Text to show when value is None
        emoji: Emoji to show with no data text

    Returns:
        Formatted string for display
    """
    if value is None:
        return f"{emoji} {no_data_text}"
    return str(value)

def format_metric_display(value, unit="", decimal_places=1, no_data_text="NO DATA", emoji="🤷"):
    """
    Format metric values with proper NULL handling and units

    Args:
        value: Numeric value or None
        unit: Unit string (e.g., "°C", "μg/m³")
        decimal_places: Number of decimal places for formatting
        no_data_text: Text to show when value is None
        emoji: Emoji to show with no data

    Returns:
        Formatted string with units or no-data indicator
    """
    if value is None:
        return f"{emoji} {no_data_text}"

    if isinstance(value, (int, float)):
        if decimal_places == 0:
            formatted_value = f"{int(value)}"
        else:
            formatted_value = f"{value:.{decimal_places}f}"
        return f"{formatted_value}{unit}"

    return f"{value}{unit}"

# Template filters for Jinja2
def register_template_filters(app):
    """
    Register datetime and data display filters for Flask/Jinja2 templates
    Usage in templates: {{ datetime_value | format_dt }}
    """
    # Datetime filters
    app.jinja_env.filters['format_dt'] = format_datetime_utc
    app.jinja_env.filters['format_date'] = format_date_only
    app.jinja_env.filters['format_time'] = format_time_only
    app.jinja_env.filters['format_iso'] = format_iso
    app.jinja_env.filters['time_ago'] = time_ago

    # Data display filters
    app.jinja_env.filters['nullable'] = format_nullable_display
    app.jinja_env.filters['metric'] = format_metric_display


# Example usage and testing
if __name__ == "__main__":
    # Test the formatting functions
    test_dt = datetime.now(timezone.utc)
    print("🕐 Terrascan Datetime Formatting Examples:")
    print(f"  Standard:      {format_datetime_utc(test_dt)}")
    print(f"  Date only:     {format_date_only(test_dt)}")
    print(f"  Time only:     {format_time_only(test_dt)}")
    print(f"  ISO format:    {format_iso(test_dt)}")
    print(f"  Time ago:      {time_ago(test_dt)}")
    print(f"  Current UTC:   {current_utc_formatted()}") 
