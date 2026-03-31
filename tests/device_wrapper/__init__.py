"""Test DeviceWrapper classes"""

from typing import Any

from tuya_sharing import CustomerDevice, DeviceFunction, DeviceStatusRange

from tuya_device_handlers.device_wrapper.base import DeviceWrapper

from .. import send_device_update


def send_wrapper_update(
    device: CustomerDevice,
    wrapper: DeviceWrapper[Any],
    updated_status_properties: dict[str, Any] | None = None,
    dp_timestamps: dict[str, int] | None = None,
) -> None:
    """Send device update, and trigger skip_update"""
    send_device_update(device, updated_status_properties)
    if updated_status_properties:
        wrapper.skip_update(
            device, list(updated_status_properties), dp_timestamps
        )


def inject_dpcode_status(
    mock_device: CustomerDevice, dpcode: str, state: Any
) -> None:
    mock_device.status[dpcode] = state


def inject_dpcode_function(
    mock_device: CustomerDevice, dpcode: str, dptype: str, values: str
) -> None:
    mock_device.function[dpcode] = DeviceFunction(
        {"code": dpcode, "type": dptype, "values": values}
    )


def inject_dpcode_status_range(
    mock_device: CustomerDevice, dpcode: str, dptype: str, values: str
) -> None:
    mock_device.status_range[dpcode] = DeviceStatusRange(
        {"code": dpcode, "type": dptype, "values": values}
    )


def inject_dpcode(
    mock_device: CustomerDevice,
    dpcode: str,
    state: Any,
    *,
    dptype: str | None = None,
    values: str = "{}",
    skip_function: bool = False,
    skip_status_range: bool = False,
) -> None:
    inject_dpcode_status(mock_device, dpcode, state)
    if dptype is not None:
        if not skip_function:
            inject_dpcode_function(mock_device, dpcode, dptype, values)
        if not skip_status_range:
            inject_dpcode_status_range(mock_device, dpcode, dptype, values)
