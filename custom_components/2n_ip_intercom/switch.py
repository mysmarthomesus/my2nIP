"""Support for 2N IP Intercom switches."""
from __future__ import annotations

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
)
from .coordinator import TwoNIntercomDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up 2N IP Intercom switch based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    switches = [
        TwoNIntercomDoorSwitch(coordinator),
        TwoNIntercomSwitch(coordinator, 1, "Switch 1"),
    ]

    async_add_entities(switches)


class TwoNIntercomDoorSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a 2N IP Intercom door switch."""

    def __init__(self, coordinator: TwoNIntercomDataUpdateCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_name = "Door"
        self._attr_unique_id = f"{coordinator.host}_door"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": "2N IP Intercom",
            "manufacturer": "2N",
            "model": "IP Intercom",
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
            "name": "2N IP Intercom",
            "manufacturer": "2N",
            "model": "IP Intercom",
        }

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.coordinator.data.get(f"switch{self._switch_id}State") == "on"

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        async with aiohttp.ClientSession() as session:
            auth = None
            if self.coordinator.username and self.coordinator.password:
                auth = aiohttp.BasicAuth(
                    self.coordinator.username,
                    self.coordinator.password,
                )

            await session.get(
                f"{self.coordinator.base_url}{API_SWITCH_CONTROL}",
                params={"switch": str(self._switch_id), "action": "on"},
                auth=auth,
            )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        async with aiohttp.ClientSession() as session:
            auth = None
            if self.coordinator.username and self.coordinator.password:
                auth = aiohttp.BasicAuth(
                    self.coordinator.username,
                    self.coordinator.password,
                )

            await session.get(
                f"{self.coordinator.base_url}{API_SWITCH_CONTROL}",
                params={"switch": str(self._switch_id), "action": "off"},
                auth=auth,
            )
        await self.coordinator.async_request_refresh()
