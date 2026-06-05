"""Test utils."""

from tuya_sharing import CustomerDevice

from tuya_device_handlers.type_information import IntegerTypeInformation
from tuya_device_handlers.utils import RemapHelper


def test_remap_helper() -> None:
    """Test RemapHelper static remap_value method."""
    assert round(RemapHelper.remap_value(25, 0, 100, 0, 255)) == 64
    assert round(RemapHelper.remap_value(64, 0, 255, 0, 100)) == 25
    assert (
        round(RemapHelper.remap_value(25, 0, 100, 0, 255, reverse=True)) == 191
    )
    assert (
        round(RemapHelper.remap_value(64, 0, 255, 0, 100, reverse=True)) == 75
    )


def test_remap_helper_from_type_information(
    mock_device: CustomerDevice,
) -> None:
    """Test RemapHelper from TypeInformation.

    `demo_integer` has min=0, max=1000, scale=1 — so the helper's
    source range is the *scaled* range (0..100), matching the values
    returned by `TypeInformation.read_device_value`.
    """
    type_information = IntegerTypeInformation.find_dpcode(
        mock_device, "demo_integer"
    )
    assert type_information
    remap_helper = RemapHelper.from_type_information(type_information, 0, 255)

    assert round(remap_helper.remap_value_from(100), 1) == 39.2
    assert round(remap_helper.remap_value_to(39.2), 1) == 100
    assert round(remap_helper.remap_value_from(100, reverse=True), 1) == 60.8
    assert round(remap_helper.remap_value_to(60.8, reverse=True), 1) == 100


def test_remap_helper_from_function_data() -> None:
    """Test RemapHelper from function_data."""
    remap_helper = RemapHelper.from_function_data(
        {"min": 0, "max": 100}, 0, 255
    )

    assert round(remap_helper.remap_value_from(100), 1) == 39.2
    assert round(remap_helper.remap_value_to(39.2), 1) == 100
    assert round(remap_helper.remap_value_from(100, reverse=True), 1) == 60.8
    assert round(remap_helper.remap_value_to(60.8, reverse=True), 1) == 100
