"""Test fixtures"""

from unittest.mock import Mock

import pytest
from tuya_sharing import CustomerDevice, DeviceFunction, DeviceStatusRange

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.devices import register_tuya_quirks
from tuya_device_handlers.registry import QuirksRegistry


@pytest.fixture(scope="module")
def filled_quirks_registry() -> QuirksRegistry:
    """Mock an old config entry that can be migrated."""
    register_tuya_quirks()
    return TUYA_QUIRKS_REGISTRY


@pytest.fixture(name="mock_device")
def device_fixture() -> CustomerDevice:
    """Fixture for a customer device."""
    mock_device = Mock(spec=CustomerDevice)
    mock_device.id = "device_id"
    mock_device.product_id = "product_id"

    mock_device.status = {
        "demo_bitmap": 3,
        "demo_boolean": True,
        "demo_enum": "customize_scene",
        "demo_integer": 123,
        "demo_integer_sum": 234,
        "demo_json": '{"h": 210,"s": 1000,"v": 1000}',
        "demo_raw": "fwceBQF/DgACAX8UAAQB",
        "demo_string": "a_string",
    }
    mock_device.function = {
        "demo_bitmap": DeviceFunction(
            code="demo_bitmap",
            type="Bitmap",
            values='{"label": ["motor_fault"]}',
        ),
        "demo_bitmap_missing_values": DeviceFunction(
            code="demo_bitmap_missing_values",
            type="Bitmap",
            values="{}",
        ),
        "demo_boolean": DeviceFunction(
            code="demo_boolean",
            type="Boolean",
            values="{}",
        ),
        "demo_enum": DeviceFunction(
            code="demo_enum",
            type="Enum",
            values='{"range": ["scene", "customize_scene", "colour"]}',
        ),
        "demo_enum_missing_values": DeviceFunction(
            code="demo_enum_missing_values",
            type="Enum",
            values="{}",
        ),
        "demo_integer": DeviceFunction(
            code="demo_integer",
            type="Integer",
            values='{"unit": "%","min": 0,"max": 1000,"scale": 1,"step": 1}',
        ),
        "demo_integer_missing_values": DeviceFunction(
            code="demo_integer_missing_values",
            type="Integer",
            values="{}",
        ),
        "demo_integer_sum": DeviceFunction(
            code="demo_integer_sum",
            type="Integer",
            values='{"unit": "%","min": 0,"max": 1000,"scale": 1,"step": 1}',
        ),
        "demo_json": DeviceFunction(
            code="demo_json",
            type="Json",
            values="{}",
        ),
        "demo_raw": DeviceFunction(
            code="demo_raw",
            type="Raw",
            values="{}",
        ),
        "demo_string": DeviceFunction(
            code="demo_json",
            type="String",
            values="{}",
        ),
    }
    mock_device.status_range = {
        "demo_bitmap": DeviceStatusRange(
            code="demo_bitmap",
            type="Bitmap",
            values='{"label": ["motor_fault"]}',
        ),
        "demo_boolean": DeviceStatusRange(
            code="demo_boolean",
            type="Boolean",
            values="{}",
        ),
        "demo_enum": DeviceStatusRange(
            code="demo_enum",
            type="Enum",
            values='{"range": ["scene", "customize_scene", "colour"]}',
        ),
        "demo_alarm_enum": DeviceStatusRange(
            code="demo_alarm",
            type="Enum",
            values='{"range": ["alarm", "normal"]}',
        ),
        "demo_integer": DeviceStatusRange(
            code="demo_integer",
            type="Integer",
            values='{"unit": "%","min": 0,"max": 1000,"scale": 1,"step": 1}',
        ),
        "demo_integer_sum": DeviceStatusRange(
            code="demo_integer_sum",
            type="Integer",
            values='{"unit": "%","min": 0,"max": 1000,"scale": 1,"step": 1}',
            report_type="sum",
        ),
        "demo_json": DeviceStatusRange(
            code="demo_json",
            type="Json",
            values="{}",
        ),
        "demo_raw": DeviceStatusRange(
            code="demo_raw",
            type="Raw",
            values="{}",
        ),
        "demo_string": DeviceStatusRange(
            code="demo_json",
            type="String",
            values="{}",
        ),
    }
    return mock_device
