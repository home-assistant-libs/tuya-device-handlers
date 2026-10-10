"""Quirk for Fairland Comfortline Inverter pool heat pump (BPNCR07).

``temp_set`` (dpid 106) declares an empty unit and a Fahrenheit-looking
range, while the confirmed unit reports Celsius values (the app's target
range is 18-40 °C). With an empty unit, the climate definition falls back
to ``temp_unit_convert``, which reports ``"f"`` on that unit, so Celsius
values are misread as Fahrenheit. The quirk declares ``"c"`` and the real
range.

Only the Celsius variant is confirmed. A Fahrenheit variant (eg. US
units) would report a setpoint of at least 50 (Celsius maximum is 40), so
that is used to detect it. Such units are left with the empty unit, so the
default ``temp_unit_convert`` fallback applies.

``temp_current`` (dpid 124) never updates. The real inlet water
temperature is the manufacturer-specific ``WInTemp`` datapoint (dpid 102),
which the quirk exposes as ``temp_current`` instead. This remap relies on
``local_strategy``, which is only patched when ``support_local`` is true.
"""

from tuya_sharing import CustomerDevice

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode


def _is_fahrenheit_variant(device: CustomerDevice) -> bool:
    """Check if the device reports temp_set in Fahrenheit."""
    raw_value = device.status.get("temp_set")
    return isinstance(raw_value, int) and raw_value >= 50


def _is_celsius_variant(device: CustomerDevice) -> bool:
    """Check if the device reports temp_set in Celsius (the default)."""
    return not _is_fahrenheit_variant(device)


(
    DeviceQuirk()
    .applies_to(product_id="CGJ08iaKlWqKmVuX")
    .add_dpid_integer(
        dpid=106,
        dpcode="temp_set",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="c",
        min=18,
        max=40,
        scale=0,
        step=1,
        apply_when=_is_celsius_variant,
    )
    .remove_dpid(dpid=124, dpcode="temp_current")
    .add_dpid_integer(
        dpid=102,
        dpcode="temp_current",
        dpmode=DPMode.READ,
        unit="c",
        min=-22,
        max=250,
        scale=0,
        step=1,
        apply_when=_is_celsius_variant,
    )
    .add_dpid_integer(
        dpid=102,
        dpcode="temp_current",
        dpmode=DPMode.READ,
        unit="",
        min=-22,
        max=250,
        scale=0,
        step=1,
        apply_when=_is_fahrenheit_variant,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
