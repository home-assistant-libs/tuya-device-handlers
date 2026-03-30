"""Helpers for diagnostics and debugging."""

import datetime as dt
from typing import Any

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from tuya_device_handlers.device_wrapper import DEVICE_WARNINGS


def customer_device_as_dict(device: CustomerDevice) -> dict[str, Any]:
    """Represent a Tuya device as a dictionary."""
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
        "function": {},
        "status_range": {},
        "status": {},
        "set_up": device.set_up,
        "support_local": device.support_local,
        "local_strategy": device.local_strategy,
        "warnings": DEVICE_WARNINGS.get(device.id),
    }
    # Gather Tuya states
    for dpcode, value in device.status.items():
        data["status"][dpcode] = value

    # Gather Tuya functions
    for function in device.function.values():
        data["function"][function.code] = {
            "type": function.type,
            "value": function.values,
        }

    # Gather Tuya status ranges
    for status_range in device.status_range.values():
        data["status_range"][status_range.code] = {
            "type": status_range.type,
            "value": status_range.values,
            "report_type": status_range.report_type,
        }

    return data
