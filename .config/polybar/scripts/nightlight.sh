#!/usr/bin/env bash

# ==============================================================================
#  NIGHT LIGHT / BLUE LIGHT FILTER SCRIPT (XRANDR)
# ==============================================================================

STATE_FILE="/tmp/.nightlight_active"
MON=$(xrandr --query | grep " connected" | head -n 1 | awk '{print $1}')

case "$1" in
    on)
        for m in $(xrandr --query | grep " connected" | awk '{print $1}'); do
            xrandr --output "$m" --gamma 1.0:0.82:0.65
        done
        touch "$STATE_FILE"
        dunstify -a "Night Light" -r 9997 "󰛩 Mode Malam" "Filter cahaya biru aktif (4500K)"
        ;;
    off)
        for m in $(xrandr --query | grep " connected" | awk '{print $1}'); do
            xrandr --output "$m" --gamma 1.0:1.0:1.0
        done
        rm -f "$STATE_FILE"
        dunstify -a "Night Light" -r 9997 "󰛨 Mode Siang / Normal" "Temperatur warna kembali normal (6500K)"
        ;;
    toggle|*)
        if [ -f "$STATE_FILE" ]; then
            "$0" off
        else
            "$0" on
        fi
        ;;
esac
