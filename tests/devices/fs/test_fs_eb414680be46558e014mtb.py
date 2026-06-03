from tuya_device_handlers import TUYA_QUIRKS_REGISTRY

def test_quirk_registers_successfully():
    """Verify our unique product ID is successfully found in the global registry."""
    quirk = TUYA_QUIRKS_REGISTRY.get("eb414680be46558e014mtb")
    assert quirk is not None
    assert quirk.name == "TOWER FAN (CZTF423S)"
