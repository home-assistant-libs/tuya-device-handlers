"""Tests for DeviceQuirk."""

from tuya_device_handlers.builder.device_quirk import DeviceQuirk


def test_applies_to_records_manufacturer_and_model() -> None:
    """applies_to stores manufacturer and model as readable attributes."""
    quirk = DeviceQuirk().applies_to(
        product_id="abc",
        manufacturer="Acme",
        model="Widget-1",
    )
    assert quirk.manufacturer == "Acme"
    assert quirk.model == "Widget-1"
