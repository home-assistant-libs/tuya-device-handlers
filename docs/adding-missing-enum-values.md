# Recipe: add missing ENUM values (e.g. extra `mode` presets)

This is a step-by-step walkthrough for a very common fix, written so you can
follow it **even if you don't write Python**. You will end up with a working
quirk, a test that proves it, and a pull request.

> **You must have the device's diagnostics file.** A contributed quirk requires
> a test fixture, and that fixture can **only** be built from a Home Assistant
> diagnostics download (Step 1). If you can't download diagnostics for the
> device, you can still write and use the quirk locally (Steps 2–3), but it
> cannot be merged without the fixture — so grab the diagnostics first.

## When to use this

Home Assistant logs a warning like:

```
Found invalid ENUM value `bheat` (<class 'str'>) for datapoint `mode`
in product id `kswbb80bbp4avryo`, expected one of `['auto']`
```

This means your device sent a value (`bheat`) that Tuya's cloud database
doesn't list for that datapoint, so Home Assistant throws it away. The result
is usually a **missing feature** — for a climate device, for example, the
`preset_mode` selector never appears because only one mode (`auto`) is known.

The fix is to **redeclare the datapoint with the full list of values** the
device actually uses.

> The example below uses issue
> [#375](https://github.com/home-assistant-libs/tuya-device-handlers/issues/375)
> (a "Weau" pool heat pump, product id `kswbb80bbp4avryo`, whose `mode`
> datapoint is missing `bheat` and other heat/cool presets). Substitute your
> own device's values as you go.

---

## Step 1 — Collect the values your device really sends

You need three things: the **product id**, the **datapoint code** (e.g.
`mode`), and **every valid value** for it.

1. **Product id + current data (required).** In Home Assistant go to
   **Settings → Devices & services → Tuya → your device → Download
   diagnostics**. **Save this JSON file and keep it** — it is required later to
   build the test fixture for your pull request, and you cannot open a PR
   without it. Near the top it contains `"product_id": "..."`.

2. **The datapoint code and its known values** come straight from the warning
   in the log (`datapoint 'mode'`, `expected one of ['auto']`).

3. **The missing values.** Each time the device sends an unknown value, Home
   Assistant logs another `Found invalid ENUM value ...` warning. Trigger every
   mode from the device's app or physical controls (Eco heat, Silent heat,
   Boost cool, …) and note the raw value from each warning. You can also read
   them from the Tuya IoT platform's **debug device** panel.

Write down the **complete** list, including the value(s) that already worked.
For the example device only `auto` (already known) and `bheat` (from the
warning) are confirmed so far; you would add each remaining raw value as you
capture it:

```
auto, bheat, <your other confirmed raw values...>
```

> ⚠️ Include the values that already work (`auto` here). The list you provide
> **replaces** the old one entirely — anything you leave out stops working.

---

## Step 2 — Write the quirk file

Create a text file named `<category>_<product_id>.py`, all lowercase. The
`<category>` is the two-letter Tuya category — for a thermostat/heat pump it is
`wk`. So for our example: `wk_kswbb80bbp4avryo.py`.

Paste this in, then edit the three highlighted parts (product id, dpid/dpcode,
and the value list):

```python
"""Quirk for Weau pool heat pump (kswbb80bbp4avryo).

The cloud database only lists `auto` for the `mode` datapoint, but the
device also reports boost/eco/silent heat & cool presets. Redeclare the
full enum range so Home Assistant exposes them as preset modes.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="kswbb80bbp4avryo")
    .add_dpid_enum(
        dpid=4,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=[
            "auto",  # already worked
            "bheat",  # Boost heat (from the warning log)
            # ...add the rest of YOUR device's confirmed raw values here...
        ],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
```

What to change:

- **`product_id="..."`** — your device's product id from Step 1.
- **`dpcode="mode"`** — the datapoint code from the warning.
- **`dpid=4`** — the datapoint's numeric id. Find it in your diagnostics JSON:
  under `local_strategy`, look for the block whose `status_code` is `mode` —
  the number that keys it is the `dpid`. (If your device has no
  `local_strategy`, any small integer works, but using the real one is best.)
- **`dpmode=DPMode.READ | DPMode.WRITE`** — keep both if Home Assistant should
  be able to _set_ the mode (the usual case). Use `DPMode.READ` alone for a
  read-only sensor.
- **`enum_range=[...]`** — your complete list from Step 1.

Keep the file to a **single** `DeviceQuirk()...register(...)` block.

### Which variant do I have — _add_ or _map_?

There are two shapes of "missing ENUM value". Check your diagnostics to tell
them apart:

- **Add (most common)** — the raw value the device sends is simply a **new
  state that isn't in the list**. The value is meaningful on its own (e.g.
  `bheat` for a boost-heat mode). Fix: add it to `enum_range` with
  `add_dpid_enum`, as above.

- **Map** — the device sends a **raw code that stands for one of the values
  already in the list, under a different name**. The clue is in your
  diagnostics: under `local_strategy`, the datapoint's `config_item` has a
  non-empty **`enumMappingMap`** that pairs Home Assistant codes with different
  raw values. For example a `mode` datapoint whose range is
  `["auto", "cold", "wet", "heat", "fan"]` but whose device sends raw `wind`
  (meaning `fan`) and `hot` (meaning `heat`). Adding `wind`/`hot` to the range
  would create bogus extra modes — instead you **translate** the raw values.

### Variant: mapping raw values with `set_dpid_strategy_to_enum`

Use this when your device reports raw codes that must be translated to the
standard values (the "Map" case above). `set_dpid_strategy_to_enum` takes an
`enum_mapping_map` of **`{raw value the device sends: value Home Assistant
should store}`**, and the stored value should be one of the values in the
datapoint's declared range.

```python
"""Quirk for <device> (<product_id>).

The device reports raw `mode` codes (`wind`, `hot`) that aren't the standard
values, so Home Assistant rejects them. Map each raw code to its real mode.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="<product_id>")
    # Make sure every target value is declared in the range...
    .add_dpid_enum(
        dpid=4,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["auto", "cold", "wet", "heat", "fan"],
    )
    # ...then translate the raw codes the device actually sends.
    .set_dpid_strategy_to_enum(
        dpid=4,
        dpcode="mode",
        enum_mapping_map={
            "wind": "fan",  # raw `wind` -> standard `fan`
            "hot": "heat",  # raw `hot`  -> standard `heat`
            # values that already match (auto/cold/wet) need no entry
        },
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
```

Notes for the mapping variant:

- The mapping is applied to values the device pushes locally (over MQTT), so
  the device must be a local one — you'll see `"support_local": true` in the
  diagnostics. If in doubt, capture the raw values from the warning logs and
  ask in the issue; a maintainer can confirm which variant fits.
- Only map the raw values that differ; values that already match a range entry
  don't need an entry.
- Keep the file to a **single** `DeviceQuirk()...register(...)` block (the two
  builder calls above are part of one chain).

> Not sure which variant you have? Attach your diagnostics to the issue and say
> which raw values appear in the warnings — that's enough for a maintainer to
> point you at the right one.

---

## Step 3 — Test it live in Home Assistant

1. Copy your file into `<config>/tuya_quirks/` (create that folder if needed) —
   e.g. `<config>/tuya_quirks/wk_kswbb80bbp4avryo.py`.
2. Reload the integration: **Settings → Devices & services → Tuya → ⋮ →
   Reload**. (No full Home Assistant restart needed.)
3. In the logs you should see `Loading custom quirk module …`. If the file has
   a typo, the error and line number are logged here.
4. Check the device — the new modes should now be selectable (for a climate
   entity, a **preset** dropdown appears with your values).

If it works, please contribute it so everyone with this device benefits. 🎉

---

## Step 4 — Turn it into a pull request

You don't need deep Git knowledge — follow these commands.

1. **Fork** this repository on GitHub (the _Fork_ button), then clone your fork
   and install the tools:

   ```console
   git clone https://github.com/<your-username>/tuya-device-handlers.git
   cd tuya-device-handlers
   poetry install
   ```

2. **Move your quirk** into the right folder (create the category folder if it
   doesn't exist):

   ```console
   mkdir -p src/tuya_device_handlers/devices/wk
   cp <path-to>/wk_kswbb80bbp4avryo.py src/tuya_device_handlers/devices/wk/
   ```

3. **Add a test fixture** from the diagnostics you downloaded in Step 1 (this
   is why that file was required). Put your `diagnostics.json` in the current
   folder; this one-liner strips the private fields and names the file for you:

   ```console
   python3 -c "
   import json
   d = json.load(open('diagnostics.json'))['data']
   for k in ('id', 'terminal_id', 'home_assistant'):
       d.pop(k, None)
   name = f\"tests/fixtures/devices/{d['category']}_{d['product_id']}.json\"
   with open(name, 'w') as f:
       json.dump(d, f, indent=2, ensure_ascii=False)
       f.write('\n')
   print('wrote', name)
   "
   ```

4. **Add a test** that proves the missing value now works. Create
   `tests/devices/wk/test_kswbb80bbp4avryo.py` with this — change only the
   fixture filename, the datapoint code, and the value you assert:

   ```python
   """Test the Weau pool heat pump mode enum quirk."""

   import json

   from tests import create_device
   from tuya_device_handlers.registry import QuirksRegistry


   def test_mode_enum_extended(
       filled_quirks_registry: QuirksRegistry,
   ) -> None:
       """The quirk adds the missing `bheat` mode value."""
       device = create_device("wk_kswbb80bbp4avryo.json")

       # BEFORE the quirk: the cloud only knows `auto`.
       before = json.loads(device.status_range["mode"].values)["range"]
       assert "bheat" not in before

       filled_quirks_registry.initialise_device_quirk(device)

       # AFTER the quirk: the full list is present.
       after = json.loads(device.status_range["mode"].values)["range"]
       assert "bheat" in after
   ```

   > Prefer a platform-level check (that the preset actually shows up as a
   > climate/fan/select option)? See
   > [`tests/devices/fs/test_xwv3jifdbhbolgh3.py`](../tests/devices/fs/test_xwv3jifdbhbolgh3.py)
   > for a real example that asserts the exposed `options`.

5. **Run the checks locally.** All three should pass:

   ```console
   poetry run pytest tests/devices/wk/test_kswbb80bbp4avryo.py
   poetry run ruff check .
   poetry run ruff format .
   ```

6. **Commit and open the PR:**

   ```console
   git checkout -b add-kswbb80bbp4avryo-quirk
   git add src/tuya_device_handlers/devices/wk/ tests/
   git commit -m "Add quirk for Weau pool heat pump (kswbb80bbp4avryo)"
   git push -u origin add-kswbb80bbp4avryo-quirk
   ```

   Then open the pull request from GitHub. In the description, mention the
   device and link the issue (e.g. `Fixes #375`).

That's it — a maintainer will review it. Thank you for contributing! 🙏
