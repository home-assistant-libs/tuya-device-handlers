"""Test DeviceWrapper classes."""

from typing import Any
from unittest.mock import patch

import pytest
from tuya_sharing import CustomerDevice

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder.device_quirk import DeviceQuirk
from tuya_device_handlers.device_wrapper.common import (
    DPCodeTypeInformationWrapper,
)
from tuya_device_handlers.device_wrapper.cover import (
    ControlBackModeInvertedPercentageMappingWrapper,
    ControlBackModePercentageMappingWrapper,
    CoverClosedEnumWrapper,
    CoverInstructionBooleanWrapper,
    CoverInstructionEnumWrapper,
    CoverInstructionSpecialEnumWrapper,
)
from tuya_device_handlers.device_wrapper.extended import (
    DPCodeInvertedPercentageWrapper,
    DPCodePercentageWrapper,
)
from tuya_device_handlers.helpers.homeassistant import TuyaCoverAction

from . import inject_dpcode


@pytest.mark.parametrize(
    ("wrapper_type", "dpcode", "status_updates", "expected_device_status"),
    [
        (DPCodePercentageWrapper, "demo_integer", {"demo_integer": 200}, 20),
        (
            DPCodeInvertedPercentageWrapper,
            "demo_integer",
            {"demo_integer": 200},
            80,
        ),
        (
            ControlBackModePercentageMappingWrapper,
            "demo_integer",
            {"demo_integer": 200},
            80,
        ),
        (
            ControlBackModePercentageMappingWrapper,
            "demo_integer",
            {"demo_integer": 200, "control_back_mode": "back"},
            20,
        ),
        (
            ControlBackModePercentageMappingWrapper,
            "demo_integer",
            {"demo_integer": 200, "control_back_mode": "forward"},
            80,
        ),
        (
            ControlBackModeInvertedPercentageMappingWrapper,
            "demo_integer",
            {"demo_integer": 200},
            20,
        ),
        (
            ControlBackModeInvertedPercentageMappingWrapper,
            "demo_integer",
            {"demo_integer": 200, "control_back_mode": "back"},
            80,
        ),
        (
            ControlBackModeInvertedPercentageMappingWrapper,
            "demo_integer",
            {"demo_integer": 200, "control_back_mode": "forward"},
            20,
        ),
        (
            CoverClosedEnumWrapper,
            "cover_situation",
            {"cover_situation": "fully_open"},
            False,
        ),
        (
            CoverClosedEnumWrapper,
            "cover_situation",
            {"cover_situation": "fully_close"},
            True,
        ),
    ],
)
def test_read_device_status(
    dpcode: str,
    wrapper_type: type[DPCodeTypeInformationWrapper[Any, Any, Any]],
    status_updates: dict[str, Any],
    expected_device_status: Any,
    mock_device: CustomerDevice,
) -> None:
    """Test read_device_status."""
    inject_dpcode(
        mock_device,
        "control_back_mode",
        "forward",
        dptype="Enum",
        values='{"range": ["forward", "back"]}',
    )
    inject_dpcode(
        mock_device,
        "cover_situation",
        "fully_open",
        dptype="Enum",
        values='{"range": ["fully_open", "fully_close"]}',
        skip_function=True,
    )
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
            "legacy_control",
            TuyaCoverAction.OPEN,
            [{"code": "legacy_control", "value": "FZ"}],
        ),
        (
            CoverInstructionSpecialEnumWrapper,
            "legacy_control",
            TuyaCoverAction.CLOSE,
            [{"code": "legacy_control", "value": "ZZ"}],
        ),
        (
            CoverInstructionSpecialEnumWrapper,
            "legacy_control",
            TuyaCoverAction.STOP,
            [{"code": "legacy_control", "value": "STOP"}],
        ),
    ],
)
def test_cover_action_command(
    wrapper_type: type[DPCodeTypeInformationWrapper[Any, Any, Any]],
    dpcode: str,
    action: TuyaCoverAction,
    expected: list[dict[str, Any]],
    mock_device: CustomerDevice,
) -> None:
    """Test get_update_commands."""
    inject_dpcode(
        mock_device,
        "control",
        "stop",
        dptype="Enum",
        values='{"range": ["open", "stop", "close"]}',
    )
    inject_dpcode(
        mock_device,
        "legacy_control",
        "stop",
        dptype="Enum",
        values='{"range": ["FZ", "ZZ", "STOP"]}',
    )
    wrapper = wrapper_type.find_dpcode(mock_device, dpcode)

    assert wrapper
    assert wrapper.get_update_commands(mock_device, action) == expected


def _register_wrapper_override(device: CustomerDevice, dpcode: str) -> None:
    (
        DeviceQuirk()
        .applies_to(product_id=device.product_id)
        .override_dpid_wrapper_cls(
            dpid=2,
            dpcode=dpcode,
            wrapper_cls=ControlBackModeInvertedPercentageMappingWrapper,
        )
        .register(TUYA_QUIRKS_REGISTRY)
    )


@pytest.mark.parametrize(
    "requested_wrapper",
    [
        DPCodePercentageWrapper,
        DPCodeInvertedPercentageWrapper,
        ControlBackModePercentageMappingWrapper,
    ],
)
def test_find_dpcode_applies_quirk_wrapper_override(
    mock_device: CustomerDevice,
    requested_wrapper: type[DPCodePercentageWrapper],
) -> None:
    """A quirk's wrapper wins, whichever wrapper the caller asks for."""
    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        _register_wrapper_override(mock_device, "demo_integer")
        wrapper = requested_wrapper.find_dpcode(mock_device, "demo_integer")

    assert type(wrapper) is ControlBackModeInvertedPercentageMappingWrapper
    assert wrapper.dpcode == "demo_integer"


def test_find_dpcode_ignores_override_for_other_dpcode(
    mock_device: CustomerDevice,
) -> None:
    """A quirk's wrapper only applies to its own datapoint."""
    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        _register_wrapper_override(mock_device, "other")
        wrapper = DPCodeInvertedPercentageWrapper.find_dpcode(
            mock_device, "demo_integer"
        )

    assert type(wrapper) is DPCodeInvertedPercentageWrapper


def test_find_dpcode_returns_none_for_missing_dpcode(
    mock_device: CustomerDevice,
) -> None:
    """No wrapper is built for a datapoint the device doesn't have."""
    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        _register_wrapper_override(mock_device, "bad")
        assert (
            DPCodeInvertedPercentageWrapper.find_dpcode(mock_device, "bad")
            is None
        )
