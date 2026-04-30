# Tuya quirks library

[![PyPI](https://img.shields.io/pypi/v/tuya-device-handlers.svg)][pypi_]
[![Python Version](https://img.shields.io/pypi/pyversions/tuya-device-handlers)][python version]
[![License](https://img.shields.io/pypi/l/tuya-device-handlers)][license]

[![Read the documentation at https://tuya-device-handlers.readthedocs.io/](https://img.shields.io/readthedocs/tuya-device-handlers/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/home-assistant-libs/tuya-device-handlers/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/home-assistant-libs/tuya-device-handlers/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)][ruff]

[pypi_]: https://pypi.org/project/tuya-device-handlers/
[python version]: https://pypi.org/project/tuya-device-handlers
[read the docs]: https://tuya-device-handlers.readthedocs.io/
[tests]: https://github.com/home-assistant-libs/tuya-device-handlers/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/home-assistant-libs/tuya-device-handlers
[pre-commit]: https://github.com/pre-commit/pre-commit
[ruff]: https://github.com/astral-sh/ruff

## What is this?

`tuya-device-handlers` is a "quirks" library used by Home Assistant's [Tuya integration][ha-tuya] to fix or normalise misbehaving Tuya devices. A quirk is matched against a device's `product_id` and patches its datapoints (function/status_range/local_strategy) before Home Assistant builds entities from them.

The library is shipped to end users via Home Assistant — you do not install it directly.

## Writing a quirk

### 1. Find your device's `product_id` and datapoints

In Home Assistant: **Settings → Devices & services → Tuya → your device → Download diagnostics**. The JSON contains the `product_id`, the cloud-reported `function` / `status_range` maps, and the current `status` values. Use these to decide what needs patching.

### 2. Create a quirk file

Drop a Python file into your Home Assistant config folder at `<config>/tuya_quirks/<category>_<product_id_lowercased>.py`. The `<category>` prefix follows Tuya's [official category codes][tuya-categories] (e.g. `cz` for plug/socket, `wk` for thermostat, `cl` for curtain).

Quirks are built using a fluent `DeviceQuirk` builder. Minimal example — redefine one datapoint and remove another:

```python
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="abcdEFGHijkl1234")
    .add_dpid_integer(
        dpid=18,
        dpcode="cur_current",
        dpmode=DPMode.READ,
        unit="mA", min=0, max=30000, scale=0, step=1,
    )
    .remove_dpid(dpid=22, dpcode="phantom_dp")
    .register(TUYA_QUIRKS_REGISTRY)
)
```

Each quirk file should contain exactly one `DeviceQuirk()...register(...)` chain at module top level — the file path is captured for reload tracking. Available builder methods include `add_dpid_boolean`, `add_dpid_bitmap`, `add_dpid_enum`, `add_dpid_integer`, and `remove_dpid`. For more complex needs (custom value scaling, platform-specific definitions), see the in-tree examples under [`src/tuya_device_handlers/devices/`][devices-dir].

### 3. Test it inside Home Assistant

1. Restart the Tuya integration (**Settings → Devices & services → Tuya → ⋮ → Reload**). Quirks under `<config>/tuya_quirks/` are reloaded each time, so you don't need to restart Home Assistant itself.
2. Watch the logs — you should see `Loading custom quirk module …` followed by `Loaded custom quirks. Please contribute them to https://github.com/home-assistant-libs/tuya-device-handlers`. If the import fails, the traceback is logged.
3. Verify the device's entities reflect your changes (download diagnostics again to confirm the patched function/status_range maps).

## Contributing your quirk

Once your quirk works, please open a pull request so other Home Assistant users benefit.

1. Fork and clone this repository, then run `poetry install`.
2. Move your quirk file from `<config>/tuya_quirks/` to `src/tuya_device_handlers/devices/<category>/`. The filename should match `<category>_<product_id_lowercased>.py`.
3. Add a device fixture JSON at `tests/fixtures/devices/<category>_<product_id>.json`. The easiest source is the `function`/`status_range`/`status` blocks from your Home Assistant diagnostics download.
4. Add a test under `tests/devices/<category>/` covering the patched behaviour.
5. Run the test suite locally:

   ```console
   nox --session=tests
   ```

6. Open a [pull request]. Coverage must stay at 100% and CI runs `pre-commit`, `mypy`, `tests`, `typeguard`, and `docs-build`.

For broader contributor guidelines (issue reporting, dev setup, pre-commit hooks), see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_Tuya quirks library_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[ha-tuya]: https://www.home-assistant.io/integrations/tuya/
[tuya-categories]: https://developer.tuya.com/en/docs/iot/standarddescription?id=K9i5ql6waswzq
[devices-dir]: https://github.com/home-assistant-libs/tuya-device-handlers/tree/main/src/tuya_device_handlers/devices
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/home-assistant-libs/tuya-device-handlers/issues
[pull request]: https://github.com/home-assistant-libs/tuya-device-handlers/pulls

<!-- github-only -->

[license]: https://github.com/home-assistant-libs/tuya-device-handlers/blob/main/LICENSE
[contributor guide]: https://github.com/home-assistant-libs/tuya-device-handlers/blob/main/CONTRIBUTING.md
