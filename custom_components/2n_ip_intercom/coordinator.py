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
    CONF_NAME,
    CONF_SWITCH_MODE,
    DEFAULT_SWITCH_MODE,
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
        self.device_name = config.get(CONF_NAME, f"2N IP Intercom ({self.host})")
        self.switch_mode = config.get(CONF_SWITCH_MODE, DEFAULT_SWITCH_MODE)
        self.base_url = f"http://{self.host}:{self.port}"
        self._session = None
        self._switch_states = {}  # Track switch states for toggle mode

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def _get_session(self):
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=10, connect=5)
            connector = aiohttp.TCPConnector(
                limit=10,
                limit_per_host=5,
                enable_cleanup_closed=True,
                force_close=True,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
            )
        return self._session

    async def _async_update_data(self):
        """Update data via API."""
        try:
            session = await self._get_session()
            auth = None
            if self.username and self.password:
                auth = aiohttp.BasicAuth(self.username, self.password)
            
            headers = {
                "Accept": "application/json",
                "Connection": "close"  # Avoid keeping connections open
            }

            _LOGGER.debug("Attempting to connect to %s:%s", self.host, self.port)

            url = f"{self.base_url}{API_SYSTEM_STATUS}"
            _LOGGER.debug("Requesting URL: %s", url)
            
            async with session.get(
                url,
                auth=auth,
                headers=headers,
                ssl=False,  # Most 2N devices use HTTP
                raise_for_status=False
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
                
                try:
                    data = await resp.json()
                    _LOGGER.debug("Parsed JSON data: %s", data)
                    return data
                except ValueError as err:
                    # If JSON parsing fails, return minimal data
                    _LOGGER.warning("Could not parse JSON response, using fallback data: %s", err)
                    return {"status": "unknown", "timestamp": "unknown"}
                        
        except aiohttp.ClientConnectorError as err:
            _LOGGER.error("Connection failed to %s:%s - %s", self.host, self.port, err)
            raise UpdateFailed(f"Connection failed to {self.host}:{self.port}") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("HTTP error communicating with %s:%s - %s", self.host, self.port, err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout connecting to %s:%s", self.host, self.port)
            raise UpdateFailed(f"Timeout connecting to {self.host}:{self.port}") from None
        except Exception as err:
            _LOGGER.error("Unexpected error connecting to %s:%s - %s", self.host, self.port, err)
            raise UpdateFailed(f"Unexpected error: {err}") from err

    async def async_validate_input(self) -> bool:
        """Validate the user input allows us to connect."""
        try:
            session = await self._get_session()
            auth = None
            if self.username and self.password:
                auth = aiohttp.BasicAuth(self.username, self.password)

            async with session.get(
                f"{self.base_url}{API_SYSTEM_STATUS}",
                auth=auth,
                ssl=False,
                raise_for_status=False
            ) as resp:
                return resp.status == 200

        except Exception as err:
            _LOGGER.error("Validation failed for %s:%s - %s", self.host, self.port, err)
            return False
