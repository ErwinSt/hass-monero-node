import aiohttp
import asyncio
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import PERCENTAGE, LENGTH_METERS, CURRENCY_DOLLAR
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from datetime import timedelta
import logging
import requests

from .const import DOMAIN, CONF_LOCAL_API, CONF_GLOBAL_API, CONF_COIN_API

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Legacy setup for Monero Node sensors."""
    pass

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Monero Node sensors based on configuration entry."""
    config = config_entry.data

    local_api = config.get(CONF_LOCAL_API)
    global_api = config.get(CONF_GLOBAL_API)
    coin_api = config.get(CONF_COIN_API)

    coordinator = MoneroNodeCoordinator(hass, local_api, global_api, coin_api)

    # Create the sensors
    async_add_entities([
        MoneroSyncSensor(coordinator),
        MoneroHeightSensor(coordinator, "local_height", "Local Height"),
        MoneroHeightSensor(coordinator, "global_height", "Global Height"),
        MoneroPriceSensor(coordinator)
    ])

class MoneroNodeCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch data from the Monero Node APIs."""

    def __init__(self, hass, local_api, global_api, coin_api):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Monero Node",
            update_interval=timedelta(seconds=30),
        )
        self.local_api = local_api
        self.global_api = global_api
        self.coin_api = coin_api

    async def _async_update_data(self):
        """Fetch data from APIs."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.local_api) as response:
                    local_data = await response.json()
            global_data = requests.get(self.global_api).json()
            coin_data = requests.get(self.coin_api).json()

            return {
                "local_height": local_data.get("height"),
                "global_height": global_data.get("height"),
                "monero_price": coin_data.get("monero", {}).get("usd"),
            }
        except Exception as e:
            _LOGGER.error(f"Error fetching data: {e}")
            return {}

class MoneroSyncSensor(CoordinatorEntity, SensorEntity):
    """Sensor for sync percentage."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Monero Node Sync Percentage"
        self._attr_unit_of_measurement = PERCENTAGE
        self._attr_unique_id = f"{DOMAIN}_sync_percentage"

    @property
    def state(self):
        data = self.coordinator.data
        if data.get("local_height") and data.get("global_height"):
            return round((data["local_height"] / data["global_height"]) * 100, 2)
        return None

class MoneroHeightSensor(CoordinatorEntity, SensorEntity):
    """Sensor for heights (local or global)."""

    def __init__(self, coordinator, key, name):
        super().__init__(coordinator)
        self.key = key
        if key == "global_height":
            self._attr_name = name
            self._attr_unit_of_measurement = LENGTH_METERS
            self._attr_unique_id = f"{DOMAIN}_{key}"
        else:
            self._attr_name = name
            self._attr_unit_of_measurement = None
            self._attr_unique_id = f"{DOMAIN}_{key}"

    @property
    def state(self):
        return self.coordinator.data.get(self.key)

class MoneroPriceSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Monero price."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Monero Price"
        self._attr_unit_of_measurement = CURRENCY_DOLLAR
        self._attr_unique_id = f"{DOMAIN}_price"

    @property
    def state(self):
        return self.coordinator.data.get("monero_price")