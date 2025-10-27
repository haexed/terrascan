#!/usr/bin/env python3
"""
Smart Metric Value Type for TERRASCAN
Handles NULL values, formatting, and status logic internally
"""

class MetricValue:
    """
    Smart value type that handles NULL/missing data gracefully

    Usage:
        temp = MetricValue(25.6, unit="°C", thresholds={'danger': 30, 'warning': 25})
        print(temp)  # "25.6°C"
        temp.status  # "warning"

        missing = MetricValue(None)
        print(missing)  # "🤷 NO DATA"
        missing.status  # "no_data"
    """

    def __init__(self, value, unit="", decimal_places=1,
                 thresholds=None, no_data_emoji="🤷", no_data_text="NO DATA"):
        self.raw_value = value
        self.unit = unit
        self.decimal_places = decimal_places
        self.thresholds = thresholds or {}
        self.no_data_emoji = no_data_emoji
        self.no_data_text = no_data_text

    @property
    def has_value(self):
        """Check if this metric has actual data"""
        return self.raw_value is not None

    @property
    def value(self):
        """Get the numeric value, or None if missing"""
        return self.raw_value

    @property
    def formatted_value(self):
        """Get formatted numeric value without unit"""
        if not self.has_value:
            return None

        if isinstance(self.raw_value, (int, float)):
            if self.decimal_places == 0:
                return str(int(self.raw_value))
            else:
                return f"{self.raw_value:.{self.decimal_places}f}"
        return str(self.raw_value)

    @property
    def status(self):
        """Get status based on thresholds"""
        if not self.has_value:
            return "no_data"

        if not self.thresholds or not isinstance(self.raw_value, (int, float)):
            return "normal"

        value = self.raw_value

        # Check thresholds in order of severity
        if 'critical' in self.thresholds and value >= self.thresholds['critical']:
            return "critical"
        elif 'danger' in self.thresholds and value >= self.thresholds['danger']:
            return "danger"
        elif 'warning' in self.thresholds and value >= self.thresholds['warning']:
            return "warning"
        elif 'moderate' in self.thresholds and value >= self.thresholds['moderate']:
            return "moderate"
        else:
            return "good"

    @property
    def css_class(self):
        """Get CSS class for status"""
        status_map = {
            'no_data': 'text-muted',
            'critical': 'text-danger',
            'danger': 'text-danger',
            'warning': 'text-warning',
            'moderate': 'text-info',
            'good': 'text-success',
            'normal': 'text-info'
        }
        return status_map.get(self.status, 'text-muted')

    @property
    def badge_class(self):
        """Get badge CSS class for status"""
        status_map = {
            'no_data': 'bg-secondary',
            'critical': 'bg-danger',
            'danger': 'bg-danger',
            'warning': 'bg-warning',
            'moderate': 'bg-info',
            'good': 'bg-success',
            'normal': 'bg-info'
        }
        return status_map.get(self.status, 'bg-secondary')

    def __str__(self):
        """String representation - this is the magic method for template display"""
        if not self.has_value:
            return f"{self.no_data_emoji} {self.no_data_text}"

        formatted = self.formatted_value
        return f"{formatted}{self.unit}" if formatted else f"{self.no_data_emoji} {self.no_data_text}"

    def __repr__(self):
        return f"MetricValue({self.raw_value}, unit='{self.unit}', status='{self.status}')"

    def __bool__(self):
        """Boolean evaluation - True if has value"""
        return self.has_value

    def __eq__(self, other):
        """Equality comparison"""
        if isinstance(other, MetricValue):
            return self.raw_value == other.raw_value
        return self.raw_value == other

    def __lt__(self, other):
        """Less than comparison"""
        if not self.has_value:
            return False
        if isinstance(other, MetricValue):
            return self.raw_value < other.raw_value if other.has_value else False
        return self.raw_value < other

    def __gt__(self, other):
        """Greater than comparison"""
        if not self.has_value:
            return False
        if isinstance(other, MetricValue):
            return self.raw_value > other.raw_value if other.has_value else True
        return self.raw_value > other


# Common metric configurations
FIRE_COUNT_CONFIG = {
    'unit': '',
    'decimal_places': 0,
    'thresholds': {'danger': 100, 'warning': 20}
}

TEMPERATURE_CONFIG = {
    'unit': '°C',
    'decimal_places': 1,
    'thresholds': {'danger': 30, 'warning': 25}
}

AIR_QUALITY_CONFIG = {
    'unit': ' μg/m³',
    'decimal_places': 2,
    'thresholds': {'critical': 75, 'danger': 35, 'warning': 15}
}

OCEAN_TEMP_CONFIG = {
    'unit': '°C',
    'decimal_places': 1,
    'thresholds': {'danger': 28, 'warning': 26}
}

COUNT_CONFIG = {
    'unit': '',
    'decimal_places': 0
}


def create_metric_value(value, metric_type="default", **kwargs):
    """Factory function to create MetricValue with common configurations"""
    configs = {
        'fire_count': FIRE_COUNT_CONFIG,
        'temperature': TEMPERATURE_CONFIG,
        'air_quality': AIR_QUALITY_CONFIG,
        'ocean_temp': OCEAN_TEMP_CONFIG,
        'count': COUNT_CONFIG
    }

    config = configs.get(metric_type, {})
    config.update(kwargs)  # Allow overrides

    return MetricValue(value, **config)


# Example usage and testing
if __name__ == "__main__":
    print("🧪 TERRASCAN MetricValue Testing:")

    # Test with real values
    fire_count = create_metric_value(150, 'fire_count')
    print(f"Fire count: {fire_count} (status: {fire_count.status}, class: {fire_count.css_class})")

    temp = create_metric_value(27.3, 'ocean_temp')
    print(f"Ocean temp: {temp} (status: {temp.status})")

    air_quality = create_metric_value(45.2, 'air_quality')
    print(f"Air quality: {air_quality} (status: {air_quality.status})")

    # Test with NULL values
    missing_temp = create_metric_value(None, 'temperature')
    print(f"Missing temp: {missing_temp} (status: {missing_temp.status})")

    missing_count = create_metric_value(None, 'count')
    print(f"Missing count: {missing_count}")

    # Test comparisons
    print(f"Fire count > 100: {fire_count > 100}")
    print(f"Missing temp > 20: {missing_temp > 20}")