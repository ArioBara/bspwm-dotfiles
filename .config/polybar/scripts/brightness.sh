#!/usr/bin/env bash

# Check for physical backlight device
BL_DEV=$(ls /sys/class/backlight 2>/dev/null | head -n 1)

get_software_brightness() {
    local mon=$(xrandr | grep " connected" | head -n 1 | awk '{print $1}')
    local br=$(xrandr --verbose | grep -i "brightness:" | head -n 1 | awk '{print $2}')
    if [ -z "$br" ]; then br="1.0"; fi
    # Convert float to percentage int
    awk -v b="$br" 'BEGIN { printf "%.0f", b * 100 }'
}

set_software_brightness() {
    local action="$1"
    local mon=$(xrandr | grep " connected" | head -n 1 | awk '{print $1}')
    local current=$(get_software_brightness)
    local target=$current

    if [ "$action" = "up" ]; then
        target=$(( current + 5 ))
        if [ $target -gt 100 ]; then target=100; fi
    elif [ "$action" = "down" ]; then
        target=$(( current - 5 ))
        if [ $target -lt 20 ]; then target=20; fi
    fi

    local float_val=$(awk -v t="$target" 'BEGIN { printf "%.2f", t / 100 }')
    xrandr --output "$mon" --brightness "$float_val"
}

case "$1" in
    up)
        if [ -n "$BL_DEV" ]; then
            brightnessctl set +5% >/dev/null 2>&1
        else
            set_software_brightness up
        fi
        ;;
    down)
        if [ -n "$BL_DEV" ]; then
            brightnessctl set 5%- >/dev/null 2>&1
        else
            set_software_brightness down
        fi
        ;;
    max)
        if [ -n "$BL_DEV" ]; then
            brightnessctl set 100% >/dev/null 2>&1
        else
            local mon=$(xrandr | grep " connected" | head -n 1 | awk '{print $1}')
            xrandr --output "$mon" --brightness 1.0
        fi
        ;;
    min)
        if [ -n "$BL_DEV" ]; then
            brightnessctl set 20% >/dev/null 2>&1
        else
            local mon=$(xrandr | grep " connected" | head -n 1 | awk '{print $1}')
            xrandr --output "$mon" --brightness 0.20
        fi
        ;;
    *)
        # Output current brightness for Polybar
        if [ -n "$BL_DEV" ]; then
            pct=$(brightnessctl -m | awk -F, '{print $4}' | tr -d '%')
        else
            pct=$(get_software_brightness)
        fi

        if [ "$pct" -ge 80 ]; then
            icon="󰃠"
        elif [ "$pct" -ge 50 ]; then
            icon="󰃟"
        elif [ "$pct" -ge 20 ]; then
            icon="󰃝"
        else
            icon="󰃞"
        fi

        echo "$icon $pct%"
        ;;
esac
