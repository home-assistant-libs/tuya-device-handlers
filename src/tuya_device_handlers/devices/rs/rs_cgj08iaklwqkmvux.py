"""Quirk for Fairland Comfortline Inverter pool heat pump (BPNCR07).

product_id CGJ08iaKlWqKmVuX, sold under Fairland's own "Smarter Pool" app and
also paired through Tuya Smart Life.

``temp_set`` (dpid 106) and ``temp_current`` (dpid 124) are both declared
with an empty ``unit`` string. ``definition/climate.py`` treats an empty
unit as "unit unknown" and falls back to reading the live value of the
``temp_unit_convert`` status datapoint to guess it. This device's
``temp_unit_convert`` reports ``"f"``, even though its own numeric values
are genuinely Celsius (confirmed against the Tuya Smart Life app, which
shows the same raw values as 20 degrees C current / 31 degrees C target,
and against the Tuya Cloud Development Platform's own "Device Debugging"
status dump, which reports ``temp_set: 31`` with no scaling applied
(``"scale": 0``) at the same moment Smart Life shows 31 degrees C).

With the empty unit left as-is, climate.py's fallback misreads the
already-correct Celsius values as Fahrenheit and converts them again,
producing nonsensical readings (31 "misread as Fahrenheit" converts to
about -0.6 degrees C). Declaring the real unit here means that fallback
is never reached for this device.

Local override only (this household's own <HA config>/tuya_quirks/), not
submitted upstream as a blanket fix -- confirmed Celsius for this one
physical unit (via the Tuya Smart Life app and the Tuya Cloud
Development Platform's Device Debugging status dump), but there's no
evidence every unit sold under this product_id is Celsius-only. A
PR to home-assistant-libs/tuya-device-handlers is being prepared
separately, scoped honestly to that single-unit confirmation, for the
maintainers to judge. See docs/fairland-heat-pump-tuya.md.

``temp_current`` (dpid 124) was NOT the device's real water-temperature
reading -- it stays fixed at its schema minimum forever. The real reading
lives under a separate raw datapoint named ``WInTemp`` ("Water In Temp" --
seen reporting live, changing values of 20-21 degrees C every few seconds
in the Tuya Cloud Device Logs, under the human-readable label "Inlet Water
Temperature"), whose own declared unit is the literal string
"摄氏度或华氏度" (Chinese for "Celsius or
Fahrenheit" -- an unfilled template placeholder in Tuya's own product spec,
not a real unit either HA's unit-alias matching or the temp_unit_convert
fallback can use).

``WInTemp`` was not visible anywhere in this device's advertised
function/status_range (only switch/temp_unit_convert/temp_set/temp_current
are) -- it only appeared after switching the Tuya Cloud Development
Platform's device view to raw "DP mode", and its Chinese name there,
"jinshui wendu (AIN1)" ("Inlet Water Temperature (AIN1)"), is an exact
match for the human-readable label Tuya's own Device Logs show for the
live, changing 20-21 degree C readings this device reports every few
seconds.

dpid 102 is CONFIRMED for this exact product_id, two ways: it matches the
dpid assignment of other Tuya-based pool heat pumps built on what looks
like the same OEM controller/firmware (e.g. the Raypak Crosswind, where
WInTemp is also dpid 102), and it was verified live here -- after
retiring the dead dpid 124 and redeclaring dpid 102 under the dpcode
"temp_current" (the name HA's generic climate logic actually searches
for), current_temperature read null for the first few seconds (no cached
status yet for a dpid HA had never seen before), then settled to a real,
plausible, changing pool-water temperature once the next status push
arrived.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="CGJ08iaKlWqKmVuX")
    .add_dpid_integer(
        dpid=106,
        dpcode="temp_set",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="c",
        min=-22,
        max=104,
        scale=0,
        step=1,
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
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
