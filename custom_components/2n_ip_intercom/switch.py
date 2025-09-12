"""Support for 2N IP Intercom switches with optional hold and release switches."""
from __future__ import annotations

import asyncio
import aiohttp
import logging

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

    if not coordinator.data:
        _LOGGER.warning("Coordinator has no data yet, initializing empty ports")
        coordinator.data = {"ports": []}

    switches: list[SwitchEntity] = []

    # Door switch
    switches.append(TwoNIntercomDoorSwitch(coordinator))

    # Main switch 1
    switches.append(TwoNIntercomSwitch(coordinator, 1, f"{coordinator.device_name} Switch 1"))

    # Additional port switches
    ports = coordinator.data.get("ports", [])
    _LOGGER.debug("Coordinator ports: %s", ports)

    for switch_id, switch_info in enumerate(ports, start=2):
        # Normal switch
        switches.append(
            TwoNIntercomSwitch(
                coordinator,
                switch_id,
                switch_info.get("name", f"Switch {switch_id}"),
            )
        )

        # Hold + Release for bistable switches
        if switch_info.get("mode") == "bistable":
            base_name = switch_info.get("name", f"Switch {switch_id}")
            switches.append(TwoNIntercomHoldSwitch(coordinator, switch_id, f"{base_name} Hold"))
            switches.append(TwoNIntercomReleaseSwitch(coordinator, switch_id, f"{base_name} Release"))

    for switch in switches:
        _LOGGER.info("Adding switch entity: %s (%s)", switch.name, switch.unique_id)

    async_add_entities(switches)


class TwoNIntercomDoorSwitch(CoordinatorEntity, SwitchEntity):
    """Door switch for 2N IP Intercom."""

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
            auth = aiohttp.BasicAuth(self.coordinator.username, self.coordinator.password) \
                if self.coordinator.username and self.coordinator.password else None
            await session.get(
                f"{self.coordinator.base_url}{API_DOOR_CONTROL}",
                params={"switch": "1", "action": action},
                auth=auth,
            )
        await self.coordinator.async_request_refresh()


class TwoNIntercomSwitch(CoordinatorEntity, SwitchEntity):
    """Normal switch for 2N IP Intercom."""

    def __init__(self, coordinator: TwoNIntercomDataUpdateCoordinator, switch_id: int, name: str) -> None:
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
            auth = aiohttp.BasicAuth(self.coordinator.username, self.coordinator.password) \
                if self.coordinator.username and self.coordinator.password else None
            await session.get(
                f"{self.coordinator.base_url}{API_SWITCH_CONTROL}",
                params={"switch": str(self._switch_id), "action": action},
                auth=auth,
            )
        await self.coordinator.async_request_refresh()


class TwoNIntercomHoldSwitch(CoordinatorEntity, SwitchEntity):
    """Hold switch for bistable ports (manual hold until release)."""

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
        """Send hold action until manually released."""
        await self._send_action("hold")
        self._state = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Release hold manually."""
        await self._send_action("release")
        self._state = False
        self.async_write_ha_state()

    async def _send_action(self, action: str) -> None:
        params = {"switch": str(self._switch_id), "action": action}
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(self.coordinator.username, self.coordinator.password) \
                if self.coordinator.username and self.coordinator.password else None
            await session.get(
                f"{self.coordinator.base_url}{API_SWITCH_CONTROL}",
                params=params,
                auth=auth,
            )
        await self.coordinator.async_request_refresh()


class TwoNIntercomReleaseSwitch(CoordinatorEntity, SwitchEntity):
    """Release switch for bistable ports (manual release)."""

    def __init__(self, coordinator, switch_id: int, name: str) -> None:
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
        self._state = False

    @property
    def is_on(self) -> bool:
        return self._state

    async def async_turn_on(self, **kwargs) -> None:
        """Send release action (stateless trigger)."""
        await self._send_action("release")
        self._state = True
        self.async_write_ha_state()

        # Reset state after 1 second for momentary button effect
        async def reset_state():
            await asyncio.sleep(1)
            self._state = False
            self.async_write_ha_state()

        self.hass.async_create_task(reset_state())

    async def async_turn_off(self, **kwargs) -> None:
        """No-op for release button."""
        self._state = False
        self.async_write_ha_state()

    async def _send_action(self, action: str) -> None:
        params = {"switch": str(self._switch_id), "action": action}
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(self.coordinator.username, self.coordinator.password) \
                if self.coordinator.username and self.coordinator.password else None
            await session.get(
                f"{self.coordinator.base_url}{API_SWITCH_CONTROL}",
                params=params,
                auth=auth,
            )
        await self.coordinator.async_request_refresh()
