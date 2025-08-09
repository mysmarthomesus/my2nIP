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
        self.port = config.get(CONF_PORT, 80)
        self.username = config.get(CONF_USERNAME)
        self.password = config.get(CONF_PASSWORD)
        self.base_url = f"http://{self.host}:{self.port}"
        self._session = aiohttp.ClientSession()

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        
    async def async_close(self) -> None:
        """Close the session."""
        if self._session:
            await self._session.close()

    async def _async_update_data(self):
        """Update data via API."""
        try:
            auth = None
            if self.username and self.password:
                auth = aiohttp.BasicAuth(self.username, self.password)
            
            headers = {
                "Accept": "application/json",
                "Connection": "keep-alive"
            }

            async with self._session.get(
                f"{self.base_url}{API_SYSTEM_STATUS}",
                auth=auth,
                headers=headers,
                timeout=10,
                ssl=False  # Most 2N devices use HTTP
            ) as resp:
                if resp.status == 401:
                    raise UpdateFailed("Invalid authentication credentials")
                if resp.status != 200:
                    raise UpdateFailed(
                        f"Error communicating with API: Status {resp.status}"
                    )
                try:
                    data = await resp.json()
                    return data
                except ValueError as err:
                    raise UpdateFailed(f"Invalid response from API: {err}") from err

        except aiohttp.ClientConnectorError as err:
            raise UpdateFailed(f"Cannot connect to {self.host}:{self.port} - {err}") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except asyncio.TimeoutError:
            raise UpdateFailed(f"Timeout connecting to {self.host}:{self.port}") from None

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
