"""Support for 2N IP Intercom sensors."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN
from .coordinator import TwoNIntercomDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up 2N IP Intercom sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        TwoNIntercomSensor(
            coordinator,
            SensorEntityDescription(
                key="device_state",
                name=f"{coordinator.device_name} Device State",
                icon="mdi:door",
            ),
        ),
    ]

    async_add_entities(sensors)


class TwoNIntercomSensor(CoordinatorEntity, SensorEntity):
    """Representation of a 2N IP Intercom sensor."""

    def __init__(
        self,
        coordinator: TwoNIntercomDataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.host}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": coordinator.device_name,
            "manufacturer": "2N",
            "model": "IP Intercom",
        }

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.coordinator.data.get("deviceState")
