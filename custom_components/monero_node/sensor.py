"""Sensor platform for Monero Node integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

import aiohttp
from homeassistant.components.sensor import (
    SensorEntity, 
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTime,
    UnitOfInformation,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, ATTR_SYNC_STATUS, ATTR_BLOCKS_BEHIND

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the Monero Node sensor platform."""
    config = entry.data
    coordinator = MoneroNodeDataUpdateCoordinator(hass, config)
    await coordinator.async_config_entry_first_refresh()

    sensors = [
        MoneroNodeSensor(
            coordinator, 
            config, 
            "global_height", 
            "Global Height", 
            "mdi:globe-model",
            SensorStateClass.MEASUREMENT,
            None,
            None,
            "blocks"
        ),
        MoneroNodeSensor(
            coordinator, 
            config, 
            "local_height", 
            "Local Height", 
            "mdi:database",
            SensorStateClass.MEASUREMENT,
            None,
            None,
            "blocks"
        ),
        MoneroNodeSensor(
            coordinator, 
            config, 
            "monero_price", 
            "Monero Price", 
            "mdi:currency-usd",
            SensorStateClass.MEASUREMENT,
            SensorDeviceClass.MONETARY,
            None,
            "USD"
        ),
        MoneroNodeSensor(
            coordinator, 
            config, 
            "node_sync_percentage", 
            "Node Sync Percentage", 
            "mdi:sync",
            SensorStateClass.MEASUREMENT,
            None,
            None,
            PERCENTAGE
        ),
        MoneroNodeSensor(
            coordinator, 
            config, 
            "blocks_behind", 
            "Blocks Behind", 
            "mdi:alert-circle-outline",
            SensorStateClass.MEASUREMENT,
            None,
            None,
            "blocks"
        ),
        MoneroNodeSensor(
            coordinator, 
            config, 
            "remaining_sync_time", 
            "Remaining Sync Time", 
            "mdi:clock-outline",
            SensorStateClass.MEASUREMENT, 
            SensorDeviceClass.DURATION,
            None,
            None
        ),
        MoneroNodeSensor(
            coordinator, 
            config, 
            "sync_speed", 
            "Sync Speed", 
            "mdi:speedometer",
            SensorStateClass.MEASUREMENT,
            None,
            None,
            "blocks/min"
        ),
        MoneroNodeSensor(
            coordinator, 
            config, 
            "sync_eta", 
            "Sync ETA", 
            "mdi:calendar-clock",
            SensorStateClass.MEASUREMENT,
            None,
            None,
            None
        ),
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
        self._prev_local_height = None
        self._prev_update_time = None
        self._session = None

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            current_time = self.hass.loop.time()
            
            if self._session is None:
                self._session = aiohttp.ClientSession()
                
            headers = {'User-Agent': 'HomeAssistant/MoneroNodeIntegration'}

            try:
                # Fetch global height from the Monero Node API
                async with self._session.get(
                    self.config['global_height_url'], 
                    headers=headers,
                    timeout=10
                ) as response:
                    if response.status != 200:
                        raise ValueError(f"Cannot connect to global height URL. Status code: {response.status}")
                    global_height_data = await response.json()
                    global_height = global_height_data.get('data', {}).get('best_block_height', 0)

                # Fetch local height
                async with self._session.get(
                    self.config['local_height_url'], 
                    headers=headers,
                    timeout=5
                ) as response:
                    if response.status != 200:
                        raise ValueError(f"Cannot connect to local height URL. Status code: {response.status}")
                    local_height_data = await response.json()

                # Fetch Monero price
                async with self._session.get(
                    self.config['price_url'], 
                    headers=headers,
                    timeout=10
                ) as response:
                    if response.status != 200:
                        raise ValueError(f"Cannot connect to price URL. Status code: {response.status}")
                    price_data = await response.json()
            except (asyncio.TimeoutError, aiohttp.ClientError) as err:
                _LOGGER.error(f"Connection error: {err}")
                raise UpdateFailed(f"Connection error: {err}")

            current_local_height = local_height_data.get('height', 0)
            blocks_behind = max(0, global_height - current_local_height)
            
            # Determine sync status
            if blocks_behind == 0:
                sync_status = "Synchronized"
            elif blocks_behind <= 10:
                sync_status = "Almost Synchronized"
            elif blocks_behind <= 100:
                sync_status = "Close to Synchronized"
            elif blocks_behind <= 1000:
                sync_status = "Synchronizing"
            else:
                sync_status = "Syncing (Far Behind)"
            
            data = {
                'global_height': global_height,
                'local_height': current_local_height,
                'blocks_behind': blocks_behind,
                'monero_price': price_data.get('monero', {}).get('usd', 0),
                ATTR_SYNC_STATUS: sync_status,
            }

            # Calculate node sync percentage
            data['node_sync_percentage'] = round(
                (data['local_height'] / data['global_height']) * 100
                if data['global_height'] > 0 else 0, 2
            )
            
            # Calculate sync speed and remaining time
            sync_speed = None
            remaining_sync_time = None
            sync_eta = None
            
            if self._prev_local_height is not None and self._prev_update_time is not None:
                # Calculate blocks per second
                time_diff = current_time - self._prev_update_time
                blocks_diff = current_local_height - self._prev_local_height
                
                if time_diff > 0:
                    blocks_per_second = blocks_diff / time_diff
                    blocks_per_minute = blocks_per_second * 60
                    sync_speed = round(blocks_per_minute, 2)
                    
                    if blocks_per_second > 0 and blocks_behind > 0:
                        remaining_seconds = blocks_behind / blocks_per_second
                        
                        # Store raw seconds for proper device class usage
                        remaining_sync_time = int(remaining_seconds)
                        
                        # Calculer la date et l'heure estimées de fin de synchronisation
                        if remaining_sync_time > 0:
                            eta_datetime = datetime.now() + timedelta(seconds=remaining_sync_time)
                            
                            # Formater l'ETA en fonction du temps restant
                            if remaining_sync_time < 3600:  # Moins d'une heure
                                minutes_left = remaining_sync_time // 60
                                sync_eta = f"{minutes_left} minutes ({eta_datetime.strftime('%H:%M')})"
                            elif remaining_sync_time < 86400:  # Moins d'un jour
                                hours_left = remaining_sync_time // 3600
                                sync_eta = f"{hours_left} heures ({eta_datetime.strftime('%H:%M le %d/%m')})"
                            else:  # Plus d'un jour
                                days_left = remaining_sync_time // 86400
                                sync_eta = f"{days_left} jours ({eta_datetime.strftime('%d/%m/%Y')})"
            
            # Update previous values for next calculation
            self._prev_local_height = current_local_height
            self._prev_update_time = current_time
            
            data['remaining_sync_time'] = remaining_sync_time
            data['sync_speed'] = sync_speed if sync_speed is not None else 0
            data['sync_eta'] = sync_eta

            return data

        except Exception as err:
            _LOGGER.error(f"Error fetching Monero Node data: {err}")
            raise UpdateFailed(f"Error fetching Monero Node data: {err}")
    
    async def async_shutdown(self):
        """Close open client session."""
        if self._session:
            await self._session.close()
            self._session = None


class MoneroNodeSensor(CoordinatorEntity, SensorEntity):
    """Monero Node Sensor class."""

    def __init__(self, coordinator, config, sensor_type, name, icon, 
                 state_class, device_class, suggested_display_precision, unit):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config = config
        self._type = sensor_type
        self._attr_name = f"Monero Node {name}"
        self._attr_icon = icon
        self._attr_unique_id = f"{DOMAIN}_{config['entry_id']}_{sensor_type}"
        self._attr_state_class = state_class
        self._attr_device_class = device_class
        self._attr_suggested_display_precision = suggested_display_precision
        self._attr_native_unit_of_measurement = unit
        
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, config['entry_id'])},
            manufacturer="Monero",
            name=f"Monero Node {config.get('name', 'Default')}",
            model="XMR Node",
            sw_version=f"v{coordinator.config.get('monerod_version', 'Unknown')}",
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._type)
        
    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if self._type in ["node_sync_percentage", "remaining_sync_time", "local_height", "sync_eta"]:
            return {
                ATTR_SYNC_STATUS: self.coordinator.data.get(ATTR_SYNC_STATUS),
                ATTR_BLOCKS_BEHIND: self.coordinator.data.get("blocks_behind")
            }
        return None