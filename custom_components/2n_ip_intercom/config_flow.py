"""Config flow for 2N IP Intercom integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
)
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    DEFAULT_PORT,
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
    CONF_NAME,
)
from .coordinator import TwoNIntercomDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for 2N IP Intercom."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                coordinator = TwoNIntercomDataUpdateCoordinator(
                    self.hass,
                    {
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_PORT: user_input.get(CONF_PORT, DEFAULT_PORT),
                        CONF_USERNAME: user_input.get(CONF_USERNAME, DEFAULT_USERNAME),
                        CONF_PASSWORD: user_input.get(CONF_PASSWORD, DEFAULT_PASSWORD),
                    },
                )
                await coordinator.async_validate_input()

                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, user_input[CONF_HOST]),
                    data=user_input,
                )
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_NAME): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Optional(CONF_USERNAME, default=DEFAULT_USERNAME): str,
                    vol.Optional(CONF_PASSWORD, default=DEFAULT_PASSWORD): str,
                }
            ),
            errors=errors,
        )
