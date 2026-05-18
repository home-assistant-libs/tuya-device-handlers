"""Test diagnostics helpers."""

from syrupy.assertion import SnapshotAssertion

from tests import create_device
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder.device_quirk import DeviceQuirk
from tuya_device_handlers.helpers.diagnostics import customer_device_as_dict
from tuya_device_handlers.registry import QuirksRegistry


def test_customer_device_as_dict(snapshot: SnapshotAssertion) -> None:
    """Test customer_device_as_dict."""
    device = create_device("sfkzq_ed7frwissyqrejic.json")
    data = customer_device_as_dict(device)
    assert data == snapshot
    assert "original_category" not in data
    assert "original_function" not in data
    assert "original_local_strategy" not in data
    assert "original_status_range" not in data


def test_customer_device_with_quirk_as_dict(
    filled_quirks_registry: QuirksRegistry, snapshot: SnapshotAssertion
) -> None:
    """Test customer_device_as_dict."""
    device = create_device("tdq_x3o8epevyeo3z3oa.json")

    filled_quirks_registry.initialise_device_quirk(device)

    data = customer_device_as_dict(device)
    # The start of the path is not important for the test.
    data["quirk"] = data["quirk"][-60:]
    assert data == snapshot
    assert "original_category" in data
    assert "original_function" in data
    assert "original_local_strategy" in data
    assert "original_status_range" in data


def test_customer_device_with_uninitialised_quirk_as_dict(
    snapshot: SnapshotAssertion,
) -> None:
    """Test customer_device_as_dict when the quirk was not initialised.

    A quirk is registered for the device, but initialise_device was
    never called, so the original_* attributes are absent.
    """
    device = create_device("tdq_x3o8epevyeo3z3oa.json")

    # auto_reset_quirks reverts this registration after the test.
    (
        DeviceQuirk()
        .applies_to(product_id=device.product_id)
        .register(TUYA_QUIRKS_REGISTRY)
    )

    data = customer_device_as_dict(device)
    # The start of the path is not important for the test.
    data["quirk"] = data["quirk"][-37:]
    assert data == snapshot
    assert data["quirk"] is not None
    assert "original_category" not in data
    assert "original_function" not in data
    assert "original_local_strategy" not in data
    assert "original_status_range" not in data
