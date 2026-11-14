"""Quirk for a Tuya ceiling fan controller (product_id g0ewlb1vmwqljzji).

The cloud declares datapoint 3 (`fan_speed`) as an Enum with the string range
["1".."6"], but the device reports the speed as an integer. The cached cloud
status therefore holds `2` instead of `"2"`, and every MQTT report is dropped
by the `default` convert strategy ("value not in range value=4"), so Home
Assistant shows no speed at all and the fan card's speed slider stays blank.

Writes are unaffected: Home Assistant sends `{"code": "fan_speed", "value":
"4"}`, the cloud accepts it and the fan does change speed - only the value
coming back is lost, which makes the speed look like it never changes.

Mapping the raw integers onto the declared string range fixes both the initial
cloud status and the later MQTT reports.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk

_FAN_SPEED = {1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6"}

(
    DeviceQuirk()
    .applies_to(product_id="g0ewlb1vmwqljzji")
    .map_dpid_initial_status_values(
        dpid=3,
        dpcode="fan_speed",
        status_mapping=_FAN_SPEED,
    )
    .set_dpid_strategy_to_enum(
        dpid=3,
        dpcode="fan_speed",
        enum_mapping_map=_FAN_SPEED,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
