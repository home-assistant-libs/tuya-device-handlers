"""Test the unified Raw/String electricity device wrappers."""

import base64
from copy import deepcopy
import json
from typing import Any

import pytest
from tuya_sharing import CustomerDevice

from tests import create_device
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder.device_quirk import DeviceQuirk
from tuya_device_handlers.device_wrapper.common import (
    DPCodeTypeInformationWrapper,
)
from tuya_device_handlers.device_wrapper.electricity import (
    ElectricityApparentPowerWrapper,
    ElectricityCurrentWrapper,
    ElectricityPowerFactorWrapper,
    ElectricityPowerWrapper,
    ElectricityReactivePowerWrapper,
    ElectricityVoltageWrapper,
    _ElectricityTypeInformation,
)
from tuya_device_handlers.device_wrapper.extended import (
    DPCodeJsonDictAttributeWrapper,
)
from tuya_device_handlers.device_wrapper.sensor import (
    ElectricityApparentPowerHexStringWrapper,
    ElectricityApparentPowerRawWrapper,
    ElectricityCurrentHexStringWrapper,
    ElectricityCurrentRawWrapper,
    ElectricityPowerFactorHexStringWrapper,
    ElectricityPowerFactorRawWrapper,
    ElectricityPowerHexStringWrapper,
    ElectricityPowerRawWrapper,
    ElectricityReactivePowerHexStringWrapper,
    ElectricityReactivePowerRawWrapper,
    ElectricityVoltageHexStringWrapper,
    ElectricityVoltageRawWrapper,
)
from tuya_device_handlers.type_information import (
    IntegerTypeInformation,
    JsonTypeInformation,
    RawTypeInformation,
    StringTypeInformation,
)

from . import inject_dpcode, inject_dpcode_function, inject_dpcode_status_range

# Captured metering frames.
#
# The v02 frame is the `phase_s1` status of the Home Assistant core test
# fixture `zndb_qxlwffgv8avf5rrw` (a String datapoint). The handlers fixture
# `zndb_uqzhc4bx5zqwpg2m` reports the same v02 layout, and
# `dlq_cnpkf4xdmd9v49iq` reports it as a base64 Raw datapoint.
#
# Layout (big-endian): version, length, voltage (0.1 V), current (mA),
# active power (W), reactive power (var), apparent power (VA), power factor
# (0.01), and for v02 a sign bitmap.
V02_FRAME = "020F08FD00044C0000D20000320000DC5F00"
_V02_PAYLOAD = V02_FRAME[4:-2]
# v01 has the version and length header, but no sign bitmap.
V01_FRAME = f"010F{_V02_PAYLOAD}"
# The legacy layout carries voltage, current and active power only.
LEGACY_FRAME = _V02_PAYLOAD[:16]

# Sign bitmap bits of the v02 layout. Apparent power and voltage are
# magnitudes and have no sign bit.
_SIGN_BITS = {
    "current": 0x01,
    "power": 0x02,
    "reactive_power": 0x04,
    "power_factor": 0x08,
}

_WRAPPER_CASES: list[
    tuple[type[DPCodeJsonDictAttributeWrapper[Any]], str, float]
] = [
    (ElectricityCurrentWrapper, "current", 1.1),
    (ElectricityPowerWrapper, "power", 0.21),
    (ElectricityVoltageWrapper, "voltage", 230.1),
    (ElectricityReactivePowerWrapper, "reactive_power", 0.05),
    (ElectricityApparentPowerWrapper, "apparent_power", 0.22),
    (ElectricityPowerFactorWrapper, "power_factor", 0.95),
]
_WRAPPER_IDS = [case[0].__name__ for case in _WRAPPER_CASES]
_WRAPPERS = [case[0] for case in _WRAPPER_CASES]
_VALUE_CASES = [(case[0], case[2]) for case in _WRAPPER_CASES]
_LEGACY_WRAPPERS = [
    (ElectricityCurrentRawWrapper, ElectricityCurrentHexStringWrapper),
    (ElectricityPowerRawWrapper, ElectricityPowerHexStringWrapper),
    (ElectricityVoltageRawWrapper, ElectricityVoltageHexStringWrapper),
    (
        ElectricityReactivePowerRawWrapper,
        ElectricityReactivePowerHexStringWrapper,
    ),
    (
        ElectricityApparentPowerRawWrapper,
        ElectricityApparentPowerHexStringWrapper,
    ),
    (ElectricityPowerFactorRawWrapper, ElectricityPowerFactorHexStringWrapper),
]

# The legacy layout cannot provide reactive power, apparent power or the
# power factor, so only the first three wrappers apply to it.
_LEGACY_VALUE_CASES = _VALUE_CASES[:3]

# Both encodings of the same frames must decode to the same values.
_EQUIVALENCE_CASES = [
    (wrapper_type, frame)
    for frame in (V02_FRAME, V01_FRAME)
    for wrapper_type, _, _ in _WRAPPER_CASES
] + [(wrapper_type, LEGACY_FRAME) for wrapper_type, _, _ in _WRAPPER_CASES[:3]]
_EQUIVALENCE_IDS = [
    f"{wrapper_type.__name__}-{name}"
    for wrapper_type, frame in _EQUIVALENCE_CASES
    if (
        name := "legacy"
        if frame == LEGACY_FRAME
        else "v01"
        if frame == V01_FRAME
        else "v02"
    )
]


def _inject_frame(
    device: CustomerDevice,
    dpcode: str,
    frame: str,
    *,
    raw: bool,
) -> None:
    """Inject a metering frame as a Raw (base64) or String (hex) datapoint."""
    if raw:
        state = base64.b64encode(bytes.fromhex(frame)).decode()
        inject_dpcode(device, dpcode, state, dptype="Raw")
    else:
        inject_dpcode(device, dpcode, frame, dptype="String")


def _find(
    device: CustomerDevice,
    wrapper_type: type[DPCodeJsonDictAttributeWrapper[Any]],
    dpcode: str,
) -> DPCodeJsonDictAttributeWrapper[Any]:
    """Find a wrapper, asserting that it was found."""
    wrapper = wrapper_type.find_dpcode(device, dpcode)
    assert wrapper is not None
    return wrapper


def _source(
    wrapper: DPCodeJsonDictAttributeWrapper[Any],
) -> RawTypeInformation | StringTypeInformation | JsonTypeInformation:
    """Return the source DP's type information."""
    normalized = wrapper.type_information
    assert isinstance(normalized, _ElectricityTypeInformation)
    return normalized.source_type_information


def _read(
    device: CustomerDevice,
    wrapper_type: type[DPCodeJsonDictAttributeWrapper[Any]],
    dpcode: str,
) -> Any:
    """Read a wrapper value, asserting that the wrapper was found."""
    return _find(device, wrapper_type, dpcode).read_device_status(device)


@pytest.mark.parametrize(
    ("wrapper_type", "expected"), _VALUE_CASES, ids=_WRAPPER_IDS
)
@pytest.mark.parametrize("raw", [False, True], ids=["string", "raw"])
def test_find_dpcode_accepts_both_encodings(
    mock_device: CustomerDevice,
    wrapper_type: type[DPCodeJsonDictAttributeWrapper[Any]],
    expected: float,
    raw: bool,
) -> None:
    """A unified wrapper is found for a Raw and for a String datapoint."""
    dpcode = "phase_1" if raw else "phase_s1"
    _inject_frame(mock_device, dpcode, V02_FRAME, raw=raw)

    wrapper = _find(mock_device, wrapper_type, dpcode)

    expected_type = RawTypeInformation if raw else StringTypeInformation
    assert isinstance(_source(wrapper), expected_type)
    assert wrapper.dpcode == dpcode
    assert wrapper.read_device_status(mock_device) == expected


@pytest.mark.parametrize(
    ("wrapper_type", "expected"), _VALUE_CASES, ids=_WRAPPER_IDS
)
def test_read_v01_frame(
    mock_device: CustomerDevice,
    wrapper_type: type[DPCodeJsonDictAttributeWrapper[Any]],
    expected: float,
) -> None:
    """The v01 layout without a sign bitmap is decoded."""
    _inject_frame(mock_device, "phase_s1", V01_FRAME, raw=False)

    assert _read(mock_device, wrapper_type, "phase_s1") == expected


@pytest.mark.parametrize(
    ("wrapper_type", "expected"), _LEGACY_VALUE_CASES, ids=_WRAPPER_IDS[:3]
)
def test_read_legacy_frame(
    mock_device: CustomerDevice,
    wrapper_type: type[DPCodeJsonDictAttributeWrapper[Any]],
    expected: float,
) -> None:
    """The legacy layout is decoded for the attributes it carries."""
    _inject_frame(mock_device, "phase_s1", LEGACY_FRAME, raw=False)

    assert _read(mock_device, wrapper_type, "phase_s1") == expected


@pytest.mark.parametrize("wrapper_type", _WRAPPERS[3:], ids=_WRAPPER_IDS[3:])
def test_legacy_frame_missing_attribute(
    mock_device: CustomerDevice,
    wrapper_type: type[DPCodeJsonDictAttributeWrapper[Any]],
) -> None:
    """No wrapper is found for an attribute the legacy frame lacks."""
    _inject_frame(mock_device, "phase_s1", LEGACY_FRAME, raw=False)

    assert wrapper_type.find_dpcode(mock_device, "phase_s1") is None


@pytest.mark.parametrize(
    "sign_bits", [0x00, 0x01, 0x02, 0x04, 0x08, 0x03, 0x0F]
)
def test_v02_sign_bitmap(
    mock_device: CustomerDevice,
    sign_bits: int,
) -> None:
    """The v02 sign bitmap negates the attributes it marks."""
    frame = f"{V02_FRAME[:-2]}{sign_bits:02X}"
    _inject_frame(mock_device, "phase_s1", frame, raw=False)

    for wrapper_type, attribute, value in _WRAPPER_CASES:
        expected = value
        if sign_bits & _SIGN_BITS.get(attribute, 0):
            expected = -value
        assert _read(mock_device, wrapper_type, "phase_s1") == expected


@pytest.mark.parametrize(
    ("wrapper_type", "frame"),
    _EQUIVALENCE_CASES,
    ids=_EQUIVALENCE_IDS,
)
def test_raw_and_string_encodings_are_equivalent(
    mock_device: CustomerDevice,
    wrapper_type: type[DPCodeJsonDictAttributeWrapper[Any]],
    frame: str,
) -> None:
    """The same frame decodes identically through both datapoint types."""
    _inject_frame(mock_device, "phase_1", frame, raw=True)
    _inject_frame(mock_device, "phase_s1", frame, raw=False)

    raw_wrapper = _find(mock_device, wrapper_type, "phase_1")
    string_wrapper = _find(mock_device, wrapper_type, "phase_s1")

    assert isinstance(_source(raw_wrapper), RawTypeInformation)
    assert isinstance(_source(string_wrapper), StringTypeInformation)
    assert raw_wrapper.read_device_status(
        mock_device
    ) == string_wrapper.read_device_status(mock_device)


@pytest.mark.parametrize("wrapper_type", _WRAPPERS, ids=_WRAPPER_IDS)
def test_truncated_raw_payload_not_found(
    mock_device: CustomerDevice,
    wrapper_type: type[DPCodeJsonDictAttributeWrapper[Any]],
) -> None:
    """A Raw payload shorter than the legacy layout provides no attribute."""
    # Valid base64, but only three bytes of payload.
    state = base64.b64encode(b"\x00\x00\x00").decode()
    inject_dpcode(mock_device, "phase_1", state, dptype="Raw")

    assert wrapper_type.find_dpcode(mock_device, "phase_1") is None


@pytest.mark.parametrize("wrapper_type", _WRAPPERS, ids=_WRAPPER_IDS)
def test_invalid_hex_string_not_found(
    mock_device: CustomerDevice,
    wrapper_type: type[DPCodeJsonDictAttributeWrapper[Any]],
) -> None:
    """A String payload which is not hex provides no attribute."""
    _inject_frame(mock_device, "phase_s1", "not-hex", raw=False)

    assert wrapper_type.find_dpcode(mock_device, "phase_s1") is None


@pytest.mark.parametrize("wrapper_type", _WRAPPERS, ids=_WRAPPER_IDS)
def test_unparsable_payload_reads_none(
    mock_device: CustomerDevice,
    wrapper_type: type[DPCodeJsonDictAttributeWrapper[Any]],
) -> None:
    """An unparsable payload is read as None."""
    _inject_frame(mock_device, "phase_1", V02_FRAME, raw=True)
    wrapper = _find(mock_device, wrapper_type, "phase_1")

    mock_device.status["phase_1"] = "AAA="
    assert wrapper.read_device_status(mock_device) is None

    # Invalid base64 is treated as "not reported" when looking for a
    # wrapper, so the wrapper still exists and reads None.
    mock_device.status["phase_1"] = "!!!"
    assert wrapper.read_device_status(mock_device) is None

    _inject_frame(mock_device, "phase_s1", V02_FRAME, raw=False)
    string_wrapper = _find(mock_device, wrapper_type, "phase_s1")
    mock_device.status["phase_s1"] = "not-hex"
    assert string_wrapper.read_device_status(mock_device) is None


@pytest.mark.parametrize("wrapper_type", _WRAPPERS, ids=_WRAPPER_IDS)
@pytest.mark.parametrize("raw", [False, True], ids=["string", "raw"])
@pytest.mark.parametrize("status", [None, ""], ids=["none", "empty"])
def test_not_reported_value_assumes_supported(
    mock_device: CustomerDevice,
    wrapper_type: type[DPCodeJsonDictAttributeWrapper[Any]],
    status: str | None,
    raw: bool,
) -> None:
    """A datapoint without a reported value is assumed to be supported."""
    dpcode = "phase_1" if raw else "phase_s1"
    inject_dpcode(
        mock_device, dpcode, status, dptype="Raw" if raw else "String"
    )

    wrapper = _find(mock_device, wrapper_type, dpcode)
    assert wrapper.read_device_status(mock_device) is None
    _inject_frame(mock_device, dpcode, V02_FRAME, raw=raw)
    assert wrapper.read_device_status(mock_device) is not None


def test_find_dpcode_without_dpcodes(mock_device: CustomerDevice) -> None:
    """No wrapper is found without a DP code."""
    assert ElectricityCurrentWrapper.find_dpcode(mock_device, None) is None


def test_find_dpcode_unknown_dpcode(mock_device: CustomerDevice) -> None:
    """No wrapper is found for a DP code the device does not report."""
    assert ElectricityCurrentWrapper.find_dpcode(mock_device, "bad") is None


def test_find_dpcode_unsupported_datapoint_type(
    mock_device: CustomerDevice,
) -> None:
    """No wrapper is found for an unrelated datapoint type."""
    inject_dpcode(mock_device, "phase_1", 100, dptype="Integer")

    assert ElectricityCurrentWrapper.find_dpcode(mock_device, "phase_1") is None


def test_find_dpcode_accepts_dpcode_tuple(mock_device: CustomerDevice) -> None:
    """The DP code order takes precedence over the datapoint type."""
    _inject_frame(mock_device, "phase_1", V02_FRAME, raw=True)
    _inject_frame(mock_device, "phase_s1", V02_FRAME, raw=False)

    string_wrapper = ElectricityCurrentWrapper.find_dpcode(
        mock_device, ("phase_s1", "phase_1")
    )
    assert string_wrapper is not None
    assert string_wrapper.dpcode == "phase_s1"
    assert isinstance(_source(string_wrapper), StringTypeInformation)

    raw_wrapper = ElectricityCurrentWrapper.find_dpcode(
        mock_device, ("phase_1", "phase_s1")
    )
    assert raw_wrapper is not None
    assert raw_wrapper.dpcode == "phase_1"
    assert isinstance(_source(raw_wrapper), RawTypeInformation)


def test_find_dpcode_prefer_function(mock_device: CustomerDevice) -> None:
    """The `prefer_function` lookup path is forwarded to the type lookup."""
    # Both maps declare a Raw datapoint, with different definitions; the
    # reported value is the base64 encoding of the frame.
    state = base64.b64encode(bytes.fromhex(V02_FRAME)).decode()
    inject_dpcode(mock_device, "phase_1", state, dptype="String")
    inject_dpcode_status_range(
        mock_device, "phase_1", "Raw", '{"from": "status_range"}'
    )
    inject_dpcode_function(
        mock_device, "phase_1", "Raw", '{"from": "function"}'
    )

    wrapper = ElectricityCurrentWrapper.find_dpcode(
        mock_device, "phase_1", prefer_function=True
    )
    assert wrapper is not None
    assert isinstance(_source(wrapper), RawTypeInformation)
    assert wrapper.type_information.type_data == '{"from": "function"}'
    assert wrapper.read_device_status(mock_device) == 1.1

    # Without `prefer_function` the status_range definition is used.
    wrapper = ElectricityCurrentWrapper.find_dpcode(mock_device, "phase_1")
    assert wrapper is not None
    assert wrapper.type_information.type_data == '{"from": "status_range"}'
    assert wrapper.read_device_status(mock_device) == 1.1


@pytest.mark.parametrize(
    ("fixture_name", "dpcode", "expected"),
    [
        (
            "zndb_uqzhc4bx5zqwpg2m.json",
            "phase_s1",
            {
                "current": 10.0,
                "power": 3.0,
                "voltage": 230.5,
                "reactive_power": 0.5,
                "apparent_power": 2.35,
                "power_factor": 0.98,
            },
        ),
        (
            "dlq_cnpkf4xdmd9v49iq.json",
            "phase_a",
            {
                "current": 0.072,
                "power": 0.008,
                "voltage": 234.1,
                "reactive_power": 0,
                "apparent_power": 0.008,
                "power_factor": 0.99,
            },
        ),
        (
            "zndb_nazpxescctua1cll.json",
            "phase_1",
            {
                "current": 3.3,
                "power": 0.63,
                "voltage": 230.1,
                "reactive_power": 0.15,
                "apparent_power": 0.66,
                "power_factor": 0.95,
            },
        ),
        (
            "zndb_nazpxescctua1cll.json",
            "phase_2",
            {
                "current": 2.2,
                "power": 0.42,
                "voltage": 230.1,
                "reactive_power": 0.1,
                "apparent_power": 0.44,
                "power_factor": 0.95,
            },
        ),
    ],
    ids=["string", "raw", "indexed_raw_1", "indexed_raw_2"],
)
def test_real_captured_frames(
    fixture_name: str,
    dpcode: str,
    expected: dict[str, float],
) -> None:
    """Real captured frames are decoded through the unified wrapper."""
    device = create_device(fixture_name)

    for wrapper_type, attribute, _ in _WRAPPER_CASES:
        wrapper = _find(device, wrapper_type, dpcode)
        assert wrapper.dpcode == dpcode
        assert wrapper.read_device_status(device) == expected[attribute]


@pytest.mark.parametrize(
    ("wrapper_type", "legacy_wrappers"),
    list(zip(_WRAPPERS, _LEGACY_WRAPPERS, strict=True)),
    ids=_WRAPPER_IDS,
)
@pytest.mark.parametrize("raw", [False, True], ids=["string", "raw"])
@pytest.mark.parametrize(
    "frame",
    [
        LEGACY_FRAME,
        f"{LEGACY_FRAME}0000",
        V01_FRAME,
        V02_FRAME,
        f"{V02_FRAME[:-2]}0F",
    ],
    ids=["legacy", "legacy_extended", "v01", "v02", "v02_negative"],
)
def test_matches_existing_wrappers(
    mock_device: CustomerDevice,
    wrapper_type: type[DPCodeJsonDictAttributeWrapper[Any]],
    legacy_wrappers: tuple[
        type[DPCodeTypeInformationWrapper[Any, Any, Any]],
        type[DPCodeTypeInformationWrapper[Any, Any, Any]],
    ],
    raw: bool,
    frame: str,
) -> None:
    """New and existing entry points expose the same attributes and readings."""
    dpcode = "phase_1" if raw else "phase_s1"
    _inject_frame(mock_device, dpcode, frame, raw=raw)
    wrapper = wrapper_type.find_dpcode(mock_device, dpcode)
    legacy = legacy_wrappers[0 if raw else 1].find_dpcode(mock_device, dpcode)
    assert (wrapper is None) == (legacy is None)
    if wrapper is None:
        return
    assert legacy is not None
    factors = {"mA": 1000, "W": 1000, "var": 1000, "VA": 1000}
    legacy_value = legacy.read_device_status(mock_device)
    assert legacy_value is not None
    assert wrapper.read_device_status(mock_device) == pytest.approx(
        legacy_value / factors.get(legacy.native_unit, 1)
    )


@pytest.mark.parametrize("raw", [False, True], ids=["string", "raw"])
def test_missing_status_then_first_report(
    mock_device: CustomerDevice, raw: bool
) -> None:
    """A missing initial status can later be read using the same wrapper."""
    dpcode = "phase_1" if raw else "phase_s1"
    _inject_frame(mock_device, dpcode, V02_FRAME, raw=raw)
    del mock_device.status[dpcode]
    wrapper = _find(mock_device, ElectricityCurrentWrapper, dpcode)
    assert wrapper.read_device_status(mock_device) is None
    _inject_frame(mock_device, dpcode, V02_FRAME, raw=raw)
    assert wrapper.read_device_status(mock_device) == 1.1


@pytest.mark.parametrize("prefer_function", [False, True])
def test_mixed_definition_types(
    mock_device: CustomerDevice, prefer_function: bool
) -> None:
    """Type matching keeps the prototype's Raw-first order for one DP."""
    _inject_frame(mock_device, "phase_1", V02_FRAME, raw=True)
    inject_dpcode_function(mock_device, "phase_1", "String", "{}")
    wrapper = ElectricityCurrentWrapper.find_dpcode(
        mock_device, "phase_1", prefer_function=prefer_function
    )
    assert wrapper is not None
    assert isinstance(_source(wrapper), RawTypeInformation)
    assert wrapper.read_device_status(mock_device) == 1.1


def test_missing_attribute_does_not_select_another_dp(
    mock_device: CustomerDevice,
) -> None:
    """A matching legacy DP does not borrow an attribute from another DP."""
    _inject_frame(mock_device, "phase_1", LEGACY_FRAME, raw=True)
    _inject_frame(mock_device, "phase_s1", V02_FRAME, raw=False)
    assert (
        ElectricityReactivePowerWrapper.find_dpcode(
            mock_device, ("phase_1", "phase_s1")
        )
        is None
    )


@pytest.mark.parametrize("raw", [False, True], ids=["string", "raw"])
def test_update_isolation(mock_device: CustomerDevice, raw: bool) -> None:
    """Reading an updated channel leaves another channel unchanged."""
    prefix = "phase_" if raw else "phase_s"
    _inject_frame(mock_device, f"{prefix}1", V02_FRAME, raw=raw)
    _inject_frame(mock_device, f"{prefix}2", V02_FRAME, raw=raw)
    first = _find(mock_device, ElectricityCurrentWrapper, f"{prefix}1")
    second = _find(mock_device, ElectricityCurrentWrapper, f"{prefix}2")
    _inject_frame(
        mock_device,
        f"{prefix}2",
        "020F08FD0008980001A40000640001B85F00",
        raw=raw,
    )
    assert first.skip_update(mock_device, [f"{prefix}2"]) is True
    assert second.skip_update(mock_device, [f"{prefix}2"]) is False
    assert first.read_device_status(mock_device) == 1.1
    assert second.read_device_status(mock_device) == 2.2


def test_quirk_type_information_override(mock_device: CustomerDevice) -> None:
    """Unified lookup retains the product's type-information override."""

    class CustomRawTypeInformation(RawTypeInformation):
        """A Raw type returned by the product quirk."""

    _inject_frame(mock_device, "phase_1", V02_FRAME, raw=True)
    quirk = DeviceQuirk().applies_to(product_id=mock_device.product_id)
    quirk.override_dpid_type_information_cls(
        dpid=101,
        dpcode="phase_1",
        type_information_cls=CustomRawTypeInformation,
    )
    TUYA_QUIRKS_REGISTRY.register(mock_device.product_id, quirk)
    wrapper = _find(mock_device, ElectricityCurrentWrapper, "phase_1")
    assert isinstance(_source(wrapper), CustomRawTypeInformation)
    assert wrapper.read_device_status(mock_device) == 1.1


@pytest.mark.parametrize(
    ("wrapper_type", "native_unit", "suggested_unit"),
    [
        (ElectricityCurrentWrapper, "A", None),
        (ElectricityPowerWrapper, "kW", None),
        (ElectricityVoltageWrapper, "V", None),
        (ElectricityReactivePowerWrapper, "kvar", None),
        (ElectricityApparentPowerWrapper, "kVA", None),
        (ElectricityPowerFactorWrapper, None, None),
    ],
    ids=_WRAPPER_IDS,
)
def test_units(
    wrapper_type: type[DPCodeJsonDictAttributeWrapper[Any]],
    native_unit: str | None,
    suggested_unit: str | None,
) -> None:
    """The normalized wrappers expose the existing JSON native units."""
    assert wrapper_type.native_unit == native_unit
    assert wrapper_type.suggested_unit == suggested_unit


def test_wrapper_is_type_information_wrapper() -> None:
    """The unified wrapper is usable where HA expects a type wrapper."""
    assert issubclass(ElectricityCurrentWrapper, DPCodeTypeInformationWrapper)


@pytest.mark.parametrize("raw", [False, True], ids=["string", "raw"])
@pytest.mark.parametrize(
    ("frame", "expected"),
    [
        pytest.param(
            V02_FRAME,
            {
                "electricCurrent": 1.1,
                "power": 0.21,
                "voltage": 230.1,
                "reactivePower": 0.05,
                "apparentPower": 0.22,
                "powerFactor": 0.95,
            },
            id="v02",
        ),
        pytest.param(
            LEGACY_FRAME,
            {"electricCurrent": 1.1, "power": 0.21, "voltage": 230.1},
            id="legacy",
        ),
        pytest.param(
            "020F00000000000000000000000000000000",
            {
                "electricCurrent": 0,
                "power": 0,
                "voltage": 0,
                "reactivePower": 0,
                "apparentPower": 0,
                "powerFactor": 0,
            },
            id="zero",
        ),
    ],
)
def test_normalized_fields_preserve_device_payload(
    mock_device: CustomerDevice,
    raw: bool,
    frame: str,
    expected: dict[str, float],
) -> None:
    """Normalize names and units without mutating status or DP definitions."""
    _inject_frame(mock_device, "phase_1", frame, raw=raw)
    status = deepcopy(mock_device.status)
    status_range = {
        code: vars(definition).copy()
        for code, definition in mock_device.status_range.items()
    }
    functions = {
        code: vars(definition).copy()
        for code, definition in mock_device.function.items()
    }
    wrapper = _find(mock_device, ElectricityCurrentWrapper, "phase_1")
    assert wrapper.type_information.read_device_value(mock_device) == expected
    assert mock_device.status == status
    assert {
        code: vars(definition)
        for code, definition in mock_device.status_range.items()
    } == status_range
    assert {
        code: vars(definition)
        for code, definition in mock_device.function.items()
    } == functions


@pytest.mark.parametrize(
    ("wrapper_type", "expected"), _VALUE_CASES, ids=_WRAPPER_IDS
)
def test_existing_json_value_is_not_scaled_again(
    mock_device: CustomerDevice,
    wrapper_type: type[DPCodeJsonDictAttributeWrapper[Any]],
    expected: float,
) -> None:
    """An already normalized JSON DP retains its native units."""
    status = json.dumps(
        {
            "electricCurrent": 1.1,
            "power": 0.21,
            "voltage": 230.1,
            "reactivePower": 0.05,
            "apparentPower": 0.22,
            "powerFactor": 0.95,
        }
    )
    inject_dpcode(mock_device, "phase_1", status, dptype="Json")
    wrapper = _find(mock_device, wrapper_type, "phase_1")
    assert isinstance(_source(wrapper), JsonTypeInformation)
    assert wrapper.read_device_status(mock_device) == expected
    assert mock_device.status["phase_1"] == status


def test_missing_json_attribute_does_not_fall_back_to_frame(
    mock_device: CustomerDevice,
) -> None:
    """A JSON DP missing a metric is never parsed as a Hex or Raw frame."""
    inject_dpcode(
        mock_device,
        "phase_1",
        '{"voltage":230.1,"electricCurrent":1.1,"power":0.21}',
        dptype="Json",
    )
    assert (
        ElectricityReactivePowerWrapper.find_dpcode(mock_device, "phase_1")
        is None
    )
    assert (
        ElectricityApparentPowerWrapper.find_dpcode(mock_device, "phase_1")
        is None
    )
    assert (
        ElectricityPowerFactorWrapper.find_dpcode(mock_device, "phase_1")
        is None
    )


def test_unrelated_quirk_override_is_not_parsed_as_a_frame(
    mock_device: CustomerDevice,
) -> None:
    """A non-metering quirk type cannot enter the frame adapter."""
    inject_dpcode(
        mock_device,
        "phase_1",
        100,
        dptype="Integer",
        values='{"min":0,"max":1000,"scale":0,"step":1}',
    )
    quirk = DeviceQuirk().applies_to(product_id=mock_device.product_id)
    quirk.override_dpid_type_information_cls(
        dpid=101,
        dpcode="phase_1",
        type_information_cls=IntegerTypeInformation,
    )
    TUYA_QUIRKS_REGISTRY.register(mock_device.product_id, quirk)
    assert ElectricityCurrentWrapper.find_dpcode(mock_device, "phase_1") is None
