"""Test DeviceWrapper classes"""

from typing import Any

import pytest
from tuya_sharing import (  # type: ignore[import-untyped]
    CustomerDevice,
    DeviceFunction,
    DeviceStatusRange,
)

from tuya_device_handlers.device_wrapper.common import (
    DPCodeTypeInformationWrapper,
)
from tuya_device_handlers.device_wrapper.cover import (
    ControlBackModePercentageMappingWrapper,
)
from tuya_device_handlers.device_wrapper.extended import (
    DPCodeInvertedPercentageWrapper,
    DPCodePercentageWrapper,
)

try:
    from typeguard import suppress_type_checks  # type: ignore[import-not-found]
except ImportError:
    from contextlib import nullcontext

    suppress_type_checks = nullcontext


@pytest.fixture()
def inject_control_back_mode(mock_device: CustomerDevice) -> None:
    mock_device.function["control_back_mode"] = DeviceFunction(
        {
            "code": "master_state",
            "type": "Enum",
            "values": '{"range": ["forward", "back"]}',
        }
    )
    mock_device.status_range["control_back_mode"] = DeviceStatusRange(
        {
            "code": "control_back_mode",
            "type": "Enum",
            "values": '{"range": ["forward", "back"]}',
        }
    )
    mock_device.status["control_back_mode"] = "forward"


@pytest.mark.usefixtures("inject_control_back_mode")
@pytest.mark.parametrize(
    ("wrapper_type", "status_updates", "expected_device_status"),
    [
        (DPCodePercentageWrapper, {"demo_integer": 200}, 20),
        (DPCodeInvertedPercentageWrapper, {"demo_integer": 200}, 80),
        (ControlBackModePercentageMappingWrapper, {"demo_integer": 200}, 80),
        (
            ControlBackModePercentageMappingWrapper,
            {"demo_integer": 200, "control_back_mode": "back"},
            20,
        ),
        (
            ControlBackModePercentageMappingWrapper,
            {"demo_integer": 200, "control_back_mode": "forward"},
            80,
        ),
    ],
)
def test_read_device_status(
    wrapper_type: type[DPCodeTypeInformationWrapper[Any, Any]],
    status_updates: dict[str, Any],
    expected_device_status: Any,
    mock_device: CustomerDevice,
) -> None:
    """Test read_device_status."""
    dpcode = "demo_integer"
    mock_device.status.update(status_updates)
    wrapper = wrapper_type.find_dpcode(mock_device, dpcode)

    assert wrapper
    assert wrapper.read_device_status(mock_device) == expected_device_status

    # All wrappers return None if status is None
    mock_device.status[dpcode] = None
    assert wrapper.read_device_status(mock_device) is None

    # All wrappers return None if status is missing
    mock_device.status.pop(dpcode)
    assert wrapper.read_device_status(mock_device) is None
