#!/usr/bin/env bash

get_brightness() {
    if command -v brightnessctl &>/dev/null; then
        brightnessctl -m | cut -d, -f4 | tr -d '%'
    else
        echo "50"
    fi
}

send_notification() {
    bright=$(get_brightness)
    dunstify -a "Brightness" -r 9994 -u low -h int:value:"$bright" -i "display-brightness" "Brightness: $bright%"
}

case "$1" in
    up)
        brightnessctl set +5% >/dev/null 2>&1
        send_notification
        ;;
    down)
        brightnessctl set 5%- >/dev/null 2>&1
        send_notification
        ;;
esac
