"""Tests for sensor definition."""

import pytest

from tests import create_device
from tuya_device_handlers.definition.sensor import get_default_definition
from tuya_device_handlers.device_wrapper.common import (
    DPCodeEnumWrapper,
    DPCodeIntegerWrapper,
    DPCodeTypeInformationWrapper,
)
from tuya_device_handlers.device_wrapper.sensor import (
    DeltaIntegerWrapper,
    ElectricityApparentPowerJsonWrapper,
    ElectricityPowerFactorJsonWrapper,
    ElectricityReactivePowerJsonWrapper,
)


@pytest.mark.parametrize(
    ("fixture_filename", "dpcode", "lookup_type", "wrapper_type"),
    [
        (
            "cs_zibqa9dutqyaxym2.json",
            "countdown_left",
            (DPCodeIntegerWrapper,),
            DPCodeIntegerWrapper,
        ),
        (
            "cs_zibqa9dutqyaxym2.json",
            "countdown_left",
            None,
            DPCodeIntegerWrapper,
        ),
        (
            "cs_zibqa9dutqyaxym2.json",
            "countdown_set",
            (DPCodeEnumWrapper,),
            DPCodeEnumWrapper,
        ),
        ("cs_zibqa9dutqyaxym2.json", "countdown_set", None, DPCodeEnumWrapper),
        ("cz_guitoc9iylae4axs.json", "add_ele", None, DeltaIntegerWrapper),
    ],
)
def test_get_default_definition(
    fixture_filename: str,
    dpcode: str,
    lookup_type: tuple[type, ...] | None,
    wrapper_type: type,
) -> None:
    """Test get_default_definition."""
    device = create_device(fixture_filename)
    assert (definition := get_default_definition(device, dpcode, lookup_type))  # ty: ignore[invalid-argument-type]
    assert isinstance(definition.sensor_wrapper, wrapper_type)


@pytest.mark.parametrize(
    "lookup_type",
    [
        None,
        (DPCodeEnumWrapper,),
    ],
)
def test_get_default_definition_fails(
    lookup_type: tuple[type, ...] | None,
) -> None:
    """Test get_default_definition."""
    device = create_device("cs_zibqa9dutqyaxym2.json")
    assert not get_default_definition(device, "bad", lookup_type)  # ty: ignore[invalid-argument-type]


@pytest.mark.parametrize(
    ("fixture_filename", "dpcode", "wrapper_type"),
    [
        (
            "zndb_iow5ux77dxy3yrpj.json",
            "phase_a",
            ElectricityReactivePowerJsonWrapper,
        ),
        (
            "zndb_iow5ux77dxy3yrpj.json",
            "phase_a",
            ElectricityApparentPowerJsonWrapper,
        ),
        (
            "zndb_iow5ux77dxy3yrpj.json",
            "phase_a",
            ElectricityPowerFactorJsonWrapper,
        ),
    ],
)
def test_get_optional_electricity_definition_supported(
    fixture_filename: str,
    dpcode: str,
    wrapper_type: type[DPCodeTypeInformationWrapper],
) -> None:
    """Test optional electricity definitions with real device payloads."""
    device = create_device(fixture_filename)

    assert get_default_definition(device, dpcode, (wrapper_type,))


def test_get_optional_electricity_definition_with_unknown_status() -> None:
    """Test missing startup status does not hide optional definitions."""
    device = create_device("zndb_iow5ux77dxy3yrpj.json")
    device.status.pop("phase_a")

    assert get_default_definition(
        device, "phase_a", (ElectricityReactivePowerJsonWrapper,)
    )
