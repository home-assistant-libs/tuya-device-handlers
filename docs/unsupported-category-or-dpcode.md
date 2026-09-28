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

| Symptom                                                                                                              | Where the fix belongs                                         |
| -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| A datapoint is **absent from the diagnostics**, or present with the wrong type, unit, scale, or a missing ENUM value | **Here** — write a quirk                                      |
| Device shows up as the wrong kind of thing (thermostat instead of a valve, …)                                        | **Here** — write a quirk                                      |
| A datapoint **is in the diagnostics** but never becomes an entity                                                    | [home-assistant/core](https://github.com/home-assistant/core) |
| Device creates **no entities at all** and its category is unknown to core                                            | [home-assistant/core](https://github.com/home-assistant/core) |

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
  your diagnostics.

- **The datapoint is there, with a sensible value in `status`, but no entity
  appeared.** Nothing for a quirk to rewrite. Continue below.

The same applies when _nothing_ appeared: if `function`, `status_range` and
`status` are all populated and correct, the datapoints aren't the problem.

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
