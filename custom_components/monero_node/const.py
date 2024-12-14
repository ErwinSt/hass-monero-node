DOMAIN = "monero_node"

CONF_LOCAL_API = "local_api"
CONF_GLOBAL_API = "global_api"
CONF_COIN_API = "coin_api"
CONF_NAME = "name"
CONF_REFRESH_INTERVAL = "refresh_interval"

DEFAULT_NAME = "Monero Node"
DEFAULT_LOCAL_API = "http://IP:18089/get_height"
DEFAULT_GLOBAL_API = "https://monero.network/global_stats"
DEFAULT_COIN_API = "https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd"
DEFAULT_REFRESH_INTERVAL = 300  # in seconds