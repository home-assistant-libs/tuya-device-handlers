"""Quirks registry."""

from __future__ import annotations

from contextlib import contextmanager
import logging
import threading
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, Self

if TYPE_CHECKING:
    from collections.abc import Iterator
    import pathlib

    from tuya_sharing import CustomerDevice, DeviceFunction, DeviceStatusRange

    # We don't want to accidentally create a circular import, so we import
    # these here for type checking only
    from .device_wrapper.base import DeviceWrapper
    from .device_wrapper.service_feeder_schedule import FeederSchedule
    from .type_information import TypeInformation

_LOGGER = logging.getLogger(__name__)


class DeviceQuirkProtocol(Protocol):
    """Protocol for a Tuya device quirk."""

    original_category: str
    original_function: dict[str, DeviceFunction]
    original_local_strategy: dict[int, dict[str, Any]]
    original_status_range: dict[str, DeviceStatusRange]

    manufacturer: str | None
    model: str | None
    model_id: str | None

    @property
    def quirk_file(self) -> pathlib.Path:
        """Get the quirk file path."""

    @property
    def quirk_file_line(self) -> int:
        """Get the quirk file line number."""

    def initialise_device(self, device: CustomerDevice) -> None:
        """Initialize the device with this quirk."""

    def get_feeder_schedules_wrapper(
        self, device: CustomerDevice
    ) -> DeviceWrapper[list[FeederSchedule]] | None:
        """Get the feeder schedules wrapper for a device."""

    def get_type_information_cls(
        self, *, dpcode: str
    ) -> type[TypeInformation[Any]] | None:
        """Get the type information class override for a dpcode."""


class QuirksRegistry:
    """Registry for Tuya quirks."""

    instance: Self

    # `_quirks` is copy-on-write: it is never mutated in place, only rebound
    # to a freshly built dict. That keeps readers lock-free, which matters
    # because they run on Home Assistant's event loop (`find_dpcode`, and so
    # every `get_default_definition`, reaches `get_quirk_for_device`) while a
    # reload may be executing arbitrary user quirk modules off it. A reader
    # sees either the pre-reload or the post-reload mapping, never a
    # partially purged one, and never blocks waiting for either.
    #
    # The lock serialises *writers* only. It is defined at class level so it
    # exists before any instance does -- the `hasattr` guards in
    # `__new__`/`__init__` are not themselves atomic -- and is reentrant
    # because loading custom quirks executes quirk module bodies while the
    # lock is held, and those call `register` on the same thread.
    _lock: ClassVar[threading.RLock] = threading.RLock()

    _quirks: dict[str, DeviceQuirkProtocol]

    # Staging area while a `reloading()` block is open; None otherwise.
    _pending: dict[str, DeviceQuirkProtocol] | None

    # Snapshot of the built-in quirks, taken before any custom quirk is
    # loaded. Registration happens as an import side effect, so a built-in
    # can only ever register once per process -- without this, a custom quirk
    # that shadows a built-in `product_id` and is then deleted would take the
    # built-in with it until the host restarts.
    _builtin_quirks: dict[str, DeviceQuirkProtocol]

    def __new__(cls) -> Self:
        """Create a new class."""
        with cls._lock:
            if not hasattr(cls, "instance"):
                cls.instance = super().__new__(cls)
            return cls.instance

    def __init__(self) -> None:
        """Initialize the registry."""
        with self._lock:
            if not hasattr(self, "_quirks"):
                self._quirks = {}
                self._pending = None
                self._builtin_quirks = {}

    def capture_builtin_quirks(self) -> None:
        """Remember the built-in quirks, so a purge can restore them.

        Called once the built-in modules have been imported and before any
        custom quirk is loaded. Later calls are ignored: the first snapshot
        is already complete, since built-ins cannot register twice.
        """
        with self._lock:
            self._capture_builtin_quirks_locked()

    def _capture_builtin_quirks_locked(self) -> None:
        """Snapshot the built-in quirks. Caller must hold `_lock`."""
        if not self._builtin_quirks:
            self._builtin_quirks = dict(self._quirks)

    @contextmanager
    def reloading(self) -> Iterator[None]:
        """Stage a full purge-and-reload, publishing it as a single swap.

        Writes inside the block accumulate off to the side and become visible
        to readers all at once on exit, so no reader can observe the
        intermediate state where custom quirks have been purged but not yet
        re-registered. Readers are never blocked while the block is open.
        """
        with self._lock:
            # Nested use must not publish early or re-snapshot.
            outermost = self._pending is None
            if outermost:
                self._pending = dict(self._quirks)
            try:
                yield
            finally:
                if outermost:
                    pending, self._pending = self._pending, None
                    if TYPE_CHECKING:
                        assert pending is not None
                    self._quirks = pending

    def register(
        self,
        product_id: str,
        quirk: DeviceQuirkProtocol,
    ) -> None:
        """Register a quirk for a specific device type."""
        with self._lock:
            self._register_locked(product_id, quirk)

    def _register_locked(
        self,
        product_id: str,
        quirk: DeviceQuirkProtocol,
    ) -> None:
        """Register a quirk. Caller must hold `_lock`.

        Writes land in the staging copy while a `reloading()` block is open,
        so they stay invisible to readers until it publishes. Otherwise
        `_quirks` is rebound rather than mutated, to keep readers lock-free.
        """
        if self._pending is not None:
            self._pending[product_id] = quirk
        else:
            self._quirks = {**self._quirks, product_id: quirk}

    def get_quirk_for_device(
        self, device: CustomerDevice
    ) -> DeviceQuirkProtocol | None:
        """Get the quirk for a specific device."""
        # Deliberately lock-free: this runs on the host's event loop.
        return self._quirks.get(device.product_id)

    def initialise_device_quirk(self, device: CustomerDevice) -> None:
        """Apply the quirk to a specific device."""
        if quirk := self._quirks.get(device.product_id):
            quirk.initialise_device(device)

    def purge_custom_quirks(self, custom_quirks_root: str) -> None:
        """Purge custom quirks from the registry."""
        with self._lock:
            self._purge_custom_quirks_locked(custom_quirks_root)

    def _purge_custom_quirks_locked(self, custom_quirks_root: str) -> None:
        """Purge custom quirks. Caller must hold `_lock`.

        A custom quirk that shadows a built-in is replaced by the built-in
        rather than dropped: quirks register as an import side effect, so the
        built-in could not register itself again.
        """
        staged = self._pending is not None
        target = self._pending if staged else dict(self._quirks)
        if TYPE_CHECKING:
            assert target is not None

        to_remove = [
            product_id
            for product_id, quirk in target.items()
            if quirk.quirk_file.is_relative_to(custom_quirks_root)
        ]

        for product_id in to_remove:
            if (builtin := self._builtin_quirks.get(product_id)) is not None:
                # The custom quirk was shadowing a built-in; uncover it
                # rather than dropping support for the device entirely.
                _LOGGER.debug(
                    "Restoring built-in quirk shadowed by custom: %s",
                    product_id,
                )
                target[product_id] = builtin
            else:
                _LOGGER.debug("Removing stale custom quirk: %s", product_id)
                target.pop(product_id, None)

        if not staged:
            # Publish as one swap; readers never see a partial purge.
            self._quirks = target
