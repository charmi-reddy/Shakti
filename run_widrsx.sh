#!/bin/bash

WIFI_IFACE="wlan1"

set_monitor_mode() {
    echo "[*] Setting $WIFI_IFACE to monitor mode..."
    sudo ifconfig $WIFI_IFACE down
    sudo iwconfig $WIFI_IFACE mode monitor
    sudo ifconfig $WIFI_IFACE up
}

set_managed_mode() {
    echo "[*] Reverting $WIFI_IFACE to managed mode..."
    sudo ifconfig $WIFI_IFACE down
    sudo iwconfig $WIFI_IFACE mode managed
    sudo ifconfig $WIFI_IFACE up
}

trap set_managed_mode EXIT

set_monitor_mode

echo "[*] Building Rust firewall TCP server..."
(cd firewall && cargo build --release)

echo "[*] Starting Rust firewall TCP server..."
(cd firewall && ./target/release/widrsx-backend &)  # Background

echo "[*] Starting Flask API server..."
python3 api_server.py &  # Background

echo "[*] Starting Wi-Fi sniffer..."
sudo venv/bin/python3 main.py &  # Background

echo "[*] All services started. Press Ctrl+C to stop everything."
wait