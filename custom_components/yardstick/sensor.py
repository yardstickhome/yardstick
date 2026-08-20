"""Yardstick sensors: the readings a Yarbo owner watches."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import YardstickConfigEntry
from .entity import YardstickEntity

SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="battery",
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(key="activity", name="Activity", icon="mdi:robot-mower"),
    SensorEntityDescription(key="rtk", name="RTK signal", icon="mdi:crosshairs-gps"),
    SensorEntityDescription(
        key="error_code", name="Fault code", icon="mdi:alert-circle-outline"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: YardstickConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        YardstickSensor(coordinator, robot, description)
        for robot in coordinator.robots()
        for description in SENSORS
    )


class YardstickSensor(YardstickEntity, SensorEntity):
    def __init__(self, coordinator, robot, description: SensorEntityDescription) -> None:
        super().__init__(coordinator, robot)
        self.entity_description = description
        self._attr_unique_id = f"{self._serial}_{description.key}"

    @property
    def native_value(self):
        return self._robot.get(self.entity_description.key)
