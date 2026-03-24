"""Tests for tuya-device-handlers."""

from datetime import datetime
import json
from typing import Any
from unittest.mock import MagicMock

from tuya_sharing import (  # type: ignore[import-untyped]
    CustomerDevice,
    DeviceFunction,
    DeviceStatusRange,
)


def _date_as_timestamp(date_string: str) -> int:
    # "2023-06-21T04:29:09+00:00"
    return int(datetime.fromisoformat(date_string).timestamp())


def create_device(fixture_filename: str) -> CustomerDevice:
    """Create a Tuya CustomerDevice."""
    with open(f"tests/fixtures/devices/{fixture_filename}") as fixture_file:
        details: dict[str, Any] = json.load(fixture_file)
    device = MagicMock(spec=CustomerDevice)

    # Use reverse of the product_id for testing
    device.id = details["product_id"].replace("_", "")[::-1]

    device.name = details["name"]
    device.category = details["category"]
    device.product_id = details["product_id"]
    device.product_name = details["product_name"]
    device.online = details["online"]
    device.sub = details.get("sub")
    device.time_zone = details.get("time_zone")
    device.active_time = details.get("active_time")
    if device.active_time:
        device.active_time = _date_as_timestamp(device.active_time)
    device.create_time = details.get("create_time")
    if device.create_time:
        device.create_time = _date_as_timestamp(device.create_time)
    device.update_time = details.get("update_time")
    if device.update_time:
        device.update_time = _date_as_timestamp(device.update_time)
    device.support_local = details.get("support_local")
    device.local_strategy = details.get("local_strategy")
    device.mqtt_connected = details.get("mqtt_connected")

    device.function = {
        key: DeviceFunction(
            code=value.get("code"),
            type=value["type"],
            values=(
                values
                if isinstance(values := value["value"], str)
                else json.dumps(value["value"])
            ),
        )
        for key, value in details["function"].items()
    }
    device.status_range = {
        key: DeviceStatusRange(
            code=value.get("code"),
            type=value["type"],
            values=(
                values
                if isinstance(values := value["value"], str)
                else json.dumps(value["value"])
            ),
            report_type=value.get("report_type"),
        )
        for key, value in details["status_range"].items()
    }
    device.status = details["status"]
    for key, value in device.status.items():
        # Some devices do not provide a status_range for all status DPs
        # Others set the type as String in status_range and as Json in function
        if (
            (dp_type := device.status_range.get(key)) and dp_type.type == "Json"
        ) or ((dp_type := device.function.get(key)) and dp_type.type == "Json"):
            device.status[key] = json.dumps(value)
        if value == "**REDACTED**":
            # It was redacted, which may cause issue with b64decode
            device.status[key] = ""
    return device


def send_device_update(
    device: CustomerDevice,
    updated_status_properties: dict[str, Any] | None = None,
) -> None:
    """Send device update"""
    property_list: list[str] = []
    if updated_status_properties:
        for key, value in updated_status_properties.items():
            if key not in device.status:
                raise ValueError(
                    f"Property {key} not found in device status: {device.status}"
                )
            device.status[key] = value
            property_list.append(key)
