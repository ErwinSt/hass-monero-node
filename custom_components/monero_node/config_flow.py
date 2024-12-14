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

class MoneroOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for the Monero integration."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_data = self.config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("name", default=current_data.get("name", "Monero Node")): str,
                vol.Optional(CONF_LOCAL_API, default=current_data.get(CONF_LOCAL_API, "http://IP:18089/get_height")): str,
                vol.Optional(CONF_GLOBAL_API, default=current_data.get(CONF_GLOBAL_API, "")): str,
                vol.Optional(CONF_COIN_API, default=current_data.get(CONF_COIN_API, "")): str,
                vol.Optional("refresh_interval", default=current_data.get("refresh_interval", 60)): int,
            })
        )