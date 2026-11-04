# Recipe: inverted covers (curtains, blinds, shutters)

This walkthrough fixes a cover whose position is backwards in Home Assistant.
You can follow it **even if you don't write Python**: you will find out how
your device behaves, then copy a short quirk.

> The classes used below for devices that follow `control_back_mode` need
> `tuya-device-handlers` 0.0.34 or later, included in Home Assistant 2026.11.
> Your version is listed in the diagnostics, under `requirements`.

## When to use this

Home Assistant and the Tuya app disagree about your cover, for example:

- a closed blind shows as open at 100%;
- the position slider moves the cover the opposite way;
- the open button closes the cover.

This happens because most Tuya motors use 0 = open and 100 = closed, while
Home Assistant uses 0 = closed and 100 = open, so Home Assistant inverts the
position by default. Some motors already use Home Assistant's convention, and
for those the default is wrong.

The fix depends on the product, so it needs a quirk: there is no general
setting in Home Assistant for it.

---

## Step 1 — Find out how your device reports its position

Download the diagnostics: **Settings → Devices & services → Tuya → your device
→ the ⋮ menu → Download diagnostics**. **Keep this file**: a pull request needs
it for the test fixture.

Then find out what the device reports when the cover is closed:

1. Close the cover **fully** from the Tuya app.
2. Download the diagnostics again, and look at `percent_state` under `status`.
   If there is no `percent_state`, use `percent_control`.
3. Write down the value, and `control_back_mode` from the same place.

| Value when fully closed | The device in this mode is |
| ----------------------- | -------------------------- |
| `0`                     | **standard**               |
| `100`                   | **reversed**               |

If your device has `control_back_mode`, repeat this in the other mode. You can
change it in the Tuya app, or with the **Motor mode** entity in Home Assistant
if your device has one.
Changing the mode can swap the motor's direction, so check that the cover still
moves safely, and **set it back afterwards**.

> Can't test the other mode, or the device has no `control_back_mode`? Use the
> first row of the next table if the device is standard. Mention in your quirk
> which mode you tested.

## Step 2 — Pick the class

| `back` mode | `forward` mode | Use                                           |
| ----------- | -------------- | --------------------------------------------- |
| standard    | standard       | `InvertedIntegerTypeInformationEx`            |
| standard    | reversed       | `BackModeInvertedIntegerTypeInformationEx`    |
| reversed    | standard       | `ForwardModeInvertedIntegerTypeInformationEx` |
| reversed    | reversed       | `IntegerTypeInformation`                      |

The last row is already the default in most categories, so you usually won't
need a quirk for it. It is only needed for `clkg` devices, which follow
`control_back_mode` by default.

A missing `control_back_mode` counts as `forward`.

## Step 3 — Write the quirk file

Create a file named `<category>_<product_id>.py`, all lowercase, for example
`cl_68nvbio9.py`. The category and the product id are in your diagnostics.

Use the class from Step 2, in the import and in each override:

```python
"""Quirk for <device> (product_id <product_id>).

This device reports its position in the standard HA convention (0 = closed,
100 = open), but the default mapping inverts it, so the position is displayed
and set backwards.

Tested in `back` and `forward` mode: the position is standard in both.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.type_information_ex import (
    InvertedIntegerTypeInformationEx,
)

(
    DeviceQuirk()
    .applies_to(product_id="<product_id>")
    .override_dpid_type_information_cls(
        dpid=2,
        dpcode="percent_control",
        type_information_cls=InvertedIntegerTypeInformationEx,
    )
    .override_dpid_type_information_cls(
        dpid=3,
        dpcode="percent_state",
        type_information_cls=InvertedIntegerTypeInformationEx,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
```

What to change:

- **`product_id="..."`**: your device's product id, exactly as in the
  diagnostics, including its case.
- **`dpid` and `dpcode`**: add one override for each position datapoint your
  device has. Under `local_strategy` in the diagnostics, the number that keys
  the block whose `status_code` is `percent_control` is its `dpid`. They are
  usually 2 and 3, but check. A device without `percent_state` needs only the
  `percent_control` override.
- **Docstring**: say what you found in Step 1, including which modes you
  tested.

For `IntegerTypeInformation`, the import is
`from tuya_device_handlers.type_information import IntegerTypeInformation`.

Keep the file to a **single** `DeviceQuirk()...register(...)` block.

Tilt is separate: `angle_horizontal` and `angle_vertical` are only changed if
you add overrides for them too.

## Step 4 — Test it live in Home Assistant

1. Copy your file into `<config>/tuya_quirks/` (create that folder if needed).
2. Reload the integration: **Settings → Devices & services → Tuya → ⋮ →
   Reload**.
3. In the logs you should see `Loading custom quirk module …`. If the file has
   a typo, the error and line number are logged here.
4. Check that the position matches the Tuya app, and that open, close and the
   position slider all move the cover the right way, in each mode you tested.

## Step 5 — Turn it into a pull request

If it works, please contribute it so everyone with this device benefits. Follow
[Step 4 of the ENUM recipe](adding-missing-enum-values.md#step-4--turn-it-into-a-pull-request)
for the fork, the fixture and the commit, with the file in
`src/tuya_device_handlers/devices/<category>/`.

For the test, create `tests/devices/<category>/test_<product_id>.py`, and adapt
the expected values to your device:

```python
"""Test the <device> cover position quirk."""

from unittest.mock import patch

from tests import create_device
from tests.integration_helpers.cover import get_cover_default_definitions
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_corrects_position(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """With the quirk, a position of 25 reads as 25 and is written as is."""
    device = create_device("<category>_<product_id>.json")
    device.status["percent_state"] = 25

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definitions = get_cover_default_definitions(device)
    read_wrapper = definitions["control"].current_position_wrapper
    assert read_wrapper is not None
    assert read_wrapper.read_device_status(device) == 75

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_cover_default_definitions(device)
    read_wrapper = definitions["control"].current_position_wrapper
    write_wrapper = definitions["control"].set_position_wrapper
    assert read_wrapper is not None
    assert write_wrapper is not None
    assert read_wrapper.read_device_status(device) == 25
    assert write_wrapper.get_update_commands(device, 70) == [
        {"code": "percent_control", "value": 70}
    ]
```

If your cover reads `percent_control` (`clkg` covers, and covers without
`percent_state`), set `device.status["percent_control"] = 25` instead.

If your device follows `control_back_mode`, test both modes by setting
`device.status["control_back_mode"]` before reading.

## Related

- [Recipe: add missing ENUM values](adding-missing-enum-values.md)
- [Recipe: missing entities](unsupported-category-or-dpcode.md), which also
  covers commands rejected by the cloud.
