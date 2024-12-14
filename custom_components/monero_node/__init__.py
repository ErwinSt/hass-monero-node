from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up Monero Node integration."""
    hass.data[DOMAIN] = {}
    return True