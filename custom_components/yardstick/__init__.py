"""The Yardstick integration: your Yarbo in Home Assistant, through Yardstick.

Yardstick runs on your own network and this integration reads Yardstick, so the
hop Home Assistant makes is local. Yardstick itself reaches the robot through the
owner's Yarbo account: a Yarbo firmware update in September 2026 closed the
robot's local broker, and with it the "no account, no cloud" this used to say.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .coordinator import YardstickCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.LAWN_MOWER,
    Platform.BUTTON,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SELECT,
]

type YardstickConfigEntry = ConfigEntry[YardstickCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: YardstickConfigEntry) -> bool:
    coordinator = YardstickCoordinator(
        hass, entry, entry.data[CONF_HOST], entry.data[CONF_PORT])
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: YardstickConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
