"""Support for 2N IP Intercom camera."""
from __future__ import annotations

import asyncio
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

from .const import DOMAIN, API_CAMERA_SNAPSHOT

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
        self._attr_name = f"{coordinator.device_name} Camera {camera_id}"
        self._attr_unique_id = f"{coordinator.host}_camera_{camera_id}"
        self._stream_source = None
        self._last_image = None
        self._attr_supported_features = CameraEntityFeature.STREAM
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": coordinator.device_name,
            "manufacturer": "2N",
            "model": "IP Intercom",
        }

    async def stream_source(self) -> str | None:
        """Return the RTSP stream source."""
        auth_string = ""
        if self.coordinator.username and self.coordinator.password:
            auth_string = f"{self.coordinator.username}:{self.coordinator.password}@"
            
        # 2N devices use port 554 for RTSP by default
        return f"rtsp://{auth_string}{self.coordinator.host}:554/h264_stream"

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image from the camera."""
        try:
            websession = async_get_clientsession(self.hass)
            auth = None
            if self.coordinator.username and self.coordinator.password:
                auth = aiohttp.BasicAuth(self.coordinator.username, self.coordinator.password)

            # 2N uses this endpoint for snapshots
            url = f"http://{self.coordinator.host}{API_CAMERA_SNAPSHOT}"
            
            timeout = aiohttp.ClientTimeout(total=10, connect=5)
            
            async with websession.get(
                url,
                auth=auth,
                timeout=timeout,
                ssl=False,
                raise_for_status=False,
            ) as response:
                if response.status == 200:
                    return await response.read()
                elif response.status == 401:
                    _LOGGER.error(
                        "Authentication failed for camera snapshot. Check username/password."
                    )
                else:
                    _LOGGER.error(
                        "Error getting camera image from %s: %s",
                        self.coordinator.host,
                        response.status,
                    )
                    
                try:
                    error_text = await response.text()
                    _LOGGER.debug("Error response: %s", error_text)
                except Exception as e:
                    _LOGGER.debug("Could not read error response: %s", e)
                
        except aiohttp.ClientConnectorError as err:
            _LOGGER.error("Connection failed to camera at %s: %s", self.coordinator.host, err)
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout getting camera image from %s", self.coordinator.host)
        except Exception as err:
            _LOGGER.error("Error getting camera image from %s: %s", self.coordinator.host, err)
            
        return None

    @property
    def extra_state_attributes(self):
        """Return the camera state attributes."""
        return {
            "rtsp_url": f"rtsp://{self.coordinator.host}:554/h264_stream",
            "snapshot_url": f"http://{self.coordinator.host}{API_CAMERA_SNAPSHOT}",
        }
