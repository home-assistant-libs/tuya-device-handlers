"""Test diagnostics helpers"""

from syrupy.assertion import SnapshotAssertion

from tuya_device_handlers.helpers.diagnostics import customer_device_as_dict

from .. import create_device


def test_customer_device_as_dict(snapshot: SnapshotAssertion) -> None:
    """Test customer_device_as_dict"""
    device = create_device("sfkzq_ed7frwissyqrejic.json")
    assert customer_device_as_dict(device) == snapshot
