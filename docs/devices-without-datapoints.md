# Recipe: a device that reports no datapoints

Some devices show up in Home Assistant with **no entities at all**, and their
diagnostics show that Tuya's cloud told Home Assistant nothing about them. This
page shows how to find the device's real datapoints, write a quirk that adds
them, and check that it works.

## When to use this

Download the device's diagnostics (**Settings → Devices & services → Tuya →
your device → Download diagnostics**) and look at the `data` object. This
recipe applies when:

- `function`, `status_range`, `local_strategy` and `status` are all empty
  (`{}`), and
- `home_assistant.entities` is empty (`[]`), and
- the `category` is one Home Assistant core knows (see Step 2 of
  [Recipe: missing entities](unsupported-category-or-dpcode.md)).

```json
{
  "data": {
    "category": "mcs",
    "product_id": "KajlwMlIaQUARNpb",
    "online": true,
    "function": {},
    "local_strategy": {},
    "status_range": {},
    "status": {},
    "set_up": false,
    "quirk": null
  }
}
```

The device usually still works in the Tuya Smart or Smart Life app, and it
still sends its reports to Home Assistant. Home Assistant just has no map from
datapoint IDs to codes, so it ignores them. A quirk supplies that map.

If the datapoints _are_ in the diagnostics but no entity appears, this recipe
does not apply: see [Recipe: missing entities](unsupported-category-or-dpcode.md).

---

## Step 1 — Get the device's thing model

The thing model lists every datapoint the device declares: its ID, code, type,
range and whether it can be written. The easiest way to read it is Tuya's
[tuya-smart-control-cli](https://github.com/tuya/tuya-smart-control-cli):

```console
tuya device model <device_id> --json
```

`<device_id>` is the `id` field in your diagnostics. Follow the CLI's README
to install it and create an API key.

> **The API key must belong to the app account that owns the device.** Tuya
> Smart and Smart Life are separate apps with separate accounts, and a key only
> sees devices in its own account's homes. If the command fails with
> `40000905` ("The user does not have device permissions"), check which app the
> device was added with, then use a key for that account.

Each entry in `properties` is one datapoint:

```json
{
  "abilityId": 13,
  "accessMode": "rw",
  "code": "humidity_set",
  "typeSpec": {
    "type": "value",
    "min": 40,
    "max": 90,
    "scale": 0,
    "step": 5,
    "unit": "%"
  }
}
```

| Thing model field | Quirk argument                                                       |
| ----------------- | -------------------------------------------------------------------- |
| `abilityId`       | `dpid`                                                               |
| `code`            | `dpcode` (see Step 2)                                                |
| `accessMode`      | `dpmode`: `rw` → `DPMode.READ \| DPMode.WRITE`, `ro` → `DPMode.READ` |
| `typeSpec`        | the builder method and its arguments, from the table below           |

| `typeSpec.type` | Builder method     | Arguments from `typeSpec`             |
| --------------- | ------------------ | ------------------------------------- |
| `bool`          | `add_dpid_boolean` | none                                  |
| `value`         | `add_dpid_integer` | `min`, `max`, `scale`, `step`, `unit` |
| `enum`          | `add_dpid_enum`    | `range` → `enum_range`                |
| `bitmap`        | `add_dpid_bitmap`  | `label` → `label_range`               |

Save the full output: it is the evidence for your issue or pull request.

## Step 2 — Decide which datapoints to add, and under which code

- **Add the datapoints Home Assistant core maps for the device's category.**
  Look up the category in core's Tuya platform files (`humidifier.py`,
  `sensor.py`, `switch.py`, `select.py`, … under
  [`homeassistant/components/tuya`](https://github.com/home-assistant/core/tree/dev/homeassistant/components/tuya))
  to see which codes become entities. A datapoint core doesn't map produces no
  entity; leave it out of the quirk and mention it in the docstring, so a core
  change can pick it up later.
- **Keep the cloud code for writable datapoints.** Home Assistant sends
  commands through the cloud by code, so a renamed writable datapoint sends a
  code the device's thing model doesn't know.
- **A read-only datapoint may be renamed** to the code core expects, when the
  device uses a non-standard one. For example, the door sensor quirk in
  [#741](https://github.com/home-assistant-libs/tuya-device-handlers/pull/741)
  maps `Battery` to `battery_percentage`.

Then write the quirk as described in the [README](../README.md#writing-a-quirk),
and explain in its docstring that the cloud advertises no datapoints and where
the thing model came from.

## Step 3 — Install it and check it applied

1. Copy the file to `<config>/tuya_quirks/<category>_<product_id_lowercased>.py`.
2. Reload the Tuya integration (**Settings → Devices & services → Tuya → ⋮ →
   Reload**).
3. Download the diagnostics again. `quirk` now shows your file and the line
   of its `DeviceQuirk()` chain, `function` and `status_range` list your
   datapoints, and `home_assistant.entities` lists the new entities.

Entity states start as `unknown` and fill in as the device sends reports.

## Step 4 — Watch reports and commands in the debug log

Turn on debug logging by calling the `logger.set_level` action from
**Developer tools → Actions**. (**Enable debug logging** on the Tuya
integration page covers the integration and `tuya_sharing`, but not this
library, so it won't show quirk loading.)

```yaml
action: logger.set_level
data:
  tuya_device_handlers: debug
  tuya_sharing: debug
  homeassistant.components.tuya: debug
```

Then use the device from its app or its buttons, and try each entity from Home
Assistant. Useful lines to look for (the device ID is the `id` field in your
diagnostics):

| Log line                                                             | Meaning                                                        |
| -------------------------------------------------------------------- | -------------------------------------------------------------- |
| `Loading custom quirk module …`                                      | Your quirk file was imported (an import error is logged here). |
| `mq _on_device_report after strategy convert code=…,value=…`         | A report arrived and your quirk mapped its DP ID to a code.    |
| `Received update for device <id> … {'<code>': <value>}`              | Home Assistant applied the report to the device.               |
| `Sending commands for device <id>: [{'code': …, 'value': …}]`        | Home Assistant sent a command.                                 |
| `response before decrypt ret = {'code': '2008', … 'success': False}` | The Tuya cloud rejected that command (see below).              |

If no report ever arrives for a DP ID, check the ID against the thing model. If
the cloud rejects commands with `2008`, the quirk can't fix that: see
[Commands rejected by the cloud](unsupported-category-or-dpcode.md#commands-rejected-by-the-cloud-error-2008).
Keep the writable datapoints declared `DPMode.READ | DPMode.WRITE` anyway and
note the limitation in the docstring, as in
[`devices/cs/cs_ipmyy4nigpqcnd8q.py`](../src/tuya_device_handlers/devices/cs/cs_ipmyy4nigpqcnd8q.py).

Set the log levels back afterwards (`warning`, or whatever your
`configuration.yaml` sets), or restart Home Assistant.

## Step 5 — Contribute it

Follow [Contributing your quirk](../README.md#contributing-your-quirk). Your
diagnostics file becomes the fixture as-is: empty maps are exactly what the
tests should start from. Good tests for this kind of quirk check that:

- without the quirk, the device has no datapoints and Home Assistant would
  build no entities;
- with it, the expected entities' definitions exist;
- commands use the cloud codes;
- an MQTT report keyed by DP ID updates the right code (see the `test_mqtt`
  tests under `tests/devices/`).

In the issue or pull request, include the thing model output (or the relevant
part of it), say which datapoints you left out and why, and say whether
commands worked.

## Related

- [Recipe: missing entities](unsupported-category-or-dpcode.md) — when the
  datapoints are in the diagnostics but no entity appears, and what to do when
  the cloud rejects commands.
- [Recipe: add missing ENUM values](adding-missing-enum-values.md)
