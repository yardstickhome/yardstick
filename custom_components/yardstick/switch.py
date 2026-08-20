"""Yardstick switches: blades, lights, camera."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import YardstickConfigEntry
from .entity import YardstickEntity


@dataclass(frozen=True, kw_only=True)
class YardstickSwitchDescription(SwitchEntityDescription):
    """A switch, its control action, and where its live state is reported.

    ``state_key`` names a field under the robot's ``control`` block, present
    once a control session is open. When there is none (lights, camera, which
    the robot does not report back), the switch is assumed-state: it shows what
    was last commanded.
    """

    action: str
    state_key: str | None = None


SWITCHES: tuple[YardstickSwitchDescription, ...] = (
    YardstickSwitchDescription(
        key="blades", name="Blades", icon="mdi:fan",
        action="blades", state_key="blades"),
    YardstickSwitchDescription(
        key="lights", name="Lights", icon="mdi:car-light-high", action="lights"),
    YardstickSwitchDescription(
        key="camera", name="Camera", icon="mdi:cctv", action="camera"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: YardstickConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        YardstickSwitch(coordinator, robot, description)
        for robot in coordinator.robots()
        for description in SWITCHES
    )


class YardstickSwitch(YardstickEntity, SwitchEntity):
    entity_description: YardstickSwitchDescription

    def __init__(self, coordinator, robot, description: YardstickSwitchDescription) -> None:
        super().__init__(coordinator, robot)
        self.entity_description = description
        self._attr_unique_id = f"{self._serial}_{description.key}"
        self._assumed = False
        if description.state_key is None:
            self._attr_assumed_state = True

    @property
    def is_on(self) -> bool:
        key = self.entity_description.state_key
        if key:
            return bool((self._robot.get("control") or {}).get(key))
        return self._assumed

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.command(
            self.entity_description.action, self._serial, on=True)
        self._assumed = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.command(
            self.entity_description.action, self._serial, on=False)
        self._assumed = False
        self.async_write_ha_state()
