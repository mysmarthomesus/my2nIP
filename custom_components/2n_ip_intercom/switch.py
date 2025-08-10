"""Support for 2N IP Intercom switches."""
from __future__ import annotations

import logging
import aiohttp

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    API_SWITCH_CONTROL,
    API_DOOR_CONTROL,
    API_SWITCH_STATUS,
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
)
from .coordinator import TwoNIntercomDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up 2N IP Intercom switches based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Create a list of switch entities
    switches = []
    
    # Add the door switch
    switches.append(TwoNIntercomDoorSwitch(coordinator))
    
    # Add regular switches (most 2N devices support up to 4 switches)
    try:
        # Query available switches
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(
                coordinator.username or DEFAULT_USERNAME,
                coordinator.password or DEFAULT_PASSWORD,
            )

            async with session.get(
                f"{coordinator.base_url}{API_SWITCH_STATUS}",
                auth=auth,
                ssl=False,
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Check for switches 1-4
                    for switch_id in range(1, 5):
                        if f"switch{switch_id}" in str(data):
                            switches.append(TwoNIntercomSwitch(coordinator, switch_id))
                else:
                    _LOGGER.error("Failed to get switch status: %s", response.status)

    except Exception as err:
        _LOGGER.error("Error setting up switches: %s", err)
        # Add at least one switch if we couldn't detect them
        switches.append(TwoNIntercomSwitch(coordinator, 1))

    async_add_entities(switches, True)


class TwoNIntercomDoorSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a 2N IP Intercom door switch."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: TwoNIntercomDataUpdateCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        # This will make the entity appear as "2N IP Intercom Door"
        self._attr_name = "Door"
        self._attr_unique_id = f"{coordinator.host}_door"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": coordinator.device_info.get("model", "2N IP Intercom"),
            "manufacturer": "2N",
            "model": coordinator.device_info.get("model", "IP Intercom"),
            "sw_version": coordinator.device_info.get("firmwareVersion", "Unknown"),
        }

    @property
    def is_on(self) -> bool:
        """Return true if the door is unlocked."""
        return self.coordinator.data.get("doorState") == "unlocked"

    async def async_turn_on(self, **kwargs) -> None:
        """Unlock the door."""
        async with aiohttp.ClientSession() as session:
            auth = None
            if self.coordinator.username and self.coordinator.password:
                auth = aiohttp.BasicAuth(
                    self.coordinator.username,
                    self.coordinator.password,
                )

            await session.get(
                f"{self.coordinator.base_url}{API_DOOR_CONTROL}",
                params={"switch": "1", "action": "on"},
                auth=auth,
            )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Lock the door."""
        async with aiohttp.ClientSession() as session:
            auth = None
            if self.coordinator.username and self.coordinator.password:
                auth = aiohttp.BasicAuth(
                    self.coordinator.username,
                    self.coordinator.password,
                )

            await session.get(
                f"{self.coordinator.base_url}{API_DOOR_CONTROL}",
                params={"switch": "1", "action": "off"},
                auth=auth,
            )
        await self.coordinator.async_request_refresh()


class TwoNIntercomSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a 2N IP Intercom switch."""

    _attr_has_entity_name = True
    
    def __init__(
        self,
        coordinator: TwoNIntercomDataUpdateCoordinator,
        switch_id: int,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._switch_id = switch_id
        # This will make the entity appear as "2N IP Intercom Switch 1", "2N IP Intercom Switch 2", etc.
        self._attr_name = f"Switch {switch_id}"
        self._attr_unique_id = f"{coordinator.host}_switch_{switch_id}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": coordinator.device_info.get("model", "2N IP Intercom"),
            "manufacturer": "2N",
            "model": coordinator.device_info.get("model", "IP Intercom"),
            "sw_version": coordinator.device_info.get("firmwareVersion", "Unknown"),
        }

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.coordinator.data.get(f"switch{self._switch_id}State") == "on"

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        try:
            async with aiohttp.ClientSession() as session:
                auth = aiohttp.BasicAuth(
                    self.coordinator.username or DEFAULT_USERNAME,
                    self.coordinator.password or DEFAULT_PASSWORD,
                )
                
                await session.get(
                    f"{self.coordinator.base_url}{API_SWITCH_CONTROL}",
                    params={"switch": str(self._switch_id), "action": "on"},
                    auth=auth,
                    ssl=False,
                )
                
                # Verify the switch state
                async with session.get(
                    f"{self.coordinator.base_url}{API_SWITCH_STATUS}",
                    auth=auth,
                    ssl=False,
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if f"switch{self._switch_id}" in data:
                            self._state = data[f"switch{self._switch_id}"]["state"] == "on"
                            self.async_write_ha_state()
                            
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error turning on switch %s: %s", self._switch_id, err)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        try:
            async with aiohttp.ClientSession() as session:
                auth = aiohttp.BasicAuth(
                    self.coordinator.username or DEFAULT_USERNAME,
                    self.coordinator.password or DEFAULT_PASSWORD,
                )
                
                await session.get(
                    f"{self.coordinator.base_url}{API_SWITCH_CONTROL}",
                    params={"switch": str(self._switch_id), "action": "off"},
                    auth=auth,
                    ssl=False,
                )
                
                # Verify the switch state
                async with session.get(
                    f"{self.coordinator.base_url}{API_SWITCH_STATUS}",
                    auth=auth,
                    ssl=False,
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if f"switch{self._switch_id}" in data:
                            self._state = data[f"switch{self._switch_id}"]["state"] == "on"
                            self.async_write_ha_state()
                            
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error turning off switch %s: %s", self._switch_id, err)
