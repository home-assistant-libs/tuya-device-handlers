"""Test utils."""

import base64
import dataclasses

import pytest
from syrupy.assertion import SnapshotAssertion

from tuya_device_handlers.raw_data_model import (
    CatLitterBoxData,
    ElectricityData,
    FeederScheduleData,
)


@pytest.mark.parametrize(
    ("base64_string", "expected"),
    [
        ("AAAFbAAA", CatLitterBoxData(weight=1388, duration=0)),
        ("AAAF2ABW", CatLitterBoxData(weight=1496, duration=86)),
        ("", None),
        ("AAAF2A==", None),
    ],
)
def test_cat_litter_box_data(
    base64_string: str, expected: CatLitterBoxData | None
) -> None:
    """Test CatLitterBoxData."""
    assert (
        CatLitterBoxData.from_bytes(base64.b64decode(base64_string)) == expected
    )


@pytest.mark.parametrize(
    "base64_string",
    [
        "Ag8JJQAASAAACAAAAAAACGME",
        "AAAAAAAAAAAAAA==",
        "CGYAPCgADPIACw==",
        "CIsAK8MACWo=",
        "CJwAA5EAAFw=",
        "CKMAAn0AAGw=",
        "CPQAI58ACBA=",
        "CREANUkADG8=",
        "CSIAFfQABKE=",
        "CT0AAmAAAIU=",
        "CTIAVfcAFGw=",
        # Mock
        base64.b64encode(bytes.fromhex("08800003E8002710")),
        base64.b64encode(bytes.fromhex("010F08800003E8002710000DAC0030D450")),
        base64.b64encode(bytes.fromhex("020F08800003E8002710000DAC0030D4500F")),
        # Invalid
        "",
    ],
)
def test_electricity_data(
    base64_string: str,
    snapshot: SnapshotAssertion,
) -> None:
    """Test ElectricityData."""
    raw_bytes = base64.b64decode(base64_string)
    raw_data = ElectricityData.from_bytes(raw_bytes)

    asdict = None if raw_data is None else dataclasses.asdict(raw_data)
    assert asdict == snapshot


def test_from_hex_matches_from_bytes() -> None:
    """from_hex decodes the hex string then delegates to from_bytes."""
    hex_string = "020F08800003E8002710000DAC0030D4500F"
    assert ElectricityData.from_hex(hex_string) == ElectricityData.from_bytes(
        bytes.fromhex(hex_string)
    )


@pytest.mark.parametrize("invalid", ["not-hex", "0F0", "ZZ"])
def test_from_hex_invalid_returns_none(invalid: str) -> None:
    """Invalid hex strings return None instead of raising."""
    assert ElectricityData.from_hex(invalid) is None


@pytest.mark.parametrize(
    "base64_string",
    [
        # Empty
        "",
        # Single entry: Mon, 07:30, portion=2, enabled=1
        base64.b64encode(bytes.fromhex("01071E0201")),
        # Two entries: Mon+Wed 08:00 p=1 on, Sat+Sun 18:15 p=3 off
        base64.b64encode(bytes.fromhex("050800010160120F0300")),
        # Invalid (length not a multiple of 5)
        base64.b64encode(bytes.fromhex("01071E02")),
    ],
)
def test_feeder_schedule_data(
    base64_string: str,
    snapshot: SnapshotAssertion,
) -> None:
    """Test FeederScheduleData round-trip."""
    raw_bytes = base64.b64decode(base64_string)
    entries = FeederScheduleData.from_bytes(raw_bytes)

    assert entries == snapshot
    if entries is not None:
        assert FeederScheduleData.to_bytes(entries) == raw_bytes
