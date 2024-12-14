import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_LOCAL_API, CONF_GLOBAL_API, CONF_COIN_API, DEFAULT_LOCAL_API, DEFAULT_GLOBAL_API, DEFAULT_COIN_API

class MoneroNodeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Monero Node."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="Monero Node", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_LOCAL_API, default=DEFAULT_LOCAL_API): str,
                vol.Required(CONF_GLOBAL_API, default=DEFAULT_GLOBAL_API): str,
                vol.Optional(CONF_COIN_API, default=DEFAULT_COIN_API): str,
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MoneroNodeOptionsFlowHandler(config_entry)

class MoneroNodeOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Monero Node."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options configuration."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_LOCAL_API, default=self.config_entry.data[CONF_LOCAL_API]): str,
                vol.Required(CONF_GLOBAL_API, default=self.config_entry.data[CONF_GLOBAL_API]): str,
                vol.Optional(CONF_COIN_API, default=self.config_entry.data[CONF_COIN_API]): str,
            })
        )