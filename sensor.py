import requests
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, CONF_LOCAL_API, CONF_GLOBAL_API, CONF_COIN_API

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Monero Node sensors based on a config entry."""
    config = config_entry.data

    local_api = config.get(CONF_LOCAL_API)
    global_api = config.get(CONF_GLOBAL_API)
    coin_api = config.get(CONF_COIN_API)

    async_add_entities([
        MoneroNodeSyncSensor("Monero Node Sync", local_api, global_api),
        MoneroPriceSensor("Monero Price", coin_api),
    ])

class MoneroNodeSyncSensor(SensorEntity):
    def __init__(self, name, local_api, global_api):
        self._name = name
        self._state = None
        self._attributes = {}
        self.local_api = local_api
        self.global_api = global_api

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

class MoneroPriceSensor(SensorEntity):
    def __init__(self, name, coin_api):
        self._name = name
        self._state = None
        self._attributes = {}
        self.coin_api = coin_api

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