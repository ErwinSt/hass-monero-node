"""Constants for the Monero Node integration."""

DOMAIN = "monero_node"

# Attribute names
ATTR_SYNC_STATUS = "sync_status"
ATTR_BLOCKS_BEHIND = "blocks_behind"

# Default values
DEFAULT_REFRESH_INTERVAL = 60  # seconds
DEFAULT_NAME = "Monero Node"
DEFAULT_GLOBAL_HEIGHT_URL = "https://api.blockchair.com/monero/stats"
DEFAULT_LOCAL_HEIGHT_URL = "http://localhost:18089/get_height"
DEFAULT_PRICE_URL = "https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd"

# Config keys
CONF_GLOBAL_HEIGHT_URL = "global_height_url"
CONF_LOCAL_HEIGHT_URL = "local_height_url"
CONF_PRICE_URL = "price_url"
CONF_REFRESH_INTERVAL = "refresh_interval"