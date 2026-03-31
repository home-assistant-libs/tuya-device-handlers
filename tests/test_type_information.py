"""Test TypeInformation classes"""

import dataclasses

import pytest
from syrupy.assertion import SnapshotAssertion
from tuya_sharing import CustomerDevice

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
    type_information_type: type[TypeInformation],
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
    type_information_type: type[TypeInformation],
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
