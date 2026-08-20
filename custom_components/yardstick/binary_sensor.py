"""Yardstick binary sensors: online and charging."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import YardstickConfigEntry
from .entity import YardstickEntity

BINARY_SENSORS: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="online", name="Online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY),
    BinarySensorEntityDescription(
        key="charging", name="Charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: YardstickConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        YardstickBinarySensor(coordinator, robot, description)
        for robot in coordinator.robots()
        for description in BINARY_SENSORS
    )


class YardstickBinarySensor(YardstickEntity, BinarySensorEntity):
    def __init__(self, coordinator, robot,
                 description: BinarySensorEntityDescription) -> None:
        super().__init__(coordinator, robot)
        self.entity_description = description
        self._attr_unique_id = f"{self._serial}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        value = self._robot.get(self.entity_description.key)
        return None if value is None else bool(value)
