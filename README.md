# Monero Node Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)
![HA Compatibility](https://img.shields.io/badge/Home%20Assistant-2023.10.0+-brightgreen)

## Description

Monitor your Monero node directly within Home Assistant! This integration tracks key metrics like network height, node synchronization status, XMR price, and more to help you keep an eye on your Monero node's health and performance.

![Monero Dashboard](https://raw.githubusercontent.com/ErwinSt/hass-monero-node/main/images/dashboard_example.png)

## Features

- **Global Block Height**: Monitors the current block height of the entire Monero network
- **Local Block Height**: Tracks your node's current block height
- **Blocks Behind**: Shows how many blocks your node is behind the network
- **Monero Price**: Displays the current USD price of Monero (XMR)
- **Node Sync Percentage**: Shows how much of your node's blockchain is synchronized
- **Sync Speed**: Displays how quickly your node is syncing (blocks/minute)
- **Remaining Sync Time**: Estimates time left until full synchronization
- **Sync Status**: Human-readable synchronization status

## Installation

### HACS Installation (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Go to **HACS** > **Integrations** > click the **⋮** menu in the top right
3. Choose **Custom repositories**
4. Add `https://github.com/ErwinSt/hass-monero-node` with category **Integration**
5. Click **Monero Node Integration** in the HACS store
6. Click **Install**
7. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Extract the folder `custom_components/monero_node` into your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration** and search for **Monero Node**
3. Enter the configuration details:
   - **Global Height URL**: API endpoint for network height (default: Blockchair API)
   - **Local Height URL**: API endpoint for your node's height
   - **Price URL**: API endpoint for Monero price (default: CoinGecko API) 
   - **Refresh Interval**: How often to update data (in seconds)
4. Click **Submit**

## Lovelace Dashboard

Add a beautiful Monero dashboard to your Home Assistant with this example configuration:

```yaml
title: Monero Node Dashboard
views:
  - title: Monero Node
    path: monero
    badges: []
    cards:
      - type: gauge
        entity: sensor.monero_node_node_sync_percentage
        name: Node Synchronization
        min: 0
        max: 100
        severity:
          green: 99
          yellow: 90
          red: 0
      
      - type: entities
        title: Node Status
        entities:
          - entity: sensor.monero_node_global_height
          - entity: sensor.monero_node_local_height
          - entity: sensor.monero_node_blocks_behind
          - entity: sensor.monero_node_sync_speed
          - entity: sensor.monero_node_remaining_sync_time
      
      - type: history-graph
        title: Node Synchronization History
        hours_to_show: 24
        entities:
          - entity: sensor.monero_node_node_sync_percentage
```

## Available Sensors

| Sensor | Description | Unit |
|--------|-------------|------|
| `sensor.monero_node_global_height` | Current network block height | blocks |
| `sensor.monero_node_local_height` | Your node's current block height | blocks |
| `sensor.monero_node_blocks_behind` | Number of blocks your node is behind | blocks |
| `sensor.monero_node_node_sync_percentage` | Synchronization percentage | % |
| `sensor.monero_node_sync_speed` | How fast your node is syncing | blocks/min |
| `sensor.monero_node_remaining_sync_time` | Estimated time to complete sync | time |
| `sensor.monero_node_monero_price` | Current Monero price | USD |

## Configuration for Advanced Users

### Running behind a proxy/nginx

If your node is running behind a proxy, make sure to:

1. Enable the RPC interface in `monerod` with:
   ```
   --rpc-bind-ip=0.0.0.0 --rpc-bind-port=18089 --restricted-rpc
   ```
2. Configure your proxy to forward traffic to port 18089

### Using with Remote Nodes

You can also configure this integration to monitor remote/public nodes by setting the appropriate URL.

## Troubleshooting

- **"Cannot connect to local height URL"**: Ensure your Monero node is running with RPC enabled
- **"Invalid URLs or cannot connect to APIs"**: Check firewall settings and internet connectivity
- **"No data updates"**: Verify that your refresh interval isn't too short causing rate limiting

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.