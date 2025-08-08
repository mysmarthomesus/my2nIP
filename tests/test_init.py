"""Tests for the 2N IP Intercom integration."""
from unittest.mock import patch
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from custom_components.2n_ip_intercom.const import DOMAIN

async def test_setup(hass: HomeAssistant):
    """Test setup of the integration."""
    assert await hass.config_entries.async_setup(DOMAIN)
    assert DOMAIN in hass.data

@pytest.fixture
def mock_setup_entry():
    """Mock setting up a config entry."""
    with patch(
        "custom_components.2n_ip_intercom.async_setup_entry", return_value=True
    ) as mock_setup:
        yield mock_setup
