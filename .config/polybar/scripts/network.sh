#!/usr/bin/env bash

# Find active wireless and wired interfaces
WLAN=$(ip -br link | grep -iE 'wl' | awk '{print $1}' | head -n 1)
ETH=$(ip -br link | grep -iE 'en|eth' | awk '{print $1}' | head -n 1)

if [ -n "$WLAN" ] && [ "$(cat /sys/class/net/$WLAN/operstate 2>/dev/null)" = "up" ]; then
    SSID=$(iwgetid -r 2>/dev/null || iw dev "$WLAN" link 2>/dev/null | grep SSID | awk '{print $2}')
    if [ -z "$SSID" ]; then SSID="WiFi"; fi
    echo "󰤨 $SSID"
elif [ -n "$ETH" ] && [ "$(cat /sys/class/net/$ETH/operstate 2>/dev/null)" = "up" ]; then
    echo "󰈀 Ethernet"
else
    # Fallback check default route
    if ip route | grep -q default; then
        echo "󰤨 Connected"
    else
        echo "󰤭 Offline"
    fi
fi
