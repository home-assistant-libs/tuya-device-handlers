"""Tests for tuya-device-handlers."""

from datetime import datetime
import json
from typing import Any

from tuya_sharing import CustomerDevice, DeviceFunction, DeviceStatusRange


def _date_as_timestamp(date_string: str | None) -> int:
    # "2023-06-21T04:29:09+00:00"
    if date_string is None:
        return 0
    return int(datetime.fromisoformat(date_string).timestamp())


def _get_functions(details: dict[str, Any]) -> dict[str, DeviceFunction]:
    function_details = details["function"]
    if "original_function" in details:
        function_details = details["original_function"]

    return {
        key: DeviceFunction(
            code=value.get("code", key),
            type=value["type"],
            values=(
                values
                if isinstance(values := value["value"], str)
                else json.dumps(value["value"])
            ),
        )
        for key, value in function_details.items()
    }


def _get_local_strategy(
    details: dict[str, Any],
) -> dict[int, dict[str, Any]] | None:
    local_strategy_details = details.get("local_strategy")
    if "original_local_strategy" in details:
        local_strategy_details = details["original_local_strategy"]
    if local_strategy_details is None:
        return None

    return {int(key): value for key, value in local_strategy_details.items()}


def _get_status_range(details: dict[str, Any]) -> dict[str, DeviceStatusRange]:
    status_range_details = details["status_range"]
    if "original_status_range" in details:
        status_range_details = details["original_status_range"]

    return {
        key: DeviceStatusRange(
            code=value.get("code", key),
            type=value["type"],
            values=(
                values
                if isinstance(values := value["value"], str)
                else json.dumps(value["value"])
            ),
            report_type=value.get("report_type"),
        )
        for key, value in status_range_details.items()
    }


def create_device(fixture_filename: str) -> CustomerDevice:
    """Create a Tuya CustomerDevice."""
    with open(f"tests/fixtures/devices/{fixture_filename}") as fixture_file:
        details: dict[str, Any] = json.load(fixture_file)
    device = CustomerDevice(
        # Use reverse of the product_id for testing
        id=details["product_id"].replace("_", "")[::-1],
        name=details["name"],
        category=details["category"],
        product_id=details["product_id"],
        product_name=details["product_name"],
        online=details["online"],
        sub=details.get("sub"),
        time_zone=details.get("time_zone"),
        active_time=_date_as_timestamp(details.get("active_time")),
        create_time=_date_as_timestamp(details.get("create_time")),
        update_time=_date_as_timestamp(details.get("update_time")),
        set_up=details.get("set_up"),
        support_local=details.get("support_local"),
        mqtt_connected=details.get("mqtt_connected"),
        function=_get_functions(details),
        local_strategy=_get_local_strategy(details),
        status_range=_get_status_range(details),
        status=details["status"],
    )

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
