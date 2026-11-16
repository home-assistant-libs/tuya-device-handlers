"""Test that climate switch_wrapper finds power_switch dpcode.

Some Tuya devices (e.g. Vital+ Ice Bath Pro, category ktkzq) use
``power_switch`` as the on/off datapoint name instead of the standard
``switch``. The climate ``get_default_definition`` lookup should accept
both names so these devices get a working on/off control on their
climate entity.
"""

from tests import create_device
from tuya_device_handlers.definition.climate import get_default_definition
from tuya_device_handlers.helpers.homeassistant import TuyaUnitOfTemperature


def test_power_switch_climate_definition() -> None:
    """Test a device with only power_switch (no switch) gets a switch_wrapper.

    This device (Vital+ Ice Bath Pro, ktkzq category) has power_switch
    as its on/off DP but does NOT have a DP named "switch". Before the
    fix, the climate switch_wrapper would be None, meaning no on/off
    control. After the fix, it should find power_switch.
    """
    device = create_device("ktkzq_urzivdhumrwfakie.json")

    # Device should have power_switch but NOT switch
    assert "power_switch" in device.function
    assert "switch" not in device.function

    # Get the climate definition
    definition = get_default_definition(device, TuyaUnitOfTemperature.CELSIUS)

    # The definition should exist
    assert definition is not None

    # The switch_wrapper should find power_switch and be non-None
    assert definition.switch_wrapper is not None

    # Also verify temperature wrappers work
    assert definition.current_temperature_wrapper is not None
    assert definition.set_temperature_wrapper is not None
