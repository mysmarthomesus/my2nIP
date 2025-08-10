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
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
)

_LOGGER = logging.getLogger(__name__)

class TwoNIntercomDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the 2N IP Intercom."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize."""
        self.host = config[CONF_HOST]
        self.port = config.get(CONF_PORT, 80)
        self.username = config.get(CONF_USERNAME, DEFAULT_USERNAME)
        self.password = config.get(CONF_PASSWORD, DEFAULT_PASSWORD)
        self.base_url = f"http://{self.host}:{self.port}"
        self._session = None
        self.device_info = None
        self.mac_address = None

        # Debug log credentials being used
        _LOGGER.debug(
            "Initializing coordinator with host=%s, port=%s, username=%s",
            self.host,
            self.port,
            self.username,
        )

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
            auth = aiohttp.BasicAuth(
                login=self.username or DEFAULT_USERNAME,
                password=self.password or DEFAULT_PASSWORD,
            )
            
            headers = {
                "Accept": "application/json",
                "Connection": "keep-alive"
            }

            _LOGGER.debug(
                "Making request to %s with username %s",
                f"{self.base_url}{API_SYSTEM_STATUS}",
                self.username or DEFAULT_USERNAME,
            )

            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}{API_SYSTEM_STATUS}"
                _LOGGER.debug("Requesting URL: %s", url)
                
                async with session.get(
                    url,
                    auth=auth,
                    headers=headers,
                    ssl=False,
                    timeout=10,
                ) as response:
                    _LOGGER.debug("Response status: %s", response.status)
                    
                    if response.status == 401:
                        raise UpdateFailed(f"Authentication failed. Please check username ({self.username or DEFAULT_USERNAME}) and password")
                        
                    if response.status != 200:
                        content = await response.text()
                        _LOGGER.debug("Error response content: %s", content)
                        raise UpdateFailed(f"Error communicating with API: {response.status}")

                    try:
                        data = await response.json()
                        _LOGGER.debug("Parsed JSON data: %s", data)
                        
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
                    except ValueError as err:
                        raise UpdateFailed(f"Invalid JSON response from API: {err}") from err

        except aiohttp.ClientConnectorError as err:
            raise UpdateFailed(f"Cannot connect to {self.host}:{self.port} - {err}") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except asyncio.TimeoutError:
            raise UpdateFailed(f"Timeout connecting to {self.host}:{self.port}") from None

    async def async_validate_input(self) -> bool:
        """Validate the user input allows us to connect."""
        try:
            auth = aiohttp.BasicAuth(
                login=self.username or DEFAULT_USERNAME,
                password=self.password or DEFAULT_PASSWORD,
            )

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}{API_SYSTEM_STATUS}",
                    auth=auth,
                    ssl=False,
                    timeout=10,
                ) as response:
                    if response.status == 401:
                        _LOGGER.error(
                            "Authentication failed during validation with username: %s",
                            self.username or DEFAULT_USERNAME,
                        )
                        return False
                        
                    return response.status == 200

        except aiohttp.ClientError as err:
            _LOGGER.error("Error validating connection: %s", err)
            return False
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout validating connection to %s:%s", self.host, self.port)
            return False
