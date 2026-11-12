# Recipe: missing entities (unknown category or DPCode)

Some problems can't be fixed by a quirk in this repository, no matter how good
the diagnostics are. This applies whether your device produces **no entities at
all** or just **some of them** — a plug that exposes its switch but none of its
power readings hits the same wall as a device that shows up empty.

This page helps you tell the two cases apart and points you at the right place
to fix each one.

## The short version

A quirk in this repository can only rewrite a device's **datapoints** — the
`function`, `status_range` and `local_strategy` maps that Tuya's cloud reports.
Turning a datapoint into a Home Assistant entity is core's job, and core can
only do that for a **device category** and a **DPCode** it knows about.

| Symptom                                                                                                              | Where the fix belongs                                                                      |
| -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| A datapoint is **absent from the diagnostics**, or present with the wrong type, unit, scale, or a missing ENUM value | **Here** — write a quirk                                                                   |
| Device shows up as the wrong kind of thing (thermostat instead of a valve, …)                                        | **Here** — write a quirk                                                                   |
| A datapoint **is in the diagnostics** but never becomes an entity                                                    | [home-assistant/core](https://github.com/home-assistant/core)                              |
| Device creates **no entities at all** and its category is unknown to core                                            | [home-assistant/core](https://github.com/home-assistant/core)                              |
| Entities show the right state, but the **cloud rejects commands** with error `2008`                                  | Neither — see [Commands rejected by the cloud](#commands-rejected-by-the-cloud-error-2008) |

The discriminator for a missing entity is simple:

> **Is the datapoint in your diagnostics?**
> No → a quirk here can add it. Yes → core has to map it.

---

## Step 1 — List what's missing, and check the diagnostics for it

Download the device's diagnostics (**Settings → Devices & services → Tuya →
your device → the ⋮ menu → Download diagnostics**) and look at the `data`
object:

```json
{
  "data": {
    "category": "znjdq",
    "product_id": "au6dqazvkxqnpaak",
    "function": { "switch_1": {}, "countdown_1": {}, "relay_status": {} },
    "status_range": { "cur_power": {}, "cur_voltage": {}, "add_ele": {} },
    "status": { "switch_1": true, "cur_voltage": 2073 }
  }
}
```

Write down each entity you expected but didn't get, and find the datapoint it
would come from.

- **The datapoint isn't in `function` or `status_range` at all.** Tuya's cloud
  never told Home Assistant about it. That's exactly what a quirk fixes —
  see the [main README](../README.md) and the
  [ENUM recipe](adding-missing-enum-values.md), and open an issue here with
  your diagnostics. If you don't know the datapoint's dpid, see
  [Finding the datapoints](#finding-the-datapoints) below.

- **The datapoint is there, with a sensible value in `status`, but no entity
  appeared.** Nothing for a quirk to rewrite. Continue below.

The same applies when _nothing_ appeared: if `function`, `status_range` and
`status` are all populated and correct, the datapoints aren't the problem.

### Finding the datapoints

A quirk adds a datapoint by its dpid. When the diagnostics don't list it, the
device may still send it in its reports, keyed by dpid, and the Tuya SDK logs
each one it can't map. This only works when both are true:

- the device has `"support_local": true` in its diagnostics: other devices
  report by code rather than dpid;
- the device already has at least one entity in Home Assistant: the SDK only
  listens for reports from devices that have one.

So the debug log helps when _some_ datapoints are missing. For a device with no
entities at all, typically when `function`, `status_range`, `local_strategy`
and `status` are all empty, read the device's thing model instead: see
[Reading the thing model](#reading-the-thing-model) below.

1. Turn on **Enable debug logging** on the Tuya integration page. It covers the
   Tuya SDK (`tuya_sharing`).
2. Use the device from its app or its buttons, so it sends reports.
3. Look for lines like these:

   ```text
   mq _on_device_report-> [{'dpId': 101, 't': 1794096541000, 'value': True}]
   mq _on_device_report unknown dpId: 101
   ```

   The first line lists the dpids and values in the report. `unknown dpId`
   means `local_strategy` has no entry for that dpid, which is what a quirk
   adds.

Change one thing at a time on the device to tell the dpids apart: a door
sensor's `True` / `False` flips as the door opens and closes, for example.
Then add each datapoint with the builder method for its type, under the code
core expects for your category (see Step 3 below). A read-only datapoint can
take the standard code, as
[`tdq_a9fn0xcsckjoqpnd.py`](../src/tuya_device_handlers/devices/tdq/tdq_a9fn0xcsckjoqpnd.py)
does with `doorcontact_state`.

To contribute the quirk, build its test fixture from your diagnostics as
described in
[Converting a diagnostics file into a fixture](../.claude/skills/tuya-device-quirk/SKILL.md#converting-a-diagnostics-file-into-a-fixture),
and add a test that a report keyed by dpid updates the right code, like
`test_mqtt` in
[`tests/devices/tdq/test_a9fn0xcsckjoqpnd.py`](../tests/devices/tdq/test_a9fn0xcsckjoqpnd.py).

#### Reading the thing model

The log only shows the datapoints the device reports while you watch, and
nothing for a device with no entities. The device's thing model lists all of
them, with their types, ranges and whether they can be written. There are two
ways to read it, both from Tuya. In both, `<device_id>` is the `id` field in
your diagnostics.

- **Online, on the [Tuya IoT Platform](https://iot.tuya.com):** in your cloud
  project, go to **Cloud → API Explorer → Device Control**, and run **Query
  Things Data Model** with your device id. This needs a Tuya developer account,
  with your Smart Life or Tuya Smart account linked to the project.
- **From a terminal, with Tuya's
  [tuya-smart-control-cli](https://github.com/tuya/tuya-smart-control-cli):**
  follow its README to install it and create an API key, then run:

  ```console
  tuya device model <device_id> --json
  ```

> **With the CLI, the API key must belong to the app account that owns the
> device.** Tuya Smart and Smart Life are separate apps with separate accounts,
> and a key only sees devices in its own account's homes. If the command fails
> with `40000905` ("The user does not have device permissions"), check which
> app the device was added with, then use a key for that account.

Each entry in `properties` is one datapoint, for example:

```json
{
  "abilityId": 102,
  "accessMode": "ro",
  "code": "battery_state",
  "typeSpec": {
    "type": "enum",
    "range": ["low", "middle", "high"]
  }
}
```

| Thing model field | Quirk argument                                                       |
| ----------------- | -------------------------------------------------------------------- |
| `abilityId`       | `dpid`                                                               |
| `code`            | `dpcode`                                                             |
| `accessMode`      | `dpmode`: `rw` → `DPMode.READ \| DPMode.WRITE`, `ro` → `DPMode.READ` |
| `typeSpec`        | the builder method and its arguments, from the table below           |

| `typeSpec.type` | Builder method     | Arguments from `typeSpec`             |
| --------------- | ------------------ | ------------------------------------- |
| `bool`          | `add_dpid_boolean` | none                                  |
| `value`         | `add_dpid_integer` | `min`, `max`, `scale`, `step`, `unit` |
| `enum`          | `add_dpid_enum`    | `range` → `enum_range`                |
| `bitmap`        | `add_dpid_bitmap`  | `label` → `label_range`               |

Include the output, or the relevant part of it, in your issue or pull request.

## Step 2 — Is the category known to core?

Open [`homeassistant/components/tuya/const.py`][core-const] and search the
`DeviceCategory` enum for your `category` value.

```python
class DeviceCategory(StrEnum):
    """Tuya device categories."""

    DLQ = "dlq"
    """Circuit breaker

    https://developer.tuya.com/en/docs/iot/dlq?id=Kb0kidk9enyh8
    """
```

**Not there?** Core has no mapping from your device to any platform, so it
creates no entities at all — and a quirk cannot change that. Go to Step 4.

## Step 3 — Is the DPCode known, and mapped for your category?

If the category exists but only _some_ entities appeared, there are two things
to check, and you may need both.

**Is the code in the `DPCode` enum?** Still in [`const.py`][core-const],
search for each datapoint code that never became an entity:

```python
ADD_ELE = "add_ele"  # energy
CUR_CURRENT = "cur_current"  # Actual current
CUR_POWER = "cur_power"  # Actual power
CUR_VOLTAGE = "cur_voltage"  # Actual voltage
```

A code that isn't in `DPCode` cannot be referenced by any entity description,
so it is silently ignored.

> This is why [#329](https://github.com/home-assistant-libs/tuya-device-handlers/issues/329)
> couldn't be solved with a quirk: the water tester reported `cf_current`,
> `tds_current` and friends, which core simply had no `DPCode` for.

**Is there a description for it under your category?** Each platform file
(`sensor.py`, `switch.py`, `climate.py`, …) maps a category to a tuple of
entity descriptions. A DPCode that exists in the enum still produces no entity
unless _your_ category's tuple references it — which is the usual reason a
device gets its switch but not its power sensors. A category can also be
missing from one platform while present in another.

## Step 4 — Open a pull request against home-assistant/core

The change is usually small, and you may need only some of these:

1. A new `DeviceCategory` member in `const.py`, with a docstring naming the
   device type and, if you can find it, a link to the
   [Tuya category documentation](https://developer.tuya.com/en/docs/iot/standarddescription?id=K9i5ql6waswzq).
2. Any missing `DPCode` members, likewise in `const.py`.
3. An entity description per platform your device needs, keyed on the category.
   Copy the closest existing category — a metering circuit breaker looks a lot
   like `DLQ`:

   ```python
   SWITCHES: dict[DeviceCategory, tuple[SwitchEntityDescription, ...]] = {
       DeviceCategory.DLQ: (
           SwitchEntityDescription(
               key=DPCode.CHILD_LOCK,
               translation_key="child_lock",
               entity_category=EntityCategory.CONFIG,
           ),
           SwitchEntityDescription(
               key=DPCode.SWITCH,
               translation_key="switch",
           ),
       ),
   }
   ```

4. Translations for any new `translation_key` you introduce, in
   `homeassistant/components/tuya/strings.json`.

Attach your diagnostics to the pull request — core's Tuya tests are snapshot
based and reviewers will want the real payload. Follow the
[Home Assistant developer documentation](https://developers.home-assistant.io/docs/development_index)
for setting up the environment and submitting the PR.

## Commands rejected by the cloud (error `2008`)

A quirk can add a datapoint the cloud doesn't list, and Home Assistant then
reads it from the device's reports. Commands are different: Home Assistant
sends them through the Tuya cloud, by DPCode, and the cloud decides whether to
accept them. A quirk can change what Home Assistant sends (which code, which
values), but not whether the cloud accepts it.

We don't know the exact rules the cloud applies. Commands for datapoints or
ENUM values missing from the cloud's definition (`original_function` in
diagnostics taken with a quirk active) are typically rejected with error
`2008`, but the cloud may also reject commands for datapoints it does list.

Neither this library nor core can work around it: commands can't be sent by
dpId, and the integration has no local control. Only the manufacturer (or
Tuya support) can change what the Tuya cloud accepts.

A quirk is still worth contributing for the readings. Declare the datapoints
that are meant to be writable as `DPMode.READ | DPMode.WRITE` anyway, and
mention the limitation in the quirk's docstring.

## What to do with your issue here

If you already opened an issue in this repository, say what you found and link
the core pull request or issue. Leave the issue open only if there is _also_ a
datapoint problem that a quirk should fix — for example some datapoints are
unmapped in core **and** a `mode` datapoint in the diagnostics is missing
values. In that case the core change lands first, and the quirk follows once
entities exist to correct.

## Related

- [Recipe: add missing ENUM values](adding-missing-enum-values.md) — for the
  common case that _is_ fixable with a quirk.

[core-const]: https://github.com/home-assistant/core/blob/dev/homeassistant/components/tuya/const.py
