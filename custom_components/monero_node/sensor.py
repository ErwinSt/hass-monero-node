import requests
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, CONF_LOCAL_API, CONF_GLOBAL_API, CONF_COIN_API

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Monero Node sensors based on a config entry."""
    config = config_entry.data

    local_api = config.get(CONF_LOCAL_API)
    global_api = config.get(CONF_GLOBAL_API)
    coin_api = config.get(CONF_COIN_API)

    name = "Monero Node"

    async_add_entities([
        MoneroNodeSyncSensor(name, local_api, global_api),
        MoneroNodeHeightSensor(name, local_api, "local_height"),
        MoneroNodeHeightSensor(name, global_api, "global_height"),
        MoneroPriceSensor(f"{name} Price", coin_api),
    ])

class MoneroNodeSyncSensor(SensorEntity):
    def __init__(self, name, local_api, global_api):
        self._name = f"{name} Sync Percentage"
        self._state = None
        self._attributes = {}
        self.local_api = local_api
        self.global_api = global_api
        self._attr_unique_id = f"monero_sync_{name.replace(' ', '_').lower()}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, name.replace(" ", "_").lower())},
            "name": name,
            "manufacturer": "Monero",
            "model": "Node",
        }

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update(self):
        try:
            local_data = requests.get(self.local_api).json()
            global_data = requests.get(self.global_api).json()

            local_height = local_data.get("height")
            global_height = global_data.get("height")

            if local_height and global_height:
                self._state = round((local_height / global_height) * 100, 2)

            self._attributes = {
                "local_height": local_height,
                "global_height": global_height,
                "hashrate": global_data.get("hashrate"),
                "difficulty": global_data.get("difficulty"),
                "last_reward": global_data.get("last_reward"),
            }
        except Exception as e:
            self._state = None
            self._attributes = {"error": str(e)}

class MoneroNodeHeightSensor(SensorEntity):
    def __init__(self, name, api_url, height_type):
        self._name = f"{name} {height_type.replace('_', ' ').title()}"
        self.api_url = api_url
        self.height_type = height_type
        self._state = None
        self._attr_unique_id = f"monero_{height_type}_{name.replace(' ', '_').lower()}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, name.replace(" ", "_").lower())},
            "name": name,
            "manufacturer": "Monero",
            "model": "Node",
        }

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    def update(self):
        try:
            data = requests.get(self.api_url).json()
            self._state = data.get("height")
        except Exception as e:
            self._state = None

class MoneroPriceSensor(SensorEntity):
    def __init__(self, name, coin_api):
        self._name = name
        self._state = None
        self._attributes = {}
        self.coin_api = coin_api
        self._attr_unique_id = f"monero_price_{name.replace(' ', '_').lower()}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "monero_price")},
            "name": "Monero Price",
            "manufacturer": "Monero",
            "model": "Coin Price",
        }

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update(self):
        try:
            coin_data = requests.get(self.coin_api).json()
            self._state = coin_data["monero"]["usd"]
            self._attributes = {"currency": "USD"}
        except Exception as e:
            self._state = None
            self._attributes = {"error": str(e)}