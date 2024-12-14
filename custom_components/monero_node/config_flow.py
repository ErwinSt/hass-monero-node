"""Config flow for Monero Node integration."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class MoneroNodeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Monero Node."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                await self._validate_input(user_input)
                unique_id = f"monero_node_{user_input['local_height_url']}"
                
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, "Monero Node"),
                    data={
                        **user_input,
                        'entry_id': self.context.get('unique_id', unique_id)
                    }
                )
            except ValueError as err:
                errors["base"] = str(err)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required('global_height_url', default='https://localmonero.co/blocks/api/get_stats'): str,
                vol.Required('local_height_url', default='http://localhost:18089/get_height'): str,
                vol.Required('price_url', default='https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd'): str,
                vol.Required('refresh_interval', default=60): int,
                vol.Optional(CONF_NAME, default='Monero Node'): str,
            }),
            errors=errors
        )

    async def _validate_input(self, user_input: Dict[str, Any]) -> None:
        """Validate the user input allows us to connect."""
        session = async_create_clientsession(self.hass)

        try:
            async with session.get(user_input['global_height_url'], headers={'User-Agent': 'HomeAssistant/MoneroNodeIntegration'}) as response:
                if response.status != 200:
                    raise ValueError(f"Cannot connect to global height URL. Status code: {response.status}")
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' not in content_type:
                    text = await response.text()
                    _LOGGER.error(f"Global height URL returned non-JSON. Content type: {content_type}, Content: {text[:500]}")
                    raise ValueError(f"Global height URL returned non-JSON content. Content type: {content_type}")
                await response.json()

            async with session.get(user_input['local_height_url'], headers={'User-Agent': 'HomeAssistant/MoneroNodeIntegration'}) as response:
                if response.status != 200:
                    raise ValueError(f"Cannot connect to local height URL. Status code: {response.status}")
                await response.json()

            async with session.get(user_input['price_url'], headers={'User-Agent': 'HomeAssistant/MoneroNodeIntegration'}) as response:
                if response.status != 200:
                    raise ValueError(f"Cannot connect to price URL. Status code: {response.status}")
                await response.json()

        except (aiohttp.ClientError, ValueError, KeyError) as err:
            _LOGGER.error(f"Validation error: {err}")
            raise ValueError(f"Invalid URLs or cannot connect to APIs: {err}") from err

async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    """Set up Monero Node from a config entry."""
    return True