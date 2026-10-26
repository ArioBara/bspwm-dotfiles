#!/usr/bin/env bash

# ==============================================================================
#  KEYBOARD RGB BACKLIGHT CONTROL SCRIPT (SCROLL LOCK)
# ==============================================================================
# Mengontrol lampu latar / RGB keyboard yang terhubung ke jalur Scroll Lock LED.
# Mendukung X11 xset, brightnessctl, dan xmodmap untuk mengaktifkan tombol fisik.

is_on() {
    xset q 2>/dev/null | grep -E "Scroll Lock:[ ]*on" >/dev/null 2>&1
}

send_notification() {
    local state="$1"
    if command -v dunstify &>/dev/null; then
        if [ "$state" = "on" ]; then
            dunstify -a "Keyboard RGB" -r 9996 -u low -i "input-keyboard" "󰌌 Keyboard Backlight" "RGB Menyala (ON)"
        else
            dunstify -a "Keyboard RGB" -r 9996 -u low -i "input-keyboard" "󰌌 Keyboard Backlight" "RGB Mati (OFF)"
        fi
    elif command -v notify-send &>/dev/null; then
        if [ "$state" = "on" ]; then
            notify-send -u low -i "input-keyboard" "Keyboard Backlight" "RGB Menyala (ON)"
        else
            notify-send -u low -i "input-keyboard" "Keyboard Backlight" "RGB Mati (OFF)"
        fi
    fi
}

turn_on() {
    xset led 3 2>/dev/null
    xset led named "Scroll Lock" 2>/dev/null
    send_notification "on"
    echo "Keyboard RGB: ON"
}

turn_off() {
    xset -led 3 2>/dev/null
    xset -led named "Scroll Lock" 2>/dev/null
    send_notification "off"
    echo "Keyboard RGB: OFF"
}

toggle() {
    if is_on; then
        turn_off
    else
        turn_on
    fi
}

status() {
    if is_on; then
        echo "on"
    else
        echo "off"
    fi
}

case "$1" in
    on|enable)
        turn_on
        ;;
    off|disable)
        turn_off
        ;;
    toggle)
        toggle
        ;;
    status)
        status
        ;;
    *)
        toggle
        ;;
esac
