"""Yardstick select: which saved plan 'start mowing' runs."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import YardstickConfigEntry
from .entity import YardstickEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: YardstickConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        YardstickPlanSelect(coordinator, robot) for robot in coordinator.robots())


class YardstickPlanSelect(YardstickEntity, SelectEntity):
    """The saved plan the mower's Start runs. Options come from a live read of
    the robot, so they fill in once it is awake."""

    _attr_name = "Plan"
    _attr_icon = "mdi:map-marker-path"

    def __init__(self, coordinator, robot) -> None:
        super().__init__(coordinator, robot)
        self._attr_unique_id = f"{self._serial}_plan"
        self._names_to_id: dict[str, str] = {}
        self._attr_options: list[str] = []
        self._attr_current_option: str | None = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        await self._refresh_plans()

    async def _refresh_plans(self) -> None:
        plans = await self.coordinator.fetch_plans(self._serial)
        self._names_to_id = {}
        options: list[str] = []
        for plan in plans:
            name = plan.get("name") or f"Plan {plan.get('id')}"
            self._names_to_id[name] = plan["id"]
            options.append(name)
        self._attr_options = options
        current = self.coordinator.selected_plan.get(self._serial)
        chosen = next((n for n, i in self._names_to_id.items() if i == current), None)
        if chosen is None and options:
            chosen = options[0]
            self.coordinator.selected_plan[self._serial] = self._names_to_id[chosen]
        self._attr_current_option = chosen
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        plan_id = self._names_to_id.get(option)
        if plan_id is None:
            # Options may be stale if plans changed on the robot; refresh once.
            await self._refresh_plans()
            plan_id = self._names_to_id.get(option)
        if plan_id is not None:
            self.coordinator.selected_plan[self._serial] = plan_id
            self._attr_current_option = option
            self.async_write_ha_state()
