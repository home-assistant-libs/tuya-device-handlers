"""Helpers for diagnostics and debugging."""

import datetime as dt
from typing import Any

from tuya_sharing import CustomerDevice, DeviceFunction, DeviceStatusRange

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.const import DEVICE_WARNINGS


def _format_functions(functions: dict[str, DeviceFunction]) -> dict[str, Any]:
    """Represent a Tuya device as a dictionary."""
    return {
        function.code: {
            "type": function.type,
            "value": function.values,
        }
        for function in functions.values()
    }


def _format_status_ranges(
    status_range: dict[str, DeviceStatusRange],
) -> dict[str, Any]:
    """Represent a Tuya device as a dictionary."""
    return {
        status_range.code: {
            "type": status_range.type,
            "value": status_range.values,
            "report_type": status_range.report_type,
        }
        for status_range in status_range.values()
    }


def customer_device_as_dict(device: CustomerDevice) -> dict[str, Any]:
    """Represent a Tuya device as a dictionary."""
    quirk = TUYA_QUIRKS_REGISTRY.get_quirk_for_device(device)

    data = {
        "id": device.id,
        "name": device.name,
        "category": device.category,
        "product_id": device.product_id,
        "product_name": device.product_name,
        "online": device.online,
        "sub": device.sub,
        "time_zone": device.time_zone,
        "active_time": dt.datetime.fromtimestamp(
            device.active_time, tz=dt.UTC
        ).isoformat(),
        "create_time": dt.datetime.fromtimestamp(
            device.create_time, tz=dt.UTC
        ).isoformat(),
        "update_time": dt.datetime.fromtimestamp(
            device.update_time, tz=dt.UTC
        ).isoformat(),
        "function": _format_functions(device.function),
        "local_strategy": device.local_strategy,
        "status_range": _format_status_ranges(device.status_range),
        "status": device.status,
        "set_up": device.set_up,
        "support_local": device.support_local,
        "quirk": (
            f"{quirk.quirk_file}:{quirk.quirk_file_line}" if quirk else None
        ),
        "warnings": DEVICE_WARNINGS.get(device.id),
    }
    if quirk:
        if hasattr(quirk, "original_function"):
            data["original_function"] = _format_functions(
                quirk.original_function
            )
        if hasattr(quirk, "original_local_strategy"):
            data["original_local_strategy"] = quirk.original_local_strategy
        if hasattr(quirk, "original_status_range"):
            data["original_status_range"] = _format_status_ranges(
                quirk.original_status_range
            )

    return data
