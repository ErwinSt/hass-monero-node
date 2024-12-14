# Monero Node Integration for Home Assistant

Monitor your Monero node's synchronization status and fetch blockchain statistics directly in Home Assistant.  

## Features  
- **Synchronization Status**: See the sync percentage of your local Monero node.  
- **Blockchain Stats**: Get global stats like hashrate, difficulty, and last reward.  
- **XMR Price**: Display the current price of Monero (USD).  
- **Configurable APIs**: Set your local node and global stats APIs directly via the Home Assistant UI.  

## Installation  

1. Clone the repository into your Home Assistant `custom_components` folder:  
   ```bash
   git clone https://github.com/yourusername/hass-monero-node.git custom_components/monero_node