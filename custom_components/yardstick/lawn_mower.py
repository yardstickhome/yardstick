"""Yardstick lawn mower: start a plan, pause, and send it home."""

from __future__ import annotations

from homeassistant.components.lawn_mower import (
    LawnMowerActivity,
    LawnMowerEntity,
    LawnMowerEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import YardstickConfigEntry
from .entity import YardstickEntity


def _activity(robot: dict) -> LawnMowerActivity | None:
    """Map Yardstick's activity string onto Home Assistant's mower states.

    The payload does not distinguish a paused job from idle-on-dock, so both
    read as docked; the Pause button and the job's own state still work.
    """
    if not robot.get("online"):
        return None
    error = robot.get("error_code")
    if error not in (None, "", "OK"):
        return LawnMowerActivity.ERROR
    activity = robot.get("activity") or ""
    if activity == "Working":
        return LawnMowerActivity.MOWING
    if activity == "Returning to dock":
        return LawnMowerActivity.RETURNING
    if activity in ("Charging", "Standby"):
        return LawnMowerActivity.DOCKED
    return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: YardstickConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        YardstickMower(coordinator, robot) for robot in coordinator.robots())


class YardstickMower(YardstickEntity, LawnMowerEntity):
    # The mower is the robot's headline entity, so it carries the device name.
    _attr_name = None
    _attr_supported_features = (
        LawnMowerEntityFeature.START_MOWING
        | LawnMowerEntityFeature.PAUSE
        | LawnMowerEntityFeature.DOCK
    )

    def __init__(self, coordinator, robot) -> None:
        super().__init__(coordinator, robot)
        self._attr_unique_id = f"{self._serial}_mower"

    @property
    def activity(self) -> LawnMowerActivity | None:
        return _activity(self._robot)

    async def async_start_mowing(self) -> None:
        plan_id = self.coordinator.selected_plan.get(self._serial)
        if plan_id is None:
            plans = await self.coordinator.fetch_plans(self._serial)
            if not plans:
                raise HomeAssistantError(
                    "No saved plans found on the robot. Make one in the Yarbo "
                    "app first, or pick one with the Plan selector.")
            plan_id = plans[0]["id"]
        await self.coordinator.command("start-plan", self._serial, planId=plan_id)

    async def async_pause(self) -> None:
        await self.coordinator.command("pause", self._serial)

    async def async_dock(self) -> None:
        await self.coordinator.command("dock", self._serial)
