#!/usr/bin/env bash

get_volume() {
    if command -v pamixer &>/dev/null; then
        pamixer --get-volume
    else
        pactl get-sink-volume @DEFAULT_SINK@ | grep -Po '\d+(?=%)' | head -n 1
    fi
}

is_mute() {
    if command -v pamixer &>/dev/null; then
        pamixer --get-mute
    else
        pactl get-sink-mute @DEFAULT_SINK@ | grep -q "yes" && echo "true" || echo "false"
    fi
}

send_notification() {
    vol=$(get_volume)
    mute=$(is_mute)
    if [ "$mute" = "true" ]; then
        dunstify -a "Volume" -r 9993 -u low -i "audio-volume-muted" "Muted"
    else
        dunstify -a "Volume" -r 9993 -u low -h int:value:"$vol" -i "audio-volume-high" "Volume: $vol%"
    fi
}

case "$1" in
    up)
        if command -v pamixer &>/dev/null; then
            pamixer -u -i 5
        else
            pactl set-sink-mute @DEFAULT_SINK@ 0
            pactl set-sink-volume @DEFAULT_SINK@ +5%
        fi
        send_notification
        ;;
    down)
        if command -v pamixer &>/dev/null; then
            pamixer -u -d 5
        else
            pactl set-sink-mute @DEFAULT_SINK@ 0
            pactl set-sink-volume @DEFAULT_SINK@ -5%
        fi
        send_notification
        ;;
    mute)
        if command -v pamixer &>/dev/null; then
            pamixer -t
        else
            pactl set-sink-mute @DEFAULT_SINK@ toggle
        fi
        send_notification
        ;;
esac
