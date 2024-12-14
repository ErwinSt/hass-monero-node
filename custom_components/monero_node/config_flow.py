import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, DEFAULT_LOCAL_API, DEFAULT_GLOBAL_API, DEFAULT_COIN_API

class MoneroNodeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Monero Node."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Valider les données saisies par l'utilisateur
            return self.async_create_entry(title="Monero Node", data=user_input)

        # Définir le schéma de formulaire
        data_schema = vol.Schema(
            {
                vol.Optional("local_api", default=DEFAULT_LOCAL_API): str,
                vol.Optional("global_api", default=DEFAULT_GLOBAL_API): str,
                vol.Optional("coin_api", default=DEFAULT_COIN_API): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )