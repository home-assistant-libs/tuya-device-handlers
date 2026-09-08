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
    ElectricityApparentPowerHexStringWrapper,
    ElectricityApparentPowerJsonWrapper,
    ElectricityApparentPowerRawWrapper,
    ElectricityPowerFactorHexStringWrapper,
    ElectricityPowerFactorJsonWrapper,
    ElectricityPowerFactorRawWrapper,
    ElectricityReactivePowerHexStringWrapper,
    ElectricityReactivePowerJsonWrapper,
    ElectricityReactivePowerRawWrapper,
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
            "dlq_cnpkf4xdmd9v49iq.json",
            "phase_a",
            ElectricityReactivePowerRawWrapper,
        ),
        (
            "dlq_cnpkf4xdmd9v49iq.json",
            "phase_a",
            ElectricityApparentPowerRawWrapper,
        ),
        (
            "dlq_cnpkf4xdmd9v49iq.json",
            "phase_a",
            ElectricityPowerFactorRawWrapper,
        ),
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
        (
            "zndb_uqzhc4bx5zqwpg2m.json",
            "phase_s1",
            ElectricityReactivePowerHexStringWrapper,
        ),
        (
            "zndb_uqzhc4bx5zqwpg2m.json",
            "phase_s1",
            ElectricityApparentPowerHexStringWrapper,
        ),
        (
            "zndb_uqzhc4bx5zqwpg2m.json",
            "phase_s1",
            ElectricityPowerFactorHexStringWrapper,
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


@pytest.mark.parametrize(
    "wrapper_type",
    [
        ElectricityReactivePowerRawWrapper,
        ElectricityApparentPowerRawWrapper,
        ElectricityPowerFactorRawWrapper,
    ],
)
def test_get_optional_electricity_definition_unsupported(
    wrapper_type: type[DPCodeTypeInformationWrapper],
) -> None:
    """Test optional definitions are omitted for a real legacy RAW frame."""
    device = create_device("zndb_ze8faryrxr0glqnn.json")

    assert not get_default_definition(device, "phase_a", (wrapper_type,))


@pytest.mark.parametrize(
    ("fixture_filename", "dpcode", "wrapper_type"),
    [
        (
            "zndb_ze8faryrxr0glqnn.json",
            "phase_a",
            ElectricityReactivePowerRawWrapper,
        ),
        (
            "zndb_iow5ux77dxy3yrpj.json",
            "phase_a",
            ElectricityReactivePowerJsonWrapper,
        ),
        (
            "zndb_uqzhc4bx5zqwpg2m.json",
            "phase_s1",
            ElectricityReactivePowerHexStringWrapper,
        ),
    ],
)
def test_get_optional_electricity_definition_with_unknown_status(
    fixture_filename: str,
    dpcode: str,
    wrapper_type: type[DPCodeTypeInformationWrapper],
) -> None:
    """Test missing startup status does not hide optional definitions."""
    device = create_device(fixture_filename)
    device.status.pop(dpcode)

    assert get_default_definition(device, dpcode, (wrapper_type,))
