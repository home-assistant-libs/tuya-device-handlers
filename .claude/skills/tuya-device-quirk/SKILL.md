---
name: tuya-device-quirk
description: How to add, test and review a Tuya device quirk in this repository, including turning a Home Assistant diagnostics file into a test fixture. Use this as the primary reference for any change under src/tuya_device_handlers/devices/, tests/devices/ or tests/fixtures/devices/.
---

## File locations

- **Quirk module**: `src/tuya_device_handlers/devices/<category>/<category>_<product_id_lowercased>.py`
- **Fixture**: `tests/fixtures/devices/<category>_<product_id>.json`
- **Tests**: `tests/devices/<category>/test_<product_id>.py`

`<category>` is the device's two-letter Tuya category code (e.g. `cl`, `cz`, `wk`). A new category also needs an `__init__.py` in both `devices/<category>/` and `tests/devices/<category>/`. Quirks are discovered by import, so there is no manifest to update.

## Rules

- A quirk can only rewrite datapoints (`function`, `status_range`, `local_strategy`). If a datapoint is already present and correct in the diagnostics but never becomes an entity, the fix belongs in Home Assistant Core, not here (see [docs/unsupported-category-or-dpcode.md](../../../docs/unsupported-category-or-dpcode.md)).
- Each quirk file contains exactly one `DeviceQuirk()...register(TUYA_QUIRKS_REGISTRY)` chain at module top level. Provenance (`quirk_file`/`quirk_file_line`) and custom-quirk reload depend on it.
- Quirk modules have a module docstring that explains what is wrong with the device and links the upstream issue when there is one.
- Use the enums in `tuya_device_handlers.helpers.homeassistant` rather than importing Home Assistant.
- For custom scaling/encoding of a single datapoint, use `.override_dpid_type_information_cls(...)` with a class from `type_information_ex.py` instead of a custom wrapper.
- Every new quirk needs a fixture built from a real diagnostics file **and** tests that load it via `create_device("<fixture>.json")`. Where the quirk changes behaviour, tests should ideally show it both without the quirk (`patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True)`) and with it (`filled_quirks_registry.initialise_device_quirk(device)`). See `tests/devices/cl/test_68nvbio9.py`.

For a worked example of the most common fix (missing ENUM values), see [docs/adding-missing-enum-values.md](../../../docs/adding-missing-enum-values.md).

## Converting a diagnostics file into a fixture

Device support requests usually attach a Home Assistant diagnostics JSON (downloaded from the device's diagnostics, or from a `github.com/user-attachments/...` link on the issue). To turn one into a fixture:

1. Take **only the contents of the top-level `data` property**. That object is the captured `CustomerDevice` payload. Discard everything else (`home_assistant`, `custom_components`, `integration_manifest`, `setup_times`, `issues`, …).
2. From that object, **remove the `id`, `terminal_id`, and `home_assistant` keys**. `id`/`terminal_id` are per-account identifiers; `home_assistant` is a nested diagnostics block, not part of the device payload.
3. Write the result to `tests/fixtures/devices/<category>_<product_id>.json`, using the device's own `category` and `product_id` fields for the filename (e.g. a `cl` device with product id `nfq1essvr99qsvvd` → `cl_nfq1essvr99qsvvd.json`). Pretty-print with 2-space indent and a trailing newline.

One-liner (input `diag.json`):

```bash
python3 -c "
import json
d = json.load(open('diag.json'))['data']
for k in ('id', 'terminal_id', 'home_assistant'):
    d.pop(k, None)
name = f\"tests/fixtures/devices/{d['category']}_{d['product_id']}.json\"
with open(name, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
    f.write('\n')
print(name)
"
```

## Reviewing a quirk PR

Check that:

- the fixture contains no `id`, `terminal_id` or `home_assistant` keys, and its filename matches its `category` and `product_id`;
- the quirk filename, `applies_to(product_id=...)` and the fixture agree on the product id;
- the tests exercise what the quirk changes, rather than only asserting that it registers;
- the change does not belong in Home Assistant Core instead (see Rules above).
