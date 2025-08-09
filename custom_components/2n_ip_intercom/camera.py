"""Support for 2N IP Intercom camera."""
from __future__ import annotations

import aiohttp
import logging

from homeassistant.components.camera import (
    Camera,
    CameraEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up 2N IP Intercom camera."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    cameras = [
        TwoNCamera(coordinator, 1),  # Main camera
    ]
    
    async_add_entities(cameras, True)

class TwoNCamera(Camera):
    """Implementation of a 2N IP Intercom camera."""

    def __init__(self, coordinator, camera_id):
        """Initialize the camera."""
        super().__init__()
        self.coordinator = coordinator
        self.camera_id = camera_id
        self._attr_name = f"2N Camera {camera_id}"
        self._attr_unique_id = f"{coordinator.host}_camera_{camera_id}"
        self._stream_source = None
        self._last_image = None
        self._attr_supported_features = CameraEntityFeature.STREAM
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": "2N IP Intercom",
            "manufacturer": "2N",
            "model": "IP Intercom",
        }

    async def stream_source(self) -> str | None:
        """Return the RTSP stream source."""
        auth_string = ""
        if self.coordinator.username and self.coordinator.password:
            auth_string = f"{self.coordinator.username}:{self.coordinator.password}@"
            
        return f"rtsp://{auth_string}{self.coordinator.host}:{self.coordinator.port}/live/ch{self.camera_id}"

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image from the camera."""
        try:
            websession = async_get_clientsession(self.hass)
            auth = None
            if self.coordinator.username and self.coordinator.password:
                auth = aiohttp.BasicAuth(self.coordinator.username, self.coordinator.password)

            url = f"http://{self.coordinator.host}/api/camera/{self.camera_id}/snapshot"
            
            async with websession.get(url, auth=auth) as response:
                if response.status == 200:
                    return await response.read()
                
                _LOGGER.error(
                    "Error getting camera image from %s: %s",
                    self.coordinator.host,
                    response.status,
                )
                
        except Exception as err:
            _LOGGER.error("Error getting camera image: %s", err)
            
        return None
