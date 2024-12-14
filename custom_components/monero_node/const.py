DOMAIN = "monero_node"
DEFAULT_NAME = "Monero Node"

# URLs par défaut
DEFAULT_LOCAL_API = "http://127.0.0.1:18081/json_rpc"
DEFAULT_GLOBAL_API = "https://localmonero.co/blocks/api/get_stats"
DEFAULT_COIN_API = "https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd"

# Fréquence de mise à jour par défaut (en secondes)
DEFAULT_SCAN_INTERVAL = 300

CONF_LOCAL_API = "local_api"
CONF_GLOBAL_API = "global_api"
CONF_COIN_API = "coin_api"