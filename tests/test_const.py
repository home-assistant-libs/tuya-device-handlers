"""Test constants."""

import pytest

from tuya_device_handlers.const import DPType


@pytest.mark.parametrize(
    ("current_type", "expected_type"),
    [
        # Regular
        ("Boolean", DPType.BOOLEAN),
        ("Enum", DPType.ENUM),
        ("Integer", DPType.INTEGER),
        ("Json", DPType.JSON),
        ("Raw", DPType.RAW),
        ("String", DPType.STRING),
        # Special
        ("bitmap", DPType.BITMAP),
        ("bool", DPType.BOOLEAN),
        ("enum", DPType.ENUM),
        ("json", DPType.JSON),
        ("raw", DPType.RAW),
        ("string", DPType.STRING),
        ("value", DPType.INTEGER),
        # Invalid
        ("boolbool", None),
    ],
)
def test_dptype_parser(
    current_type: str,
    expected_type: DPType | None,
) -> None:
    """Test DPType.try_parse."""
    assert DPType.try_parse(current_type) is expected_type
