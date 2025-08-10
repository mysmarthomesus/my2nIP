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

    sensors = []
    
    # Device state sensor
    sensors.append(
        TwoNIntercomSensor(
            coordinator,
            SensorEntityDescription(
                key="device_state",
                name="State",
                icon="mdi:door",
            ),
        )
    )
    
    # System sensors if available from device_info
    if coordinator.device_info:
        if "serialNumber" in coordinator.device_info:
            sensors.append(
                TwoNIntercomSensor(
                    coordinator,
                    SensorEntityDescription(
                        key="serial_number",
                        name="Serial Number",
                        icon="mdi:identifier",
                    ),
                )
            )
        
        if "macAddress" in coordinator.device_info:
            sensors.append(
                TwoNIntercomSensor(
                    coordinator,
                    SensorEntityDescription(
                        key="mac_address",
                        name="MAC Address",
                        icon="mdi:network",
                    ),
                )
            )
            
        if "firmwareVersion" in coordinator.device_info:
            sensors.append(
                TwoNIntercomSensor(
                    coordinator,
                    SensorEntityDescription(
                        key="firmware_version",
                        name="Firmware Version",
                        icon="mdi:cellphone-arrow-down",
                    ),
                )
            )

    async_add_entities(sensors, True)


class TwoNIntercomSensor(CoordinatorEntity, SensorEntity):
    """Representation of a 2N IP Intercom sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TwoNIntercomDataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.host}_{description.key}"
        
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
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.host}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": "2N IP Intercom",
            "manufacturer": "2N",
            "model": "IP Intercom",
        }

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.coordinator.data.get("deviceState")
