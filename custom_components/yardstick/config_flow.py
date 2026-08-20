"""Config flow — add Yardstick by hand, or accept it when it is auto-discovered."""

from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .const import DEFAULT_PORT, DOMAIN


class _LicenceRequired(Exception):
    """Yardstick answered the paywall — the licence has lapsed."""


async def _validate(hass, host: str, port: int) -> dict:
    session = async_get_clientsession(hass)
    async with session.get(
        f"http://{host}:{port}/api/ha", timeout=aiohttp.ClientTimeout(total=10)
    ) as response:
        if response.status == 402:
            raise _LicenceRequired
        response.raise_for_status()
        return await response.json()


class YardstickConfigFlow(ConfigFlow, domain=DOMAIN):
    """Set up a Yardstick install."""

    VERSION = 1

    def __init__(self) -> None:
        self._host: str | None = None
        self._port: int = DEFAULT_PORT

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            try:
                await _validate(self.hass, host, port)
            except _LicenceRequired:
                errors["base"] = "licence"
            except (aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"{host}:{port}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Yardstick",
                    data={CONF_HOST: host, CONF_PORT: port})
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
            }),
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        host = discovery_info.host
        port = discovery_info.port or DEFAULT_PORT
        await self.async_set_unique_id(f"{host}:{port}")
        self._abort_if_unique_id_configured(
            updates={CONF_HOST: host, CONF_PORT: port})
        self._host = host
        self._port = port
        self.context["title_placeholders"] = {"host": host}
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await _validate(self.hass, self._host, self._port)
            except _LicenceRequired:
                errors["base"] = "licence"
            except (aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title="Yardstick",
                    data={CONF_HOST: self._host, CONF_PORT: self._port})
        return self.async_show_form(
            step_id="zeroconf_confirm",
            errors=errors,
            description_placeholders={"host": self._host or ""},
        )
