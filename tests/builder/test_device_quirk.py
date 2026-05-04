"""Tests for DeviceQuirk."""

import pytest

from tuya_device_handlers.builder.device_quirk import DeviceQuirk
from tuya_device_handlers.registry import QuirksRegistry


def test_applies_to_records_manufacturer_and_model() -> None:
    """applies_to stores manufacturer and model as readable attributes."""
    quirk = DeviceQuirk().applies_to(
        product_id="abc",
        manufacturer="Acme",
        model="Widget-1",
    )
    assert quirk.manufacturer == "Acme"
    assert quirk.model == "Widget-1"


def test_applies_to_called_twice_raises() -> None:
    """Calling applies_to a second time raises ValueError."""
    quirk = DeviceQuirk().applies_to(product_id="abc")
    with pytest.raises(ValueError, match="already has an applies_to condition"):
        quirk.applies_to(product_id="def")


def test_register_without_applies_to_raises() -> None:
    """register raises ValueError when applies_to was never called."""
    quirk = DeviceQuirk()
    with pytest.raises(
        ValueError, match="does not have an applies_to condition"
    ):
        quirk.register(QuirksRegistry())
