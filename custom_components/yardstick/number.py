"""Yardstick numbers: attachment settings (blower speed, heights, chute)."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import YardstickConfigEntry
from .entity import YardstickEntity


@dataclass(frozen=True, kw_only=True)
class YardstickNumberDescription(NumberEntityDescription):
    """A number, its control action, the body key it sends, and where its live
    value is reported (under the robot's ``control`` block), if at all."""

    action: str
    param_key: str = "value"
    state_key: str | None = None


NUMBERS: tuple[YardstickNumberDescription, ...] = (
    YardstickNumberDescription(
        key="blower", name="Blower speed", icon="mdi:weather-windy",
        action="blower", param_key="vel", state_key="blower",
        native_min_value=0, native_max_value=2000, native_step=50,
        mode=NumberMode.SLIDER),
    YardstickNumberDescription(
        key="blade_height", name="Blade height", icon="mdi:arrow-expand-vertical",
        action="blade-height", native_min_value=0, native_max_value=100,
        native_step=1, mode=NumberMode.BOX),
    YardstickNumberDescription(
        key="head_lift", name="Head lift", icon="mdi:arrow-up-down",
        action="head-lift", native_min_value=0, native_max_value=64,
        native_step=1, mode=NumberMode.SLIDER),
    YardstickNumberDescription(
        key="chute_angle", name="Chute angle", icon="mdi:rotate-3d-variant",
        action="chute-angle", native_min_value=-90, native_max_value=90,
        native_step=5, mode=NumberMode.SLIDER),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: YardstickConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        YardstickNumber(coordinator, robot, description)
        for robot in coordinator.robots()
        for description in NUMBERS
    )


class YardstickNumber(YardstickEntity, NumberEntity):
    entity_description: YardstickNumberDescription

    def __init__(self, coordinator, robot, description: YardstickNumberDescription) -> None:
        super().__init__(coordinator, robot)
        self.entity_description = description
        self._attr_unique_id = f"{self._serial}_{description.key}"
        self._value: float | None = None

    @property
    def native_value(self) -> float | None:
        key = self.entity_description.state_key
        if key:
            value = (self._robot.get("control") or {}).get(key)
            return None if value is None else float(value)
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.command(
            self.entity_description.action, self._serial,
            **{self.entity_description.param_key: value})
        self._value = value
        self.async_write_ha_state()
