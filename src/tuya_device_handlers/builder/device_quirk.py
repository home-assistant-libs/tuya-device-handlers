"""Base quirk definition."""

from collections.abc import Sequence
from dataclasses import dataclass
import inspect
import pathlib
from typing import TYPE_CHECKING, Any, Self

from tuya_device_handlers.const import DPType
from tuya_device_handlers.definition.alarm_control_panel import (
    AlarmControlPanelQuirk,
)
from tuya_device_handlers.definition.binary_sensor import BinarySensorQuirk
from tuya_device_handlers.definition.button import ButtonQuirk
from tuya_device_handlers.definition.camera import CameraQuirk
from tuya_device_handlers.definition.climate import ClimateQuirk
from tuya_device_handlers.definition.cover import CoverQuirk
from tuya_device_handlers.definition.event import EventQuirk
from tuya_device_handlers.definition.fan import FanQuirk
from tuya_device_handlers.definition.humidifier import HumidifierQuirk
from tuya_device_handlers.definition.light import LightQuirk
from tuya_device_handlers.definition.number import NumberQuirk
from tuya_device_handlers.definition.select import SelectQuirk
from tuya_device_handlers.definition.sensor import SensorQuirk
from tuya_device_handlers.definition.siren import SirenQuirk
from tuya_device_handlers.definition.switch import SwitchQuirk
from tuya_device_handlers.definition.vacuum import VacuumQuirk
from tuya_device_handlers.definition.valve import ValveQuirk
from tuya_device_handlers.registry import DeviceQuirkProtocol, QuirksRegistry


@dataclass(kw_only=True)
class DatapointDefinition:
    """Definition for a Tuya datapoint."""

    dpid: int
    dpcode: str
    dptype: DPType
    enum_range: list[str] | None = None
    int_range: dict[str, Any] | None = None
    label_range: list[str] | None = None


class DeviceQuirk(DeviceQuirkProtocol):
    """Quirk for Tuya device."""

    _alarm_control_panel: list[AlarmControlPanelQuirk] | None = None
    _binary_sensor: list[BinarySensorQuirk] | None = None
    _button: list[ButtonQuirk] | None = None
    _camera: list[CameraQuirk] | None = None
    _climate: list[ClimateQuirk] | None = None
    _cover: list[CoverQuirk] | None = None
    _event: list[EventQuirk] | None = None
    _fan: list[FanQuirk] | None = None
    _humidifier: list[HumidifierQuirk] | None = None
    _light: list[LightQuirk] | None = None
    _number: list[NumberQuirk] | None = None
    _select: list[SelectQuirk] | None = None
    _sensor: list[SensorQuirk] | None = None
    _siren: list[SirenQuirk] | None = None
    _switch: list[SwitchQuirk] | None = None
    _vacuum: list[VacuumQuirk] | None = None
    _valve: list[ValveQuirk] | None = None

    def __init__(self) -> None:
        """Initialize the quirk."""
        self._applies_to: list[tuple[str, str]] = []

        self.datapoint_definitions: dict[int, DatapointDefinition] = {}

        current_frame = inspect.currentframe()
        if TYPE_CHECKING:
            assert current_frame is not None
        caller = current_frame.f_back
        if TYPE_CHECKING:
            assert caller is not None
        self._quirk_file = pathlib.Path(caller.f_code.co_filename)
        self._quirk_file_line = caller.f_lineno

    @property
    def quirk_file(self) -> pathlib.Path:
        """Get the file path of the quirk."""
        return self._quirk_file

    def applies_to(self, *, category: str, product_id: str) -> Self:
        """Set the device type the quirk applies to."""
        self._applies_to.append((category, product_id))
        return self

    def register(self, registry: QuirksRegistry) -> None:
        """Register the quirk in the registry."""
        for category, product_id in self._applies_to:
            registry.register(category, product_id, self)

    def add_dpid_bitmap(
        self, *, dpid: int, dpcode: str, label_range: list[str]
    ) -> Self:
        """Add datapoint Bitmap definition."""
        self.datapoint_definitions[dpid] = DatapointDefinition(
            dpid=dpid,
            dpcode=dpcode,
            dptype=DPType.BITMAP,
            label_range=label_range,
        )
        return self

    def add_dpid_boolean(self, *, dpid: int, dpcode: str) -> Self:
        """Add datapoint Boolean definition."""
        self.datapoint_definitions[dpid] = DatapointDefinition(
            dpid=dpid,
            dpcode=dpcode,
            dptype=DPType.BOOLEAN,
        )
        return self

    def add_dpid_enum(
        self, *, dpid: int, dpcode: str, enum_range: list[str]
    ) -> Self:
        """Add datapoint Enum definition."""
        self.datapoint_definitions[dpid] = DatapointDefinition(
            dpid=dpid,
            dpcode=dpcode,
            dptype=DPType.ENUM,
            enum_range=enum_range,
        )
        return self

    def add_dpid_integer(
        self, *, dpid: int, dpcode: str, int_range: dict[str, Any]
    ) -> Self:
        """Add datapoint Integer definition."""
        self.datapoint_definitions[dpid] = DatapointDefinition(
            dpid=dpid,
            dpcode=dpcode,
            dptype=DPType.INTEGER,
            int_range=int_range,
        )
        return self

    @property
    def alarm_control_panel_quirks(
        self,
    ) -> Sequence[AlarmControlPanelQuirk] | None:
        """Get alarm control panel quirks."""
        return self._alarm_control_panel

    def _add_alarm_control_panel_quirk(
        self, quirk: AlarmControlPanelQuirk
    ) -> Self:
        """Add alarm control panel definition."""
        if self._alarm_control_panel is None:
            self._alarm_control_panel = []
        self._alarm_control_panel.append(quirk)
        return self

    @property
    def binary_sensor_quirks(self) -> Sequence[BinarySensorQuirk] | None:
        """Get binary sensor quirks."""
        return self._binary_sensor

    def _add_binary_sensor_quirk(self, quirk: BinarySensorQuirk) -> Self:
        """Add binary sensor definition."""
        if self._binary_sensor is None:
            self._binary_sensor = []
        self._binary_sensor.append(quirk)
        return self

    @property
    def button_quirks(self) -> Sequence[ButtonQuirk] | None:
        """Get button quirks."""
        return self._button

    def _add_button_quirk(self, quirk: ButtonQuirk) -> Self:
        """Add button definition."""
        if self._button is None:
            self._button = []
        self._button.append(quirk)

        return self

    @property
    def camera_quirks(self) -> Sequence[CameraQuirk] | None:
        """Get camera quirks."""
        return self._camera

    def _add_camera_quirk(self, quirk: CameraQuirk) -> Self:
        """Add camera definition."""
        if self._camera is None:
            self._camera = []
        self._camera.append(quirk)
        return self

    @property
    def climate_quirks(self) -> Sequence[ClimateQuirk] | None:
        """Get climate quirks."""
        return self._climate

    def _add_climate_quirk(self, quirk: ClimateQuirk) -> Self:
        """Add climate definition."""
        if self._climate is None:
            self._climate = []
        self._climate.append(quirk)
        return self

    @property
    def cover_quirks(self) -> Sequence[CoverQuirk] | None:
        """Get cover quirks."""
        return self._cover

    def _add_cover_quirk(self, quirk: CoverQuirk) -> Self:
        """Add cover definition."""
        if self._cover is None:
            self._cover = []
        self._cover.append(quirk)
        return self

    @property
    def event_quirks(self) -> Sequence[EventQuirk] | None:
        """Get event quirks."""
        return self._event

    def _add_event_quirk(self, quirk: EventQuirk) -> Self:
        """Add event definition."""
        if self._event is None:
            self._event = []
        self._event.append(quirk)
        return self

    @property
    def fan_quirks(self) -> Sequence[FanQuirk] | None:
        """Get fan quirks."""
        return self._fan

    def _add_fan_quirk(self, quirk: FanQuirk) -> Self:
        """Add fan definition."""
        if self._fan is None:
            self._fan = []
        self._fan.append(quirk)
        return self

    @property
    def humidifier_quirks(self) -> Sequence[HumidifierQuirk] | None:
        """Get humidifier quirks."""
        return self._humidifier

    def _add_humidifier_quirk(self, quirk: HumidifierQuirk) -> Self:
        """Add humidifier definition."""
        if self._humidifier is None:
            self._humidifier = []
        self._humidifier.append(quirk)
        return self

    @property
    def light_quirks(self) -> Sequence[LightQuirk] | None:
        """Get light quirks."""
        return self._light

    def _add_light_quirk(self, quirk: LightQuirk) -> Self:
        """Add light definition."""
        if self._light is None:
            self._light = []
        self._light.append(quirk)
        return self

    @property
    def number_quirks(self) -> Sequence[NumberQuirk] | None:
        """Get number quirks."""
        return self._number

    def _add_number_quirk(self, quirk: NumberQuirk) -> Self:
        """Add number definition."""
        if self._number is None:
            self._number = []
        self._number.append(quirk)
        return self

    @property
    def select_quirks(self) -> Sequence[SelectQuirk] | None:
        """Get select quirks."""
        return self._select

    def _add_select_quirk(self, quirk: SelectQuirk) -> Self:
        """Add select definition."""
        if self._select is None:
            self._select = []
        self._select.append(quirk)
        return self

    @property
    def sensor_quirks(self) -> Sequence[SensorQuirk] | None:
        """Get sensor quirks."""
        return self._sensor

    def _add_sensor_quirk(self, quirk: SensorQuirk) -> Self:
        """Add sensor definition."""
        if self._sensor is None:
            self._sensor = []
        self._sensor.append(quirk)
        return self

    @property
    def siren_quirks(self) -> Sequence[SirenQuirk] | None:
        """Get siren quirks."""
        return self._siren

    def _add_siren_quirk(self, quirk: SirenQuirk) -> Self:
        """Add siren definition."""
        if self._siren is None:
            self._siren = []
        self._siren.append(quirk)
        return self

    @property
    def switch_quirks(self) -> Sequence[SwitchQuirk] | None:
        """Get switch quirks."""
        return self._switch

    def _add_switch_quirk(self, quirk: SwitchQuirk) -> Self:
        """Add switch definition."""
        if self._switch is None:
            self._switch = []
        self._switch.append(quirk)
        return self

    @property
    def vacuum_quirks(self) -> Sequence[VacuumQuirk] | None:
        """Get vacuum quirks."""
        return self._vacuum

    def _add_vacuum_quirk(self, quirk: VacuumQuirk) -> Self:
        """Add vacuum definition."""
        if self._vacuum is None:
            self._vacuum = []
        self._vacuum.append(quirk)
        return self

    @property
    def valve_quirks(self) -> Sequence[ValveQuirk] | None:
        """Get valve quirks."""
        return self._valve

    def _add_valve_quirk(self, quirk: ValveQuirk) -> Self:
        """Add valve definition."""
        if self._valve is None:
            self._valve = []
        self._valve.append(quirk)
        return self
