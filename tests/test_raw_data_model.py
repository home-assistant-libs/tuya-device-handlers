"""Test utils."""

import base64
import dataclasses

import pytest
from syrupy.assertion import SnapshotAssertion

from tuya_device_handlers.raw_data_model import ElectricityData


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
