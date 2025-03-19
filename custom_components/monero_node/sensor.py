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
        MoneroNodeSensor(coordinator, config, "remaining_sync_time", "Remaining Sync Time", "mdi:clock-outline"),
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
            update_interval=timedelta(seconds=config.get('refresh_interval', 60))  # Intervalle de mise à jour
        )
        self.config = config
        self._prev_local_height = None
        self._prev_update_time = None

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            current_time = self.hass.loop.time()
            async with aiohttp.ClientSession() as session:
                headers = {'User-Agent': 'HomeAssistant/MoneroNodeIntegration'}

                # Fetch global height from the Monero Node API
                async with session.get(self.config['global_height_url'], headers=headers) as response:
                    if response.status != 200:
                        raise ValueError(f"Cannot connect to global height URL. Status code: {response.status}")
                    global_height_data = await response.json()

                    global_height = global_height_data.get('data', {}).get('best_block_height', 0)

                # Fetch local height
                async with session.get(self.config['local_height_url'], headers=headers) as response:
                    if response.status != 200:
                        raise ValueError(f"Cannot connect to local height URL. Status code: {response.status}")
                    local_height_data = await response.json()

                # Fetch Monero price
                async with session.get(self.config['price_url'], headers=headers) as response:
                    if response.status != 200:
                        raise ValueError(f"Cannot connect to price URL. Status code: {response.status}")
                    price_data = await response.json()

            current_local_height = local_height_data.get('height', 0)
            
            data = {
                'global_height': global_height,
                'local_height': current_local_height,
                'monero_price': price_data.get('monero', {}).get('usd', 0),
            }

            # Calculate node sync percentage
            data['node_sync_percentage'] = (
                (data['local_height'] / data['global_height']) * 100
                if data['global_height'] > 0 else 0
            )
            
            # Calculate remaining sync time estimation
            remaining_sync_time = None
            if self._prev_local_height is not None and self._prev_update_time is not None:
                # Calculate blocks per second
                time_diff = current_time - self._prev_update_time
                blocks_diff = current_local_height - self._prev_local_height
                
                if time_diff > 0 and blocks_diff > 0:
                    blocks_per_second = blocks_diff / time_diff
                    remaining_blocks = global_height - current_local_height
                    
                    if blocks_per_second > 0:
                        remaining_seconds = remaining_blocks / blocks_per_second
                        
                        # Format the remaining time
                        if remaining_seconds < 60:
                            remaining_sync_time = f"{int(remaining_seconds)} seconds"
                        elif remaining_seconds < 3600:
                            remaining_sync_time = f"{int(remaining_seconds / 60)} minutes"
                        elif remaining_seconds < 86400:
                            hours = int(remaining_seconds / 3600)
                            minutes = int((remaining_seconds % 3600) / 60)
                            remaining_sync_time = f"{hours} hours {minutes} minutes"
                        else:
                            days = int(remaining_seconds / 86400)
                            hours = int((remaining_seconds % 86400) / 3600)
                            remaining_sync_time = f"{days} days {hours} hours"
            
            # Update previous values for next calculation
            self._prev_local_height = current_local_height
            self._prev_update_time = current_time
            
            data['remaining_sync_time'] = remaining_sync_time if remaining_sync_time else "Calculating..."

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
        if self._type in ["node_sync_percentage"]:
            return SensorStateClass.TOTAL
        return SensorStateClass.MEASUREMENT