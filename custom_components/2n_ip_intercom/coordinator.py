"""DataUpdateCoordinator for 2N IP Intercom integration."""
import asyncio
from datetime import timedelta
import logging

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD

from .const import DOMAIN, API_SYSTEM_STATUS, API_SWITCH_CAPS, CONF_NAME

_LOGGER = logging.getLogger(__name__)

class TwoNIntercomDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the 2N IP Intercom."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize coordinator."""
        self.hass = hass
        self.host = config[CONF_HOST]
        self.port = config.get(CONF_PORT, 80)
        self.username = config.get(CONF_USERNAME)
        self.password = config.get(CONF_PASSWORD)
        self.device_name = config.get(CONF_NAME, f"2N IP Intercom ({self.host})")
        self.base_url = f"http://{self.host}:{self.port}"

        # Store ports info
        self.data = {
            "doorState": "locked",
            "switch1State": "off",
            "ports": []
        }

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )

    async def async_shutdown(self) -> None:
        """Shutdown coordinator."""
        pass  # No persistent session to close here

    async def _async_update_data(self):
        """Fetch data from the 2N IP Intercom API."""
        try:
            auth = aiohttp.BasicAuth(self.username, self.password) \
                if self.username and self.password else None

            async with aiohttp.ClientSession() as session:
                # Fetch system status
                async with session.get(
                    f"{self.base_url}{API_SYSTEM_STATUS}",
                    auth=auth,
                    timeout=10,
                    ssl=False,
                ) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"Failed to fetch system status, HTTP {resp.status}")
                    system_data = await resp.json()

                # Update door state
                self.data["doorState"] = "unlocked" if system_data.get("doorState") == "unlocked" else "locked"

                # Fetch switch states and capabilities
                async with session.get(
                    f"{self.base_url}{API_SWITCH_CAPS}",
                    auth=auth,
                    timeout=10,
                    ssl=False,
                ) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"Failed to fetch switch capabilities, HTTP {resp.status}")
                    caps_data = await resp.json()

                ports = []
                for switch_info in caps_data.get("switches", []):
                    port = {
                        "id": switch_info.get("id"),
                        "name": switch_info.get("name"),
                        "mode": switch_info.get("mode"),  # bistable or monostable
                        "state": "on" if switch_info.get("state") == "on" else "off"
                    }
                    # Update main switch states dynamically
                    self.data[f"switch{port['id']}State"] = port["state"]
                    ports.append(port)
                self.data["ports"] = ports

                return self.data

        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise UpdateFailed(f"Error fetching data from {self.host}: {err}") from err

    async def async_config_entry_first_refresh(self):
        """First refresh for coordinator."""
        await super().async_refresh()

