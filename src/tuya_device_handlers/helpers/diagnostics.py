"""Helpers for diagnostics and debugging."""

import datetime as dt
from typing import Any

from tuya_sharing import CustomerDevice

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.device_wrapper import DEVICE_WARNINGS
from tuya_device_handlers.registry import DeviceQuirkProtocol


def _get_function(
    device: CustomerDevice, quirk: DeviceQuirkProtocol | None
) -> dict[str, Any]:
    """Represent a Tuya device as a dictionary."""
    functions = device.function
    if quirk and hasattr(quirk, "original_function"):
        functions = quirk.original_function

    return {
        function.code: {
            "type": function.type,
            "value": function.values,
        }
        for function in functions.values()
    }


def _get_local_strategy(
    device: CustomerDevice, quirk: DeviceQuirkProtocol | None
) -> dict[int, dict[str, Any]]:
    """Represent a Tuya device as a dictionary."""
    local_strategy = device.local_strategy
    if quirk and hasattr(quirk, "original_local_strategy"):
        local_strategy = quirk.original_local_strategy

    if local_strategy is None:
        return None  # type: ignore[return-value]
    return {**local_strategy}


def _get_status_range(
    device: CustomerDevice, quirk: DeviceQuirkProtocol | None
) -> dict[str, Any]:
    """Represent a Tuya device as a dictionary."""
    status_range = device.status_range
    if quirk and hasattr(quirk, "original_status_range"):
        status_range = quirk.original_status_range

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
        "function": _get_function(device, quirk),
        "local_strategy": _get_local_strategy(device, quirk),
        "status_range": _get_status_range(device, quirk),
        "status": {**device.status},
        "set_up": device.set_up,
        "support_local": device.support_local,
        "quirk": (
            f"{quirk.quirk_file}:{quirk.quirk_file_line}" if quirk else None
        ),
        "warnings": DEVICE_WARNINGS.get(device.id),
    }

    return data
