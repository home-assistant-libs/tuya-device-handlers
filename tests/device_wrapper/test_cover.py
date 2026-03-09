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
    CoverInstructionBooleanWrapper,
    CoverInstructionEnumWrapper,
    CoverInstructionSpecialEnumWrapper,
)
from tuya_device_handlers.device_wrapper.extended import (
    DPCodeInvertedPercentageWrapper,
    DPCodePercentageWrapper,
)
from tuya_device_handlers.helpers.homeassistant import TuyaCoverAction

try:
    from typeguard import suppress_type_checks  # type: ignore[import-not-found]
except ImportError:
    from contextlib import nullcontext

    suppress_type_checks = nullcontext


@pytest.fixture()
def inject_control_back_mode(mock_device: CustomerDevice) -> None:
    mock_device.function["control_back_mode"] = DeviceFunction(
        {
            "code": "control_back_mode",
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


@pytest.fixture()
def inject_control(mock_device: CustomerDevice) -> None:
    mock_device.function["control"] = DeviceFunction(
        {
            "code": "control",
            "type": "Enum",
            "values": '{"range": ["open", "stop", "close"]}',
        }
    )
    mock_device.status_range["control"] = DeviceStatusRange(
        {
            "code": "control",
            "type": "Enum",
            "values": '{"range": ["open", "stop", "close"]}',
        }
    )
    mock_device.status["control"] = "stop"


@pytest.fixture()
def inject_legacy_control(mock_device: CustomerDevice) -> None:
    mock_device.function["legacy_control"] = DeviceFunction(
        {
            "code": "legacy_control",
            "type": "Enum",
            "values": '{"range": ["open", "stop", "close"]}',
        }
    )
    mock_device.status_range["legacy_control"] = DeviceStatusRange(
        {
            "code": "legacy_control",
            "type": "Enum",
            "values": '{"range": ["open", "stop", "close"]}',
        }
    )
    mock_device.status["legacy_control"] = "stop"


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


@pytest.mark.usefixtures("inject_control")
@pytest.mark.parametrize(
    ("wrapper_type", "dpcode", "action", "expected"),
    [
        (
            CoverInstructionBooleanWrapper,
            "demo_boolean",
            TuyaCoverAction.OPEN,
            [{"code": "demo_boolean", "value": True}],
        ),
        (
            CoverInstructionBooleanWrapper,
            "demo_boolean",
            TuyaCoverAction.CLOSE,
            [{"code": "demo_boolean", "value": False}],
        ),
        (
            CoverInstructionEnumWrapper,
            "control",
            TuyaCoverAction.OPEN,
            [{"code": "control", "value": "open"}],
        ),
        (
            CoverInstructionEnumWrapper,
            "control",
            TuyaCoverAction.CLOSE,
            [{"code": "control", "value": "close"}],
        ),
        (
            CoverInstructionEnumWrapper,
            "control",
            TuyaCoverAction.STOP,
            [{"code": "control", "value": "stop"}],
        ),
        (
            CoverInstructionSpecialEnumWrapper,
            "control",
            TuyaCoverAction.OPEN,
            [{"code": "control", "value": "FZ"}],
        ),
        (
            CoverInstructionSpecialEnumWrapper,
            "control",
            TuyaCoverAction.CLOSE,
            [{"code": "control", "value": "ZZ"}],
        ),
        (
            CoverInstructionSpecialEnumWrapper,
            "control",
            TuyaCoverAction.STOP,
            [{"code": "control", "value": "STOP"}],
        ),
    ],
)
def test_get_update_commands(
    wrapper_type: type[DPCodeTypeInformationWrapper[Any, Any]],
    dpcode: str,
    action: TuyaCoverAction,
    expected: list[dict[str, Any]],
    mock_device: CustomerDevice,
) -> None:
    """Test get_update_commands."""
    wrapper = wrapper_type.find_dpcode(mock_device, dpcode)

    assert wrapper
    assert wrapper.get_update_commands(mock_device, action) == expected
