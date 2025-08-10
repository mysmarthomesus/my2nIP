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
        self._session = None
        self.device_info = None
        self.mac_address = None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        
        # Initialize device info
        self._init_device_info()

    def _init_device_info(self):
        """Initialize device info."""
        if not self.device_info:
            self.device_info = {
                "model": "2N IP Intercom",
                "manufacturer": "2N",
                "firmwareVersion": "Unknown"
            }

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        if self._session and not self._session.closed:
            await self._session.close()
            
    async def _async_update_data(self) -> dict:
        """Update data via library."""
        try:
            if not self._session:
                self._session = aiohttp.ClientSession()

            auth = None
            if self.username and self.password:
                auth = aiohttp.BasicAuth(self.username, self.password)

            async with self._session.get(
                f"{self.base_url}{API_SYSTEM_STATUS}",
                auth=auth,
                ssl=False,
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Update device info
                    if not self.device_info:
                        self.device_info = {}
                    
                    self.device_info.update({
                        "model": data.get("model", "2N IP Intercom"),
                        "manufacturer": "2N",
                        "firmwareVersion": data.get("firmwareVersion", "Unknown"),
                        "serialNumber": data.get("serialNumber"),
                        "macAddress": data.get("macAddress"),
                    })
                    
                    if data.get("macAddress"):
                        self.mac_address = data["macAddress"].replace(":", "")
                    
                    return data
                    
                raise UpdateFailed(f"Error communicating with API: {response.status}")
                
        except asyncio.TimeoutError as exception:
            raise UpdateFailed("Timeout communicating with API") from exception
            
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with API: {exception}") from exception

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

            _LOGGER.debug("Attempting to connect to %s:%s", self.host, self.port)

            try:
                async with aiohttp.ClientSession() as session:
                    url = f"{self.base_url}{API_SYSTEM_STATUS}"
                    _LOGGER.debug("Requesting URL: %s", url)
                    
                    async with session.get(
                        url,
                        auth=auth,
                        headers=headers,
                        timeout=10,
                        ssl=False  # Most 2N devices use HTTP
                    ) as resp:
                        _LOGGER.debug("Response status: %s", resp.status)
                        
                        if resp.status == 401:
                            raise UpdateFailed("Invalid authentication credentials")
                        if resp.status != 200:
                            content = await resp.text()
                            _LOGGER.debug("Error response content: %s", content)
                            raise UpdateFailed(
                                f"Error communicating with API: Status {resp.status}"
                            )
                        
                        content = await resp.text()
                        _LOGGER.debug("Response content: %s", content)
                        
                        try:
                            data = await resp.json()
                            _LOGGER.debug("Parsed JSON data: %s", data)
                            return data
                        except ValueError as err:
                            raise UpdateFailed(f"Invalid JSON response from API: {err}") from err
                            
            except aiohttp.ClientConnectorError as err:
                raise UpdateFailed(f"Connection failed to {self.host}:{self.port} - {err}") from err
            except asyncio.TimeoutError:
                raise UpdateFailed(f"Timeout connecting to {self.host}:{self.port}") from None

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
