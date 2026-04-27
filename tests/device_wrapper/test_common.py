"""Test DeviceWrapper classes"""

import base64
from typing import Any
from unittest.mock import patch

import pytest
from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper import (
    DEVICE_WARNINGS,
    SetValueOutOfRangeError,
)
from tuya_device_handlers.device_wrapper.common import (
    DPCodeBitmapWrapper,
    DPCodeBooleanWrapper,
    DPCodeEnumWrapper,
    DPCodeIntegerWrapper,
    DPCodeJsonWrapper,
    DPCodeRawWrapper,
    DPCodeStringWrapper,
    DPCodeTypeInformationWrapper,
)

try:
    from typeguard import suppress_type_checks  # type: ignore[import-not-found]
except ImportError:
    from contextlib import nullcontext

    suppress_type_checks = nullcontext


def test_dpcode_not_found(
    mock_device: CustomerDevice,
) -> None:
    """Test find_dpcode with invalid dpcode."""
    type_information = DPCodeIntegerWrapper.find_dpcode(mock_device, "invalid")

    assert type_information is None


@pytest.mark.parametrize(
    ("wrapper_type", "dpcode", "expected_device_status"),
    [
        (DPCodeBitmapWrapper, "demo_bitmap", 3),
        (DPCodeBooleanWrapper, "demo_boolean", True),
        (DPCodeEnumWrapper, "demo_enum", "customize_scene"),
        (DPCodeIntegerWrapper, "demo_integer", 12.3),
        (DPCodeJsonWrapper, "demo_json", {"h": 210, "s": 1000, "v": 1000}),
        (
            DPCodeRawWrapper,
            "demo_raw",
            base64.b64decode("fwceBQF/DgACAX8UAAQB"),
        ),
        (DPCodeStringWrapper, "demo_string", "a_string"),
    ],
)
def test_read_device_status(
    dpcode: str,
    wrapper_type: type[DPCodeTypeInformationWrapper[Any, Any, Any]],
    expected_device_status: Any,
    mock_device: CustomerDevice,
) -> None:
    """Test read_device_status."""
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
    ("wrapper_type", "dpcode", "status", "warning_key"),
    [
        (
            DPCodeBooleanWrapper,
            "demo_boolean",
            "hot",
            "boolean_out_range|demo_boolean|hot",
        ),
        (
            DPCodeEnumWrapper,
            "demo_enum",
            "hot",
            "enum_out_range|demo_enum|hot",
        ),
        (
            DPCodeIntegerWrapper,
            "demo_integer",
            1230,
            "integer_out_range|demo_integer|1230",
        ),
    ],
)
@patch.dict(DEVICE_WARNINGS, {}, clear=True)
def test_read_invalid_device_status(
    dpcode: str,
    wrapper_type: type[DPCodeTypeInformationWrapper[Any, Any, Any]],
    status: Any,
    warning_key: str,
    mock_device: CustomerDevice,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test read_device_status."""
    mock_device.status[dpcode] = status
    wrapper = wrapper_type.find_dpcode(mock_device, dpcode)

    expected_log = "please report this defect to Tuya support"

    assert not DEVICE_WARNINGS
    assert expected_log not in caplog.text

    assert wrapper
    assert wrapper.read_device_status(mock_device) is None
    assert (dev_warnings := DEVICE_WARNINGS.get(mock_device.id))
    assert warning_key in dev_warnings  # warning added
    assert expected_log in caplog.text  # first log entry

    caplog.clear()
    assert wrapper.read_device_status(mock_device) is None
    assert len(dev_warnings) == 1  # no added warning
    assert expected_log not in caplog.text  # no second log entry


@pytest.mark.parametrize(
    ("wrapper_type", "dpcode", "value", "expected"),
    [
        (
            DPCodeBooleanWrapper,
            "demo_boolean",
            False,
            [{"code": "demo_boolean", "value": False}],
        ),
        (
            DPCodeEnumWrapper,
            "demo_enum",
            "colour",
            [{"code": "demo_enum", "value": "colour"}],
        ),
        (
            DPCodeIntegerWrapper,
            "demo_integer",
            11.3,
            [{"code": "demo_integer", "value": 113}],
        ),
    ],
)
def test_get_update_commands(
    dpcode: str,
    wrapper_type: type[DPCodeTypeInformationWrapper[Any, Any, Any]],
    value: Any,
    expected: list[dict[str, Any]],
    mock_device: CustomerDevice,
) -> None:
    """Test read_device_status."""
    wrapper = wrapper_type.find_dpcode(mock_device, dpcode)

    assert wrapper
    assert wrapper.get_update_commands(mock_device, value) == expected


@pytest.mark.parametrize(
    ("wrapper_type", "dpcode", "value"),
    [
        (DPCodeBooleanWrapper, "demo_boolean", "h"),
        (DPCodeEnumWrapper, "demo_enum", "hot"),
        (DPCodeIntegerWrapper, "demo_integer", 111.3),
    ],
)
def test_get_update_commands_value_error(
    dpcode: str,
    wrapper_type: type[DPCodeTypeInformationWrapper[Any, Any, Any]],
    value: Any,
    mock_device: CustomerDevice,
) -> None:
    """Test get_update_commands (ValueError)."""
    wrapper = wrapper_type.find_dpcode(mock_device, dpcode)

    assert wrapper
    with suppress_type_checks(), pytest.raises(SetValueOutOfRangeError):
        wrapper.get_update_commands(mock_device, value)


def test_enum_details(mock_device: CustomerDevice) -> None:
    """Test scale_value/scale_value_back."""
    wrapper = DPCodeEnumWrapper.find_dpcode(mock_device, "demo_enum")

    assert wrapper
    assert wrapper.options == ["scene", "customize_scene", "colour"]


def test_integer_details(mock_device: CustomerDevice) -> None:
    """Test scale_value/scale_value_back."""
    wrapper = DPCodeIntegerWrapper.find_dpcode(mock_device, "demo_integer")

    assert wrapper
    assert wrapper.max_value == 100
    assert wrapper.min_value == 0
    assert wrapper.value_step == 0.1
    assert wrapper.native_unit == "%"


def test_skip_update(mock_device: CustomerDevice) -> None:
    """Test skip_update."""
    wrapper = DPCodeIntegerWrapper.find_dpcode(mock_device, "demo_integer")

    assert wrapper
    assert wrapper.skip_update(mock_device, [], None) is True
    assert wrapper.skip_update(mock_device, ["a", "b", "c"], {}) is True
    assert (
        wrapper.skip_update(mock_device, ["a", "demo_integer", "c"], {})
        is False
    )
    # Ensure compatibility when dp_timestamps is not passed up
    assert wrapper.skip_update(mock_device, []) is True
    assert wrapper.skip_update(mock_device, ["a", "b", "c"]) is True
    assert wrapper.skip_update(mock_device, ["a", "demo_integer", "c"]) is False
