"""Support for 2N IP Intercom switches with optional hold switches."""
from __future__ import annotations

import asyncio
import logging
import aiohttp
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, API_SWITCH_CONTROL, API_DOOR_CONTROL
from .coordinator import TwoNIntercomDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up 2N IP Intercom switches based on a config entry."""
    coordinator: TwoNIntercomDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    switches: list[SwitchEntity] = [
        TwoNIntercomDoorSwitch(coordinator),
        TwoNIntercomSwitch(coordinator, 1, f"{coordinator.device_name} Switch 01"),
        # Test: Always create a Hold switch for Switch 01 to test functionality
        TwoNIntercomHoldSwitch(coordinator, 1, f"{coordinator.device_name} Switch 01 Hold"),
    ]

    # Add additional port/hold switches if available
    for switch_id, switch_info in enumerate(coordinator.data.get("ports", []), start=2):
        # Normal switch
        switches.append(
            TwoNIntercomSwitch(
                coordinator,
                switch_id,
                switch_info.get("name", f"Switch {switch_id}"),
            )
        )

        # Add hold switch if bistable
        if switch_info.get("mode") == "bistable":
            switches.append(
                TwoNIntercomHoldSwitch(
                    coordinator,
                    switch_id,
                    f"{switch_info.get('name', f'Switch {switch_id}')} Hold",
                )
            )

    # Debug logging to see what switches are being created
    _LOGGER.debug("Creating %d switches for %s", len(switches), coordinator.device_name)
    for switch in switches:
        _LOGGER.debug("Switch: %s (ID: %s)", switch.name, switch.unique_id)

    async_add_entities(switches)


class TwoNIntercomDoorSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a 2N IP Intercom door switch."""

    def __init__(self, coordinator: TwoNIntercomDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_name = f"{coordinator.device_name} Door"
        self._attr_unique_id = f"{coordinator.host}_door"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=coordinator.device_name,
            manufacturer="2N",
            model="IP Intercom",
        )

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("doorState") == "unlocked"

    async def async_turn_on(self, **kwargs) -> None:
        await self._send_door_action("on")

    async def async_turn_off(self, **kwargs) -> None:
        await self._send_door_action("off")

    async def _send_door_action(self, action: str) -> None:
        async with aiohttp.ClientSession() as session:
            auth = (
                aiohttp.BasicAuth(self.coordinator.username, self.coordinator.password)
                if self.coordinator.username and self.coordinator.password
                else None
            )
            await session.get(
                f"{self.coordinator.base_url}{API_DOOR_CONTROL}",
                params={"switch": "1", "action": action},
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
        super().__init__(coordinator)
        self._switch_id = switch_id
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.host}_switch_{switch_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=coordinator.device_name,
            manufacturer="2N",
            model="IP Intercom",
        )

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get(f"switch{self._switch_id}State") == "on"

    async def async_turn_on(self, **kwargs) -> None:
        await self._send_switch_action("on")

    async def async_turn_off(self, **kwargs) -> None:
        await self._send_switch_action("off")

    async def _send_switch_action(self, action: str) -> None:
        async with aiohttp.ClientSession() as session:
            auth = (
                aiohttp.BasicAuth(self.coordinator.username, self.coordinator.password)
                if self.coordinator.username and self.coordinator.password
                else None
            )
            await session.get(
                f"{self.coordinator.base_url}{API_SWITCH_CONTROL}",
                params={"switch": str(self._switch_id), "action": action},
                auth=auth,
            )
        await self.coordinator.async_request_refresh()


class TwoNIntercomHoldSwitch(CoordinatorEntity, SwitchEntity):
    """Hold switch for bistable 2N ports (uses hold/release actions)."""

    def __init__(self, coordinator: TwoNIntercomDataUpdateCoordinator, switch_id: int, name: str) -> None:
        super().__init__(coordinator)
        self._switch_id = switch_id
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.host}_hold_switch_{switch_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=coordinator.device_name,
            manufacturer="2N",
            model="IP Intercom",
        )
        self._state = False

    @property
    def is_on(self) -> bool:
        """Return True if currently held."""
        return self._state

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    async def async_turn_on(self, **kwargs) -> None:
        """Send hold action and maintain state until manually turned off."""
        try:
            await self._send_action("hold")
            self._state = True
            self.async_write_ha_state()
            _LOGGER.info("Hold switch %s activated", self._switch_id)
        except Exception as e:
            _LOGGER.error("Failed to hold switch %s: %s", self._switch_id, e)

    async def async_turn_off(self, **kwargs) -> None:
        """Send release action to turn off the hold switch."""
        try:
            await self._send_action("release")
            self._state = False
            self.async_write_ha_state()
            _LOGGER.info("Hold switch %s released", self._switch_id)
        except Exception as e:
            _LOGGER.error("Failed to release switch %s: %s", self._switch_id, e)

    async def _send_action(self, action: str) -> None:
        """Send hold or release action to the 2N switch."""
        params = {"switch": str(self._switch_id), "action": action}

        # Reuse session from coordinator if available, otherwise create new session
        session = getattr(self.coordinator, "_aiohttp_session", None)
        close_session = False
        if session is None:
            session = aiohttp.ClientSession()
            close_session = True

        try:
            auth = (
                aiohttp.BasicAuth(self.coordinator.username, self.coordinator.password)
                if self.coordinator.username and self.coordinator.password
                else None
            )
            async with session.get(
                f"{self.coordinator.base_url}{API_SWITCH_CONTROL}",
                params=params,
                auth=auth,
            ) as resp:
                if resp.status != 200:
                    _LOGGER.warning(
                        "Failed to send action '%s' to switch %s, HTTP status %s",
                        action,
                        self._switch_id,
                        resp.status,
                    )
        finally:
            if close_session:
                await session.close()

        await self.coordinator.async_request_refresh()