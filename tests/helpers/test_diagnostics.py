"""Test diagnostics helpers."""

from syrupy.assertion import SnapshotAssertion

from tests import create_device
from tuya_device_handlers.helpers.diagnostics import customer_device_as_dict


def test_customer_device_as_dict(snapshot: SnapshotAssertion) -> None:
    """Test customer_device_as_dict."""
    device = create_device("sfkzq_ed7frwissyqrejic.json")
    assert customer_device_as_dict(device) == snapshot
