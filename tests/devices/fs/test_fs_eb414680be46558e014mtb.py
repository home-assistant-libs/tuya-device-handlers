from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
# Force python to load and execute the registration file
import tuya_device_handlers.devices.fs.fs_eb414680be46558e014mtb  # noqa: F401

def test_quirk_registers_successfully():
    """Verify our unique product ID is successfully found in the global registry."""
    # Look directly inside the internal _quirks dictionary using our product ID
    quirk = TUYA_QUIRKS_REGISTRY._quirks.get("eb414680be46558e014mtb")
    
    assert quirk is not None
    assert quirk._applies_to == "eb414680be46558e014mtb"
