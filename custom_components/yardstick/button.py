"""Yardstick buttons: one-press actions on the robot."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import YardstickConfigEntry
from .entity import YardstickEntity


@dataclass(frozen=True, kw_only=True)
class YardstickButtonDescription(ButtonEntityDescription):
    """A button and the control action it sends."""

    action: str


BUTTONS: tuple[YardstickButtonDescription, ...] = (
    YardstickButtonDescription(
        key="dock", name="Send home", icon="mdi:home-import-outline", action="dock"),
    YardstickButtonDescription(
        key="pause", name="Pause", icon="mdi:pause", action="pause"),
    YardstickButtonDescription(
        key="resume", name="Resume", icon="mdi:play", action="resume"),
    YardstickButtonDescription(
        key="find", name="Find (sound)", icon="mdi:bullhorn", action="buzzer"),
    YardstickButtonDescription(
        key="stop", name="Stop", icon="mdi:stop", action="halt"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: YardstickConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        YardstickButton(coordinator, robot, description)
        for robot in coordinator.robots()
        for description in BUTTONS
    )


class YardstickButton(YardstickEntity, ButtonEntity):
    entity_description: YardstickButtonDescription

    def __init__(self, coordinator, robot, description: YardstickButtonDescription) -> None:
        super().__init__(coordinator, robot)
        self.entity_description = description
        self._attr_unique_id = f"{self._serial}_{description.key}"

    async def async_press(self) -> None:
        await self.coordinator.command(self.entity_description.action, self._serial)
