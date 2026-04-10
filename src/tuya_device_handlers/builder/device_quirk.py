"""Base quirk definition."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
import functools
import inspect
import pathlib
from typing import TYPE_CHECKING, Any, Self

from tuya_sharing import CustomerDevice

from tuya_device_handlers.const import DPType
from tuya_device_handlers.definition.alarm_control_panel import (
    AlarmControlPanelDefinition,
    AlarmControlPanelQuirk,
    get_default_definition as get_alarm_control_panel_default_definition,
)
from tuya_device_handlers.definition.binary_sensor import (
    BinarySensorDefinition,
    BinarySensorQuirk,
    get_default_definition as get_binary_sensor_default_definition,
)
from tuya_device_handlers.definition.button import (
    ButtonDefinition,
    ButtonQuirk,
    get_default_definition as get_button_default_definition,
)
from tuya_device_handlers.definition.camera import (
    CameraDefinition,
    CameraQuirk,
    get_default_definition as get_camera_default_definition,
)
from tuya_device_handlers.definition.climate import (
    ClimateDefinition,
    ClimateQuirk,
    get_default_definition as get_climate_default_definition,
)
from tuya_device_handlers.definition.cover import (
    CoverDefinition,
    CoverQuirk,
    get_default_definition as get_cover_default_definition,
)
from tuya_device_handlers.definition.event import (
    EventDefinition,
    EventQuirk,
    get_default_definition as get_event_default_definition,
)
from tuya_device_handlers.definition.fan import (
    FanDefinition,
    FanQuirk,
    get_default_definition as get_fan_default_definition,
)
from tuya_device_handlers.definition.humidifier import (
    HumidifierDefinition,
    HumidifierQuirk,
    get_default_definition as get_humidifier_default_definition,
)
from tuya_device_handlers.definition.light import (
    LightDefinition,
    LightQuirk,
    get_default_definition as get_light_default_definition,
)
from tuya_device_handlers.definition.number import (
    NumberDefinition,
    NumberQuirk,
    get_default_definition as get_number_default_definition,
)
from tuya_device_handlers.definition.select import (
    SelectDefinition,
    SelectQuirk,
    get_default_definition as get_select_default_definition,
)
from tuya_device_handlers.definition.sensor import (
    SensorDefinition,
    SensorQuirk,
    get_default_definition as get_sensor_default_definition,
)
from tuya_device_handlers.definition.siren import (
    SirenDefinition,
    SirenQuirk,
    get_default_definition as get_siren_default_definition,
)
from tuya_device_handlers.definition.switch import (
    SwitchDefinition,
    SwitchQuirk,
    get_default_definition as get_switch_default_definition,
)
from tuya_device_handlers.definition.vacuum import (
    VacuumDefinition,
    VacuumQuirk,
    get_default_definition as get_vacuum_default_definition,
)
from tuya_device_handlers.definition.valve import (
    ValveDefinition,
    ValveQuirk,
    get_default_definition as get_valve_default_definition,
)
from tuya_device_handlers.helpers.homeassistant import TuyaUnitOfTemperature
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

    @property
    def quirk_file_line(self) -> int:
        """Get the line number of the quirk."""
        return self._quirk_file_line

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

    def add_alarm_control_panel(
        self,
        key: str,
        *,
        definition_fn: Callable[
            [CustomerDevice],
            AlarmControlPanelDefinition | None,
        ]
        | None = None,
    ) -> Self:
        """Add alarm control panel definition."""
        if definition_fn is None:
            definition_fn = get_alarm_control_panel_default_definition

        quirk = AlarmControlPanelQuirk(
            key=key,
            definition_fn=definition_fn,
        )
        return self._add_alarm_control_panel_quirk(quirk)

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

    def add_binary_sensor(
        self,
        key: str,
        *,
        definition_fn: Callable[[CustomerDevice], BinarySensorDefinition | None]
        | None = None,
    ) -> Self:
        """Add binary sensor definition."""
        if definition_fn is None:
            definition_fn = functools.partial(
                get_binary_sensor_default_definition, dpcode=key
            )

        quirk = BinarySensorQuirk(
            key=key,
            definition_fn=definition_fn,
        )
        return self._add_binary_sensor_quirk(quirk)

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

    def add_button(
        self,
        key: str,
        *,
        definition_fn: Callable[[CustomerDevice], ButtonDefinition | None]
        | None = None,
    ) -> Self:
        """Add button definition."""
        if definition_fn is None:
            definition_fn = functools.partial(
                get_button_default_definition, dpcode=key
            )

        quirk = ButtonQuirk(
            key=key,
            definition_fn=definition_fn,
        )
        return self._add_button_quirk(quirk)

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

    def add_camera(
        self,
        key: str,
        *,
        definition_fn: Callable[[CustomerDevice], CameraDefinition | None]
        | None = None,
    ) -> Self:
        """Add camera definition."""
        if definition_fn is None:
            definition_fn = get_camera_default_definition

        quirk = CameraQuirk(
            key=key,
            definition_fn=definition_fn,
        )
        return self._add_camera_quirk(quirk)

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

    def add_climate(
        self,
        key: str,
        *,
        definition_fn: Callable[
            [CustomerDevice, TuyaUnitOfTemperature],
            ClimateDefinition | None,
        ]
        | None = None,
    ) -> Self:
        """Add climate definition."""
        if definition_fn is None:
            definition_fn = get_climate_default_definition

        quirk = ClimateQuirk(
            key=key,
            definition_fn=definition_fn,
        )
        return self._add_climate_quirk(quirk)

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

    def add_cover(
        self,
        key: str,
        *,
        definition_fn: Callable[[CustomerDevice], CoverDefinition | None]
        | None = None,
    ) -> Self:
        """Add cover definition."""
        if definition_fn is None:
            definition_fn = functools.partial(
                get_cover_default_definition, instruction_dpcode=key
            )

        quirk = CoverQuirk(
            key=key,
            definition_fn=definition_fn,
        )
        return self._add_cover_quirk(quirk)

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

    def add_event(
        self,
        key: str,
        *,
        definition_fn: Callable[[CustomerDevice], EventDefinition | None]
        | None = None,
    ) -> Self:
        """Add event definition."""
        if definition_fn is None:
            definition_fn = functools.partial(
                get_event_default_definition, dpcode=key
            )

        quirk = EventQuirk(
            key=key,
            definition_fn=definition_fn,
        )
        return self._add_event_quirk(quirk)

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

    def add_fan(
        self,
        key: str,
        *,
        definition_fn: Callable[[CustomerDevice], FanDefinition | None]
        | None = None,
    ) -> Self:
        """Add fan definition."""
        if definition_fn is None:
            definition_fn = get_fan_default_definition

        quirk = FanQuirk(
            key=key,
            definition_fn=definition_fn,
        )
        return self._add_fan_quirk(quirk)

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

    def add_humidifier(
        self,
        key: str,
        *,
        definition_fn: Callable[
            [CustomerDevice],
            HumidifierDefinition | None,
        ]
        | None = None,
    ) -> Self:
        """Add humidifier definition."""
        if definition_fn is None:
            definition_fn = functools.partial(
                get_humidifier_default_definition, switch_dpcode=key
            )

        quirk = HumidifierQuirk(
            key=key,
            definition_fn=definition_fn,
        )
        return self._add_humidifier_quirk(quirk)

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

    def add_light(
        self,
        key: str,
        *,
        definition_fn: Callable[
            [CustomerDevice],
            LightDefinition | None,
        ]
        | None = None,
    ) -> Self:
        """Add light definition."""
        if definition_fn is None:
            definition_fn = functools.partial(
                get_light_default_definition, switch_dpcode=key
            )

        quirk = LightQuirk(
            key=key,
            definition_fn=definition_fn,
        )
        return self._add_light_quirk(quirk)

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

    def add_number(
        self,
        key: str,
        *,
        definition_fn: Callable[
            [CustomerDevice],
            NumberDefinition | None,
        ]
        | None = None,
    ) -> Self:
        """Add number definition."""
        if definition_fn is None:
            definition_fn = functools.partial(
                get_number_default_definition, dpcode=key
            )

        quirk = NumberQuirk(
            key=key,
            definition_fn=definition_fn,
        )
        return self._add_number_quirk(quirk)

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

    def add_select(
        self,
        key: str,
        *,
        definition_fn: Callable[
            [CustomerDevice],
            SelectDefinition | None,
        ]
        | None = None,
    ) -> Self:
        """Add select definition."""
        if definition_fn is None:
            definition_fn = functools.partial(
                get_select_default_definition, dpcode=key
            )

        quirk = SelectQuirk(
            key=key,
            definition_fn=definition_fn,
        )
        return self._add_select_quirk(quirk)

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

    def add_sensor(
        self,
        key: str,
        *,
        definition_fn: Callable[
            [CustomerDevice],
            SensorDefinition | None,
        ]
        | None = None,
    ) -> Self:
        """Add sensor definition."""
        if definition_fn is None:
            definition_fn = functools.partial(
                get_sensor_default_definition, dpcode=key
            )

        quirk = SensorQuirk(
            key=key,
            definition_fn=definition_fn,
        )
        return self._add_sensor_quirk(quirk)

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

    def add_siren(
        self,
        key: str,
        *,
        definition_fn: Callable[
            [CustomerDevice],
            SirenDefinition | None,
        ]
        | None = None,
    ) -> Self:
        """Add siren definition."""
        if definition_fn is None:
            definition_fn = functools.partial(
                get_siren_default_definition, dpcode=key
            )

        quirk = SirenQuirk(
            key=key,
            definition_fn=definition_fn,
        )
        return self._add_siren_quirk(quirk)

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

    def add_switch(
        self,
        key: str,
        *,
        definition_fn: Callable[
            [CustomerDevice],
            SwitchDefinition | None,
        ]
        | None = None,
    ) -> Self:
        """Add switch definition."""
        if definition_fn is None:
            definition_fn = functools.partial(
                get_switch_default_definition, dpcode=key
            )

        quirk = SwitchQuirk(
            key=key,
            definition_fn=definition_fn,
        )
        return self._add_switch_quirk(quirk)

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

    def add_vacuum(
        self,
        key: str,
        *,
        definition_fn: Callable[
            [CustomerDevice],
            VacuumDefinition | None,
        ]
        | None = None,
    ) -> Self:
        """Add vacuum definition."""
        if definition_fn is None:
            definition_fn = get_vacuum_default_definition

        quirk = VacuumQuirk(
            key=key,
            definition_fn=definition_fn,
        )
        return self._add_vacuum_quirk(quirk)

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

    def add_valve(
        self,
        key: str,
        *,
        definition_fn: Callable[
            [CustomerDevice],
            ValveDefinition | None,
        ]
        | None = None,
    ) -> Self:
        """Add valve definition."""
        if definition_fn is None:
            definition_fn = functools.partial(
                get_valve_default_definition, dpcode=key
            )

        quirk = ValveQuirk(
            key=key,
            definition_fn=definition_fn,
        )
        return self._add_valve_quirk(quirk)
