"""Test the Pro Breeze 30L dehumidifier quirk."""

import json

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry


def test_pro_breeze_30l_quirk(filled_quirks_registry: QuirksRegistry) -> None:
    """The quirk removes the phantom anion and adds the real datapoints."""
    device = create_device("cs_ipmyy4nigpqcnd8q.json")

    # BEFORE: the cloud only knows anion / fault / countdown_left.
    assert "anion" in device.status_range
    assert "switch" not in device.function

    filled_quirks_registry.initialise_device_quirk(device)

    # AFTER: anion removed, writable datapoints in function and status_range.
    assert "anion" not in device.function
    assert "anion" not in device.status_range
    for code in (
        "switch",
        "mode",
        "dehumidify_set_value",
        "fan_speed_enum",
        "child_lock",
        "countdown_set",
    ):
        assert code in device.function
        assert code in device.status_range
    assert "humidity_indoor" in device.status_range

    target = json.loads(device.status_range["dehumidify_set_value"].values)
    assert (target["min"], target["max"], target["step"]) == (30, 80, 5)

    fault = json.loads(device.status_range["fault"].values)
    assert fault["label"][3] == "tankfull"
