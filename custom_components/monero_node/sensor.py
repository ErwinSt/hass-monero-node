"""Sensor platform for Monero Node integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import aiohttp
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the Monero Node sensor platform."""
    config = entry.data
    coordinator = MoneroNodeDataUpdateCoordinator(hass, config)
    await coordinator.async_config_entry_first_refresh()

    sensors = [
        MoneroNodeSensor(coordinator, config, "global_height", "Global Height", "mdi:counter"),
        MoneroNodeSensor(coordinator, config, "local_height", "Local Height", "mdi:counter"),
        MoneroNodeSensor(coordinator, config, "monero_price", "Monero Price", "mdi:currency-usd"),
        MoneroNodeSensor(coordinator, config, "node_sync_percentage", "Node Sync Percentage", "mdi:sync"),
    ]

    async_add_entities(sensors)

class MoneroNodeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Monero Node data from API."""

    def __init__(self, hass, config):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=config.get('refresh_interval', 60))
        )
        self.config = config

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'User-Agent': 'HomeAssistant/MoneroNodeIntegration'}

                # Fetch global height with alternative parsing
                async with session.get(self.config['global_height_url'], headers=headers) as response:
                    if response.status != 200:
                        raise ValueError(f"Cannot connect to global height URL. Status code: {response.status}")
                    global_height_data = await response.json()

                    # Extract the global height from the new API response
                    global_height = global_height_data.get('data', {}).get('best_block_height', 0)

                # Fetch local height
                async with session.get(self.config['local_height_url'], headers=headers) as response:
                    local_height_data = await response.json()

                # Fetch Monero price
                async with session.get(self.config['price_url'], headers=headers) as response:
                    price_data = await response.json()

            data = {
                'global_height': global_height,  # Use the new global height value
                'local_height': local_height_data.get('height', 0),
                'monero_price': price_data.get('monero', {}).get('usd', 0),
            }

            # Calculate node sync percentage
            data['node_sync_percentage'] = (
                (data['local_height'] / data['global_height']) * 100
                if data['global_height'] > 0 else 0
            )

            return data

        except Exception as err:
            _LOGGER.error(f"Error fetching Monero Node data: {err}")
            raise UpdateFailed(f"Error fetching Monero Node data: {err}") from err

class MoneroNodeSensor(CoordinatorEntity, SensorEntity):
    """Monero Node Sensor class."""

    def __init__(self, coordinator, config, sensor_type, name, icon):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config = config
        self._type = sensor_type
        self._attr_name = f"Monero Node {name}"
        self._attr_icon = icon
        self._attr_unique_id = f"{DOMAIN}_{config['entry_id']}_{sensor_type}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, config['entry_id'])},
            manufacturer="Monero",
            name=f"Monero Node {config['entry_id']}",
        )

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._type)

    @property
    def device_class(self):
        """Return the device class."""
        return "monetary" if self._type == "monero_price" else None

    @property
    def state_class(self):
        """Return the state class."""
        return SensorStateClass.MEASUREMENT if self._type != "node_sync_percentage" else SensorStateClass.TOTAL