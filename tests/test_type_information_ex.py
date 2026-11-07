"""Test extended TypeInformation classes."""

import pytest
from tuya_sharing import CustomerDevice, DeviceStatusRange

from tuya_device_handlers.device_wrapper.extended import (
    DPCodeInvertedPercentageWrapper,
)
from tuya_device_handlers.type_information import (
    IntegerTypeInformation,
    PrepareSetValueError,
)
from tuya_device_handlers.type_information_ex import (
    BackModeInvertedIntegerTypeInformationEx,
    ForwardModeInvertedIntegerTypeInformationEx,
    InvertedIntegerTypeInformationEx,
)


def _find(device: CustomerDevice) -> InvertedIntegerTypeInformationEx:
    """Return the inverted type information for ``demo_integer``."""
    # demo_integer: min=0, max=1000, scale=1, step=1 => scaled range 0-100.
    type_information = InvertedIntegerTypeInformationEx.find_dpcode(
        device, "demo_integer"
    )
    assert type_information is not None
    return type_information


def test_read_inverts_within_range(mock_device: CustomerDevice) -> None:
    """Read returns ``scale_value(max) - value``."""
    mock_device.status["demo_integer"] = 123
    type_information = _find(mock_device)
    # scale_value(1000) - scale_value(123) = 100 - 12.3 = 87.7
    value = type_information.read_device_value(mock_device)
    assert value == pytest.approx(87.7)


def test_read_handles_missing_value(mock_device: CustomerDevice) -> None:
    """Read returns ``None`` (not inverted) when no value is reported."""
    del mock_device.status["demo_integer"]
    type_information = _find(mock_device)
    assert type_information.read_device_value(mock_device) is None


def test_write_inverts_within_range(mock_device: CustomerDevice) -> None:
    """Write sends the inverted raw value to the device."""
    type_information = _find(mock_device)
    # scale_value(1000) - 70 = 30 => scale_value_back(30) = 300
    assert type_information.prepare_set_value(mock_device, 70) == 300


def test_write_delegates_non_numeric(mock_device: CustomerDevice) -> None:
    """Write delegates non-numeric values to the parent for validation."""
    type_information = _find(mock_device)
    with pytest.raises(PrepareSetValueError):
        type_information.prepare_set_value(mock_device, "stop")


def test_inversion_round_trips(mock_device: CustomerDevice) -> None:
    """A value read back after writing returns to its original."""
    type_information = _find(mock_device)
    raw = type_information.prepare_set_value(mock_device, 70)
    mock_device.status["demo_integer"] = raw
    assert type_information.read_device_value(mock_device) == pytest.approx(70)


@pytest.mark.parametrize(
    "type_information_cls",
    [
        BackModeInvertedIntegerTypeInformationEx,
        ForwardModeInvertedIntegerTypeInformationEx,
    ],
)
@pytest.mark.parametrize(
    ("control_back_mode", "inverted_cls"),
    [
        ("back", BackModeInvertedIntegerTypeInformationEx),
        ("forward", ForwardModeInvertedIntegerTypeInformationEx),
        (None, ForwardModeInvertedIntegerTypeInformationEx),
    ],
)
def test_mode_inverted(
    mock_device: CustomerDevice,
    type_information_cls: type[InvertedIntegerTypeInformationEx],
    control_back_mode: str | None,
    inverted_cls: type[InvertedIntegerTypeInformationEx],
) -> None:
    """The value is only inverted in the mode of the class."""
    mock_device.status["demo_integer"] = 123
    mock_device.status["control_back_mode"] = control_back_mode
    type_information = type_information_cls.find_dpcode(
        mock_device, "demo_integer"
    )
    assert type_information is not None

    is_inverted = type_information_cls is inverted_cls
    assert type_information.read_device_value(mock_device) == pytest.approx(
        87.7 if is_inverted else 12.3
    )
    assert type_information.prepare_set_value(mock_device, 70) == (
        300 if is_inverted else 700
    )


@pytest.mark.parametrize(
    "type_information_cls",
    [
        BackModeInvertedIntegerTypeInformationEx,
        ForwardModeInvertedIntegerTypeInformationEx,
    ],
)
def test_mode_inverted_edge_values(
    mock_device: CustomerDevice,
    type_information_cls: type[InvertedIntegerTypeInformationEx],
) -> None:
    """Missing values and invalid writes are handled in both modes."""
    for control_back_mode in ("back", "forward"):
        mock_device.status["control_back_mode"] = control_back_mode
        mock_device.status.pop("demo_integer", None)
        type_information = type_information_cls.find_dpcode(
            mock_device, "demo_integer"
        )
        assert type_information is not None
        assert type_information.read_device_value(mock_device) is None
        with pytest.raises(PrepareSetValueError):
            type_information.prepare_set_value(mock_device, "invalid")


@pytest.mark.parametrize(
    ("type_information_cls", "back_position", "forward_position"),
    [
        (IntegerTypeInformation, 80, 80),
        (InvertedIntegerTypeInformationEx, 20, 20),
        (BackModeInvertedIntegerTypeInformationEx, 20, 80),
        (ForwardModeInvertedIntegerTypeInformationEx, 80, 20),
    ],
)
def test_combinations_through_cover_wrapper(
    mock_device: CustomerDevice,
    type_information_cls: type[IntegerTypeInformation],
    back_position: int,
    forward_position: int,
) -> None:
    """All four combinations are reachable through the cover wrapper."""
    mock_device.status["demo_integer"] = 200
    type_information = type_information_cls.find_dpcode(
        mock_device, "demo_integer"
    )
    assert type_information is not None
    wrapper = DPCodeInvertedPercentageWrapper("demo_integer", type_information)

    mock_device.status["control_back_mode"] = "back"
    assert wrapper.read_device_status(mock_device) == back_position
    mock_device.status["control_back_mode"] = "forward"
    assert wrapper.read_device_status(mock_device) == forward_position


def test_inverts_within_nonzero_range(mock_device: CustomerDevice) -> None:
    """The value is reflected around both bounds of the range."""
    mock_device.status_range["demo_integer"] = DeviceStatusRange(
        code="demo_integer",
        type="Integer",
        values='{"min":10,"max":90,"scale":0,"step":1}',
    )
    mock_device.status["demo_integer"] = 10
    type_information = _find(mock_device)

    assert type_information.read_device_value(mock_device) == 90
    assert type_information.prepare_set_value(mock_device, 25) == 75
