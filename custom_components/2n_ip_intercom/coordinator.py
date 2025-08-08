"""DataUpdateCoordinator for 2N IP Intercom integration."""
from datetime import timedelta
import logging

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
)

from .const import (
    DOMAIN,
    API_SYSTEM_STATUS,
)

_LOGGER = logging.getLogger(__name__)

class TwoNIntercomDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the 2N IP Intercom."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize."""
        self.host = config[CONF_HOST]
        self.port = config.get(CONF_PORT)
        self.username = config.get(CONF_USERNAME)
        self.password = config.get(CONF_PASSWORD)
        self.base_url = f"http://{self.host}:{self.port}"

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self):
        """Update data via API."""
        try:
            async with aiohttp.ClientSession() as session:
                auth = None
                if self.username and self.password:
                    auth = aiohttp.BasicAuth(self.username, self.password)

                async with session.get(
                    f"{self.base_url}{API_SYSTEM_STATUS}",
                    auth=auth,
                ) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(
                            f"Error communicating with API: {resp.status}"
                        )
                    data = await resp.json()
                    return data

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def async_validate_input(self) -> bool:
        """Validate the user input allows us to connect."""
        try:
            async with aiohttp.ClientSession() as session:
                auth = None
                if self.username and self.password:
                    auth = aiohttp.BasicAuth(self.username, self.password)

                async with session.get(
                    f"{self.base_url}{API_SYSTEM_STATUS}",
                    auth=auth,
                ) as resp:
                    return resp.status == 200

        except aiohttp.ClientError:
            return False
