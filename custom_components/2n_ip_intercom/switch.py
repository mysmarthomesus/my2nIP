"""Support for 2N IP Intercom switches with optional hold and release switches."""
from __future__ import annotations

import asyncio
import aiohttp
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, API_SWITCH_CONTROL, API_DOOR_CONTROL
from .coordinator import TwoNIntercomDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up 2N IP Intercom switches based on a config entry."""
    coordinator: TwoNIntercomDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    switches: list[SwitchEntity] = [
        TwoNIntercomDoorSwitch(coordinator),
        TwoNIntercomSwitch(coordinator, 1, f"{coordinator.device_name} Switch 1"),
    ]

    # Add additional port/hold/release switches if available
    for switch_id, switch_info in enumerate(coordinator.data.get("ports", []), start=2):
        # Normal switch
        switches.append(
            TwoNIntercomSwitch(
                coordinator,
                switch_id,
                switch_info.get("name", f"Switch {switch_id}"),
            )
        )

        # Add hold + release switches if bistable
        if switch_info.get("mode") == "bistable":
            base_name = switch_info.get("name", f"Switch {switch_id}")
            hold_entity = TwoNIntercomHoldSwitch(coordinator, switch_id, f"{base_name} Hold")
            release_entity = TwoNIntercomReleaseSwitch(coordinator, switch_id, f"{base_name} Release", hold_entity)
            switches.append(hold_entity)
            switches.append(release_entity)

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
    """Hold switch for bistable 2N ports."""

    def __init__(self, coordinator, switch_id: int, name: str) -> None:
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
        return self._state

    async def async_turn_on(self, **kwargs) -> None:
        """Send hold action."""
        await self._send_action("hold")
        self._state = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Disabled: use the Release button to end hold."""
        return

    async def _send_action(self, action: str) -> None:
        params = {"switch": str(self._switch_id), "action": action}
        async with aiohttp.ClientSession() as session:
            auth = (
                aiohttp.BasicAuth(self.coordinator.username, self.coordinator.password)
                if self.coordinator.username and self.coordinator.password
                else None
            )
            await session.get(
                f"{self.coordinator.base_url}{API_SWITCH_CONTROL}",
                params=params,
                auth=auth,
            )
        await self.coordinator.async_request_refresh()

    def release(self) -> None:
        """Called externally when Release switch is pressed."""
        self._state = False
        self.async_write_ha_state()


class TwoNIntercomReleaseSwitch(CoordinatorEntity, SwitchEntity):
    """Release switch for bistable 2N ports."""

    def __init__(self, coordinator, switch_id: int, name: str, hold_entity: TwoNIntercomHoldSwitch) -> None:
        super().__init__(coordinator)
        self._switch_id = switch_id
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.host}_release_switch_{switch_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=coordinator.device_name,
            manufacturer="2N",
            model="IP Intercom",
        )
        self._hold_entity = hold_entity
        self._state = False

    @property
    def is_on(self) -> bool:
        return self._state

    async def async_turn_on(self, **kwargs) -> None:
        """Send release action and reset hold switch."""
        await self._send_action("release")
        self._state = True
        self.async_write_ha_state()

        # Reset hold entity state
        self._hold_entity.release()

        # Reset release back to off after 1s
        await asyncio.sleep(1)
        self._state = False
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """No-op, release is momentary."""
        self._state = False
        self.async_write_ha_state()

    async def _send_action(self, action: str) -> None:
        params = {"switch": str(self._switch_id), "action": action}
        async with aiohttp.ClientSession() as session:
            auth = (
                aiohttp.BasicAuth(self.coordinator.username, self.coordinator.password)
                if self.coordinator.username and self.coordinator.password
                else None
            )
            await session.get(
                f"{self.coordinator.base_url}{API_SWITCH_CONTROL}",
                params=params,
                auth=auth,
            )
        await self.coordinator.async_request_refresh()
