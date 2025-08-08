from datetime import timedelta
import logging
import aiohttp

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = TwoNIntercomDataUpdateCoordinator(hass, entry.data)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([TwoNIntercomSensor(coordinator, entry.data.get("host"))], True)


class TwoNIntercomDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config):
        self.host = config[CONF_HOST]
        self.port = config.get(CONF_PORT, 80)
        self.username = config.get(CONF_USERNAME)
        self.password = config.get(CONF_PASSWORD)
        super().__init__(
            hass,
            _LOGGER,
            name="2N IP Intercom",
            update_interval=timedelta(seconds=30)
        )

    async def _async_update_data(self):
        url = f"http://{self.host}:{self.port}/status"  # Adjust endpoint as needed.
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, auth=aiohttp.BasicAuth(self.username, self.password)) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Error fetching data: Status code {response.status}")
                    data = await response.json()
                    return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with 2N IP Intercom: {err}") from err


class TwoNIntercomSensor(SensorEntity):
    def __init__(self, coordinator, name):
        self.coordinator = coordinator
        self._attr_name = f"2N IP Intercom {name}"
        self._state = None

    @property
    def state(self):
        data = self.coordinator.data
        if data:
            # Adjust this based on the proper key in the returned JSON
            return data.get("call_status")
        return None

    async def async_update(self):
        await self.coordinator.async_request_refresh()
