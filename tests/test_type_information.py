"""Test TypeInformation classes."""

import dataclasses
from typing import Any
from unittest.mock import patch

import pytest
from syrupy.assertion import SnapshotAssertion
from tuya_sharing import CustomerDevice

from tuya_device_handlers.const import DEVICE_WARNINGS
from tuya_device_handlers.type_information import (
    BitmapTypeInformation,
    BooleanTypeInformation,
    EnumTypeInformation,
    IntegerTypeInformation,
    JsonTypeInformation,
    RawTypeInformation,
    StringTypeInformation,
    TypeInformation,
)


@pytest.mark.parametrize(
    ("type_information_type", "dpcode"),
    [
        (BitmapTypeInformation, "demo_bitmap"),
        (BooleanTypeInformation, "demo_boolean"),
        (EnumTypeInformation, "demo_enum"),
        (IntegerTypeInformation, "demo_integer"),
        (JsonTypeInformation, "demo_json"),
        (RawTypeInformation, "demo_raw"),
        (StringTypeInformation, "demo_string"),
    ],
)
def test_valid_type_information(
    dpcode: str | tuple[str] | None,
    type_information_type: type[TypeInformation[Any]],
    snapshot: SnapshotAssertion,
    mock_device: CustomerDevice,
) -> None:
    """Test find_dpcode."""
    type_information = type_information_type.find_dpcode(mock_device, dpcode)

    assert type_information
    assert dataclasses.asdict(type_information) == snapshot


@pytest.mark.parametrize(
    ("type_information_type", "dpcode"),
    [
        # Invalid (missing type details)
        (BitmapTypeInformation, "demo_bitmap_missing_values"),
        (EnumTypeInformation, "demo_enum_missing_values"),
        (IntegerTypeInformation, "demo_integer_missing_values"),
        # Invalid => return None
        (BitmapTypeInformation, "invalid"),
        (BooleanTypeInformation, "invalid"),
        (EnumTypeInformation, "invalid"),
        (IntegerTypeInformation, "invalid"),
        (JsonTypeInformation, "invalid"),
        (RawTypeInformation, "invalid"),
        (StringTypeInformation, "invalid"),
        (StringTypeInformation, ("some",)),
        (StringTypeInformation, None),
    ],
)
def test_invalid_type_information(
    dpcode: str | tuple[str] | None,
    type_information_type: type[TypeInformation[Any]],
    mock_device: CustomerDevice,
) -> None:
    """Test find_dpcode."""
    type_information = type_information_type.find_dpcode(mock_device, dpcode)

    assert type_information is None


def test_integer_scaling(mock_device: CustomerDevice) -> None:
    """Test scale_value/scale_value_back."""
    type_information = IntegerTypeInformation.find_dpcode(
        mock_device, "demo_integer"
    )

    assert type_information
    assert type_information.scale == 1
    assert type_information.scale_value(150) == 15
    assert type_information.scale_value_back(15) == 150


@pytest.mark.parametrize(
    (
        "type_information_type",
        "dpcode",
        "value",
        "warning_key",
        "warning_diplayed",
    ),
    [
        (
            BitmapTypeInformation,
            "demo_bitmap",
            "some_string",
            "invalid_bitmap|demo_bitmap|some_string",
            "Found invalid BITMAP value `some_string` (<class 'str'>) "
            "for datapoint `demo_bitmap` in product id `product_id`",
        ),
        (
            BooleanTypeInformation,
            "demo_boolean",
            "some_string",
            "boolean_out_range|demo_boolean|some_string",
            "Found invalid BOOLEAN value `some_string` (<class 'str'>) "
            "for datapoint `demo_boolean` in product id `product_id`",
        ),
        (
            EnumTypeInformation,
            "demo_enum",
            "some_string",
            "enum_out_range|demo_enum|some_string",
            "Found invalid ENUM value `some_string` (<class 'str'>) "
            "for datapoint `demo_enum` in product id `product_id`",
        ),
        (
            IntegerTypeInformation,
            "demo_integer",
            "some_string",
            "integer_out_range|demo_integer|some_string",
            "Found invalid INTEGER value `some_string` (<class 'str'>) "
            "for datapoint `demo_integer` in product id `product_id`",
        ),
        (
            JsonTypeInformation,
            "demo_json",
            "some_string",
            "invalid_json|demo_json",
            "Found invalid JSON value `some_string` (<class 'str'>) "
            "for datapoint `demo_json` in product id `product_id`",
        ),
        (
            RawTypeInformation,
            "demo_raw",
            "some_string",
            "invalid_raw|demo_raw",
            "Found invalid RAW value `some_string` (<class 'str'>) "
            "for datapoint `demo_raw` in product id `product_id`",
        ),
    ],
)
@patch.dict(DEVICE_WARNINGS, {}, clear=True)
def test_log_invalid_value(
    dpcode: str,
    type_information_type: type[TypeInformation[Any]],
    mock_device: CustomerDevice,
    value: Any,
    warning_key: str,
    warning_diplayed: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test find_dpcode."""
    mock_device.status[dpcode] = value
    type_information = type_information_type.find_dpcode(mock_device, dpcode)

    assert type_information
    assert type_information.read_device_value(mock_device) is None
    if warning_key is not None:
        assert warning_key in DEVICE_WARNINGS[mock_device.id]
    assert warning_diplayed in caplog.text

    # Second read should not fail (but also not log again)
    caplog.clear()
    assert type_information.read_device_value(mock_device) is None
    assert warning_diplayed not in caplog.text
