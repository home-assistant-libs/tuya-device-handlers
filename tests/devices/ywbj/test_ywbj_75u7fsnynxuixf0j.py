"""Tests for Tuya quirk 75u7fsnynxuixf0j (Smoke Detector with Temp/Humidity)."""

from tuya_device_handlers.test_utils import assert_device_mapping


def test_ywbj_75u7fsnynxuixf0j_mapping():
    """Test that DPs 23 and 24 map to temperature and humidity correctly."""
    assert_device_mapping(
        product_id="75u7fsnynxuixf0j",
        status={
            "1": "normal",
            "15": 80,
            "16": False,
            "23": 189,  # Represents 18.9 °C with scale=1
            "24": 64,   # Represents 64 %
        },
        expected_states={
            "smoke_sensor_status": "normal",
            "battery_percentage": 80,
            "muffling": False,
            "temp_current": 18.9,
            "humidity_value": 64,
        },
    )
  
