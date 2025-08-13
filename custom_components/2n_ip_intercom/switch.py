"""Support for 2N IP Intercom switches."""
from __future__ import annotations

import aiohttp
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    API_SWITCH_CONTROL,
    API_DOOR_CONTROL,
    SWITCH_MODE_PULSE,
    SWITCH_MODE_TOGGLE,
)
from .coordinator import TwoNIntercomDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up 2N IP Intercom switch based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    switches = [
        TwoNIntercomDoorSwitch(coordinator),
        TwoNIntercomSwitch(coordinator, 1, f"{coordinator.device_name} Switch 1"),
    ]

    async_add_entities(switches)


class TwoNIntercomDoorSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a 2N IP Intercom door switch."""

    def __init__(self, coordinator: TwoNIntercomDataUpdateCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_name = f"{coordinator.device_name} Door"
        self._attr_unique_id = f"{coordinator.host}_door"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": coordinator.device_name,
            "manufacturer": "2N",
            "model": "IP Intercom",
        }

    @property
    def is_on(self) -> bool:
        """Return true if the door is unlocked."""
        return self.coordinator.data.get("doorState") == "unlocked"

    async def async_turn_on(self, **kwargs) -> None:
        """Unlock the door."""
        try:
            session = await self.coordinator._get_session()
            auth = None
            if self.coordinator.username and self.coordinator.password:
                auth = aiohttp.BasicAuth(
                    self.coordinator.username,
                    self.coordinator.password,
                )

            async with session.get(
                f"{self.coordinator.base_url}{API_DOOR_CONTROL}",
                params={"switch": "1", "action": "on"},
                auth=auth,
                ssl=False,
                raise_for_status=False
            ) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to turn on door switch: HTTP %s", resp.status)
                    
        except Exception as err:
            _LOGGER.error("Error turning on door switch: %s", err)
            
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Lock the door."""
        try:
            session = await self.coordinator._get_session()
            auth = None
            if self.coordinator.username and self.coordinator.password:
                auth = aiohttp.BasicAuth(
                    self.coordinator.username,
                    self.coordinator.password,
                )

            async with session.get(
                f"{self.coordinator.base_url}{API_DOOR_CONTROL}",
                params={"switch": "1", "action": "off"},
                auth=auth,
                ssl=False,
                raise_for_status=False
            ) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to turn off door switch: HTTP %s", resp.status)
                    
        except Exception as err:
            _LOGGER.error("Error turning off door switch: %s", err)
            
        await self.coordinator.async_request_refresh()


class TwoNIntercomSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a 2N IP Intercom switch."""

    def __init__(
        self,
        coordinator: TwoNIntercomDataUpdateCoordinator,
        switch_id: int,
        name: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._switch_id = switch_id
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.host}_switch_{switch_id}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": coordinator.device_name,
            "manufacturer": "2N",
            "model": "IP Intercom",
        }

    @property
    def extra_state_attributes(self):
        """Return the switch state attributes."""
        return {
            "switch_mode": self.coordinator.switch_mode,
            "switch_id": self._switch_id,
        }

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        if self.coordinator.switch_mode == SWITCH_MODE_TOGGLE:
            # In toggle mode, track the state locally
            return self.coordinator._switch_states.get(f"switch_{self._switch_id}", False)
        else:
            # In pulse mode, check coordinator data (traditional behavior)
            return self.coordinator.data.get(f"switch{self._switch_id}State") == "on"

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        try:
            session = await self.coordinator._get_session()
            auth = None
            if self.coordinator.username and self.coordinator.password:
                auth = aiohttp.BasicAuth(
                    self.coordinator.username,
                    self.coordinator.password,
                )

            # Send switch on command
            async with session.get(
                f"{self.coordinator.base_url}{API_SWITCH_CONTROL}",
                params={"switch": str(self._switch_id), "action": "on"},
                auth=auth,
                ssl=False,
                raise_for_status=False
            ) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to turn on switch %s: HTTP %s", self._switch_id, resp.status)
                    
            # Update local state for toggle mode
            if self.coordinator.switch_mode == SWITCH_MODE_TOGGLE:
                self.coordinator._switch_states[f"switch_{self._switch_id}"] = True
                
        except Exception as err:
            _LOGGER.error("Error turning on switch %s: %s", self._switch_id, err)
            
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        if self.coordinator.switch_mode == SWITCH_MODE_PULSE:
            # In pulse mode, we don't actually send an off command
            # The device handles this automatically
            return
            
        try:
            session = await self.coordinator._get_session()
            auth = None
            if self.coordinator.username and self.coordinator.password:
                auth = aiohttp.BasicAuth(
                    self.coordinator.username,
                    self.coordinator.password,
                )

            # Send switch off command (only in toggle mode)
            async with session.get(
                f"{self.coordinator.base_url}{API_SWITCH_CONTROL}",
                params={"switch": str(self._switch_id), "action": "off"},
                auth=auth,
                ssl=False,
                raise_for_status=False
            ) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to turn off switch %s: HTTP %s", self._switch_id, resp.status)
                    
            # Update local state
            self.coordinator._switch_states[f"switch_{self._switch_id}"] = False
            
        except Exception as err:
            _LOGGER.error("Error turning off switch %s: %s", self._switch_id, err)
            
        await self.coordinator.async_request_refresh()
