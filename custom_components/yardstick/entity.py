"""Shared base for Yardstick entities — one Home Assistant device per robot."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import YardstickCoordinator


class YardstickEntity(CoordinatorEntity[YardstickCoordinator]):
    """An entity of one robot, grouped under that robot's device.

    The device is branded Yardstick — manufacturer, software version, and a
    'Visit device' link back to the Yardstick page — because Yardstick is what
    brings it into Home Assistant.
    """

    _attr_has_entity_name = True

    def __init__(self, coordinator: YardstickCoordinator, robot: dict) -> None:
        super().__init__(coordinator)
        self._serial: str = robot["serial"]
        version = (coordinator.data or {}).get("yardstick", {}).get("version")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._serial)},
            name=robot.get("name") or "Yarbo",
            manufacturer=MANUFACTURER,
            model="Yarbo",
            sw_version=f"Yardstick {version}" if version else None,
            serial_number=self._serial,
            configuration_url=coordinator.base_url,
        )

    @property
    def _robot(self) -> dict:
        return self.coordinator.robot(self._serial) or {}

    @property
    def available(self) -> bool:
        # The coordinator being up is not enough — the robot must still be in
        # the payload (it could have been unconfigured in Yardstick).
        return super().available and self.coordinator.robot(self._serial) is not None
