from homeassistant import config_entries
from .const import DOMAIN

class MoneroNodeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Monero Node."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="Monero Node", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_user_schema()
        )

    def _get_user_schema(self):
        """Return the input schema for the user."""
        from homeassistant.helpers.selector import TextSelector, TextSelectorConfig

        return {
            "local_api": TextSelector(TextSelectorConfig(type="url")),
            "global_api": TextSelector(TextSelectorConfig(type="url")),
            "coin_api": TextSelector(TextSelectorConfig(type="url")),
        }