# Monero Node Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

## Description

This integration allows you to monitor the status of your Monero node directly within **Home Assistant**. With this integration, you can track key metrics like **Global Block Height**, **Local Block Height**, **Monero Price**, and **Node Sync Percentage** to keep an eye on your Monero node's health and performance.

Whether you are a Monero enthusiast or just a cryptocurrency fan, this integration makes it easy to get important stats in your smart home setup.

## Features

- **Global Block Height**: Monitors the current block height of the entire Monero network.
- **Local Block Height**: Tracks your node's current block height.
- **Monero Price**: Displays the current USD price of Monero (XMR).
- **Node Sync Percentage**: Shows how much of your node's blockchain is synchronized with the global network.

## Installation

1. **Install via HACS (Home Assistant Community Store):**

   If you are using **HACS**, follow these steps:
   - Go to **HACS** > **Integrations** > click on the **three dots** menu in the top right corner and choose **Custom repositories**.
   - Add the repository URL: `https://github.com/ErwinSt/hass-monero-node`.
   - Select **Integration** as the category.
   - Once added, you can search for **Monero Node Integration** in the **HACS** store, click **Install**, and restart Home Assistant.


## Configuration

To set up the **Monero Node Integration**, you will need to enter the following configuration in Home Assistant.

1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration** and search for **Monero Node**.
3. Enter the necessary configuration details (URLs for global height, local height, and price).
4. Restart Home Assistant to apply the changes.
