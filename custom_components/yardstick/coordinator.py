"""Fetches robot state from a Yardstick install on the local network."""

from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=15)


class YardstickCoordinator(DataUpdateCoordinator[dict]):
    """Polls Yardstick's local /api/ha endpoint.

    Yardstick reads the robot on the LAN and exposes a small, stable JSON — this
    integration never touches the robot or the cloud directly, only Yardstick.
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry,
                 host: str, port: int) -> None:
        super().__init__(
            hass, _LOGGER, name="Yardstick",
            update_interval=SCAN_INTERVAL, config_entry=entry)
        self.base_url = f"http://{host}:{port}/"
        self._url = f"{self.base_url}api/ha"
        self._session = async_get_clientsession(hass)
        # Which saved plan "start mowing" runs, chosen with the Plan select.
        # Per robot serial; defaults to the first plan when unset.
        self.selected_plan: dict[str, str] = {}

    async def _async_update_data(self) -> dict:
        try:
            async with self._session.get(
                self._url, timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                if response.status == 402:
                    # Yardstick answers the paywall when the licence has lapsed.
                    raise ConfigEntryAuthFailed(
                        "This Yardstick needs an active licence to feed Home "
                        "Assistant.")
                response.raise_for_status()
                return await response.json()
        except ConfigEntryAuthFailed:
            raise
        except Exception as err:  # noqa: BLE001 - surface any reach problem as one
            raise UpdateFailed(f"Could not reach Yardstick: {err}") from err

    def robots(self) -> list[dict]:
        return (self.data or {}).get("robots", [])

    def robot(self, serial: str) -> dict | None:
        return next((r for r in self.robots() if r.get("serial") == serial), None)

    async def command(self, action: str, serial: str, **params) -> dict:
        """Send a control action to Yardstick, which relays it to the robot.

        Yardstick answers 402 when the licence has lapsed and 404 when the
        owner has manual control switched off; both are surfaced as a plain
        message rather than a stack trace.
        """
        body = {"serial": serial, **params}
        try:
            async with self._session.post(
                f"{self.base_url}api/ha/control/{action}", json=body,
                timeout=aiohttp.ClientTimeout(total=20)
            ) as response:
                if response.status == 402:
                    raise HomeAssistantError(
                        "This Yardstick needs an active licence.")
                if response.status == 404:
                    raise HomeAssistantError(
                        "Manual control is switched off in Yardstick's settings.")
                response.raise_for_status()
                data = await response.json()
        except HomeAssistantError:
            raise
        except Exception as err:  # noqa: BLE001 - one message for any reach problem
            raise HomeAssistantError(f"Could not reach Yardstick: {err}") from err
        if not data.get("ok"):
            raise HomeAssistantError(
                data.get("error") or "Yardstick refused the command.")
        # Reflect the new state promptly rather than waiting for the next poll.
        await self.async_request_refresh()
        return data

    async def fetch_plans(self, serial: str) -> list[dict]:
        """The robot's saved plans, for the Plan select. A live read, so it is
        fetched on demand rather than on the poll; an empty list when the robot
        is asleep is normal, not an error."""
        try:
            async with self._session.get(
                f"{self.base_url}api/ha/plans", params={"serial": serial},
                timeout=aiohttp.ClientTimeout(total=25)
            ) as response:
                response.raise_for_status()
                data = await response.json()
        except Exception:  # noqa: BLE001 - a sleeping robot is not an error here
            return []
        return [p for p in data.get("plans", []) if p.get("id") is not None]
