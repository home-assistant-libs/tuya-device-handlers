# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`tuya-device-handlers` is a Python library of "quirks" for Tuya devices. It patches `tuya_sharing.CustomerDevice` instances (functions, status_range, local_strategy) and exposes per-platform definitions/wrappers so that Home Assistant's Tuya integration sees a corrected/normalised device. There is no CLI or runtime entry point — the library is consumed entirely by HA Core's [`homeassistant.components.tuya`](https://github.com/home-assistant/core/tree/dev/homeassistant/components/tuya), which pins it as a `requirement` in its manifest.

### Public API surface (do not break)

HA Core imports specific symbols from specific paths. Treat these as a stable contract — renames or moves require a coordinated bump of HA's pinned version.

- `tuya_device_handlers.devices.TUYA_QUIRKS_REGISTRY` and `tuya_device_handlers.devices.register_tuya_quirks` — used by `coordinator.py`. HA calls `register_tuya_quirks(<config>/tuya_quirks)` at setup and `TUYA_QUIRKS_REGISTRY.initialise_device_quirk(device)` per device. (Note: HA imports `TUYA_QUIRKS_REGISTRY` from `.devices`, not the top-level package — the re-export in `devices/__init__.py` is load-bearing.)
- `tuya_device_handlers.device_wrapper.DeviceWrapper` — used by `entity.py` as the generic type for `_read_wrapper` / `_async_send_wrapper_updates`.
- `tuya_device_handlers.definition.<platform>` — every platform module exposes `<Platform>Definition` (e.g. `ClimateDefinition`, `SensorDefinition`) **and** `get_default_definition(...)`. HA platforms call `get_default_definition(...)` as the fallback when no quirk overrides; quirks return the same dataclass type.
- `tuya_device_handlers.device_wrapper.<platform>` and `tuya_device_handlers.device_wrapper.common` — concrete wrapper classes (e.g. `ElectricityCurrentRawWrapper`, `WindDirectionEnumWrapper`, `DPCodeTypeInformationWrapper`) that HA platforms reference by name.
- `tuya_device_handlers.helpers.homeassistant` — `TuyaClimateHVACMode`, `TuyaUnitOfTemperature`, `TuyaSensorDeviceClass`, etc. HA maps these to its own enums; quirks use them so they don't import HA directly.

### The custom quirks path

`register_tuya_quirks(custom_quirks_path)` and `QuirksRegistry.purge_custom_quirks(...)` exist specifically to let HA users drop ad-hoc quirk files into `<HA config>/tuya_quirks/` and have them reloaded without restarting the integration. `purge_custom_quirks` filters by `quirk_file.is_relative_to(...)` — that is why `DeviceQuirk.__init__` captures the caller's filename via `inspect.currentframe().f_back`. Reload semantics depend on this provenance being correct, so each quirk file should produce exactly one `DeviceQuirk()` chain at module top level.

## Tooling

Poetry + Nox. Python 3.13 and 3.14 are both supported (CI runs both).

- `poetry install` — set up dev environment.
- `nox` — run the default sessions: `pre-commit`, `safety`, `mypy`, `tests`, `typeguard`, `docs-build`.
- `nox --list-sessions` — list sessions.
- `nox --session=tests` — full test suite under coverage (parallel).
- `nox --session=tests -- tests/path/to/test_file.py::test_name` — single test (posargs forward to pytest).
- `nox --session=mypy` — type-check `src`, `tests`, `docs/conf.py`.
- `nox --session=typeguard` — runtime type checking via pytest.
- `nox --session=coverage` — combine `.coverage.*` shards and report.
- `nox --session=pre-commit -- install` — install git hooks (also patches them to use the nox virtualenv).

The project targets 100% coverage. Ruff config lives in [pyproject.toml](pyproject.toml) (line-length 80, isort with `force-sort-within-sections`, mccabe max-complexity 10). Mypy is in `strict` mode.

## Architecture

### Registry and the quirks lookup path

[src/tuya_device_handlers/\_\_init\_\_.py](src/tuya_device_handlers/__init__.py) exposes `TUYA_QUIRKS_REGISTRY`, the single `QuirksRegistry` instance consumers import. The registry is a singleton: `QuirksRegistry.__new__` reuses the class-level `instance`, and `__init__` is guarded to not wipe `_quirks` on re-instantiation (see commit `e4cf692`). Treat re-instantiation as a no-op — never reset state by constructing a new registry.

`QuirksRegistry` ([src/tuya_device_handlers/registry.py](src/tuya_device_handlers/registry.py)) maps `product_id → DeviceQuirkProtocol`. The protocol has three keys: `original_function`/`original_local_strategy`/`original_status_range` (snapshots taken at apply time), `quirk_file`/`quirk_file_line` (provenance for diagnostics), and `initialise_device(device)` (the mutation step).

`purge_custom_quirks(custom_quirks_root)` filters quirks by `quirk_file.is_relative_to(...)` — this is what makes user-supplied quirks reloadable without restarting the host. Built-in quirks are not affected.

### Loading quirks

[src/tuya_device_handlers/devices/\_\_init\_\_.py](src/tuya_device_handlers/devices/__init__.py) — `register_tuya_quirks(custom_quirks_path=None)`:

1. Purge previously-loaded custom quirks (by file path).
2. `pkgutil.walk_packages` over the `devices/` subpackage: importing each module registers its quirks as a side effect (the module body runs the `DeviceQuirk()...register(TUYA_QUIRKS_REGISTRY)` chain).
3. If `custom_quirks_path` is set, walk that directory and import each module via `importlib.util` so user quirks register the same way.

Quirk discovery is therefore import-driven. A new quirk file under `src/tuya_device_handlers/devices/<category>/` is picked up automatically — there is no manifest.

### Building a quirk

[src/tuya_device_handlers/builder/device_quirk.py](src/tuya_device_handlers/builder/device_quirk.py) — `DeviceQuirk` is a fluent builder:

```python
(
    DeviceQuirk()
    .applies_to(product_id="...")
    .add_dpid_integer(dpid=..., dpcode="...", dpmode=DPMode.READ | DPMode.WRITE, ...)
    .remove_dpid(dpid=..., dpcode="...")
    .register(TUYA_QUIRKS_REGISTRY)
)
```

`__init__` captures the caller's filename/lineno via `inspect.currentframe().f_back` for `quirk_file*` — each quirk file should produce exactly one `DeviceQuirk()` chain at module top level so provenance points at the right line.

`initialise_device` snapshots the device's original maps then walks `_datapoint_definitions`. For each entry it adds/removes from `device.function` (WRITE flag), `device.status_range` (READ flag), and `device.local_strategy` (only when `device.support_local`). A `None` value means "remove this dpid/dpcode entirely".

`DPMode` is an `IntFlag` (`READ=1`, `WRITE=2`) so combine with `|`. `DPType` is a `StrEnum` and has a forgiving `try_parse` for ill-formed cloud values (see [const.py](src/tuya_device_handlers/const.py)).

### Device categories

`devices/<two-letter-category>/<category>_<product_id_lowercased>.py`. Categories follow Tuya's official codes (e.g. `cl` curtain, `cz` plug/socket, `wk` thermostat) — the `__init__.py` of each category links to the relevant Tuya developer doc.

### Definitions and wrappers

These two layers exist because the cloud-side device shape (datapoints) doesn't map 1:1 to Home Assistant entities.

- `definition/` — per-platform dataclasses (`TuyaClimateDefinition`, etc.) the host integration consumes to build HA entities. All inherit from `BaseEntityQuirk` ([base.py](src/tuya_device_handlers/definition/base.py)) with a single `key` field.
- `device_wrapper/` — `DeviceWrapper[T]` + typed `DPCodeWrapper[T]` subclasses (`DPCodeBooleanWrapper`, `DPCodeIntegerWrapper`, …) that encapsulate the read/write conversion between a raw DPCode value and the HA-facing value. `read_device_status` and `_convert_value_to_raw_value` are the override points; `find_dpcode(device, code, prefer_function=...)` is the standard lookup. Override these in a quirk file when a device needs custom scaling/encoding (see the `CustomIntegerTypeDefinition` example in [devices/wk/wk_iayz2wk1th0cmlml.py](src/tuya_device_handlers/devices/wk/wk_iayz2wk1th0cmlml.py)).
- `raw_data_model.py` — parsers for base64-encoded RAW DPs (e.g. `ElectricityData.from_bytes` handles legacy/v01/v02 layouts).

### Helpers

[helpers/homeassistant.py](src/tuya_device_handlers/helpers/homeassistant.py) re-exports HA enums (`TuyaSensorDeviceClass`, `TuyaEntityCategory`, `TuyaUnitOfTemperature`, …) so quirks don't import Home Assistant directly. Keep new HA-shaped constants here.

## Tests

`tests/` mirrors `src/tuya_device_handlers/`. Per-device JSON fixtures live under [tests/fixtures/devices/](tests/fixtures/devices/) named `<category>_<product_id>.json` — these capture real `CustomerDevice` payloads. Snapshot tests use `syrupy` (`__snapshots__/` directories). [tests/conftest.py](tests/conftest.py) provides `mock_device` (a `CustomerDevice` Mock pre-populated with `demo_*` DPs covering every `DPType`) and `filled_quirks_registry` (calls `register_tuya_quirks()` once per module).

When adding a new device quirk: add a fixture JSON, add the quirk module under `devices/<category>/`, and add tests under `tests/devices/<category>/`.
