import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries
from .const import DOMAIN

CONFIG_SCHEMA = vol.Schema({
    vol.Required("host"): cv.string,
    vol.Optional("port", default=80): cv.positive_int,
    vol.Optional("username", default=""): cv.string,
    vol.Optional("password", default=""): cv.string,
})


class TwoNIPIntercomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for the 2N IP Intercom integration."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Optionally, add connection validation here
            return self.async_create_entry(title="2N IP Intercom", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
            errors=errors,
        )
