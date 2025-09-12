"""The 2N IP Intercom integration."""
import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import TwoNIntercomDataUpdateCoordinator

PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.CAMERA]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the 2N IP Intercom component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up 2N IP Intercom from a config entry."""
    coordinator = TwoNIntercomDataUpdateCoordinator(hass, entry.data)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Failed to fetch data from 2N Intercom: %s", err)
        raise ConfigEntryNotReady from err

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setup to all platforms
    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()
    return unload_ok
