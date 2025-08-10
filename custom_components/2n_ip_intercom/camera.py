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

from .const import (
    DOMAIN,
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
)

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

    _attr_has_entity_name = True

    def __init__(self, coordinator, camera_id):
        """Initialize the camera."""
        super().__init__()
        self.coordinator = coordinator
        self.camera_id = camera_id
        self._attr_name = f"Camera {camera_id}"  # Will appear as "2N IP Intercom Camera 1"
        self._attr_unique_id = f"{coordinator.host}_camera_{camera_id}"
        self._stream_source = None
        self._last_image = None
        self._attr_supported_features = CameraEntityFeature.STREAM
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": "2N IP Intercom",
            "manufacturer": "2N",
            "model": "IP Intercom"
        }
        
        # Update with device info if available
        if coordinator.device_info:
            self._attr_device_info.update({
                "name": coordinator.device_info.get("model", "2N IP Intercom"),
                "model": coordinator.device_info.get("model", "IP Intercom"),
                "sw_version": coordinator.device_info.get("firmwareVersion"),
            })

    async def stream_source(self) -> str | None:
        """Return the RTSP stream source."""
        username = self.coordinator.username or DEFAULT_USERNAME
        password = self.coordinator.password or DEFAULT_PASSWORD
        auth_string = f"{username}:{password}@"
            
        # 2N devices use port 554 for RTSP by default
        return f"rtsp://{auth_string}{self.coordinator.host}:554/h264_stream"

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image from the camera."""
        try:
            websession = async_get_clientsession(self.hass)
            auth = aiohttp.BasicAuth(
                login=self.coordinator.username or DEFAULT_USERNAME,
                password=self.coordinator.password or DEFAULT_PASSWORD,
            )

            # 2N uses this endpoint for snapshots
            url = f"{self.coordinator.base_url}/api/camera/snapshot"
            
            _LOGGER.debug(
                "Making camera snapshot request to %s with username %s",
                url,
                self.coordinator.username or DEFAULT_USERNAME,
            )
            
            async with websession.get(
                url,
                auth=auth,
                timeout=10,
                ssl=False,
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
                
        except Exception as err:
            _LOGGER.error("Error getting camera image: %s", err)
            
        return None

    @property
    def extra_state_attributes(self):
        """Return the camera state attributes."""
        username = self.coordinator.username or DEFAULT_USERNAME
        password = self.coordinator.password or DEFAULT_PASSWORD
        
        return {
            "rtsp_url": f"rtsp://{username}:{password}@{self.coordinator.host}:554/h264_stream",
            "snapshot_url": f"http://{username}:{password}@{self.coordinator.host}/api/camera/snapshot",
        }
