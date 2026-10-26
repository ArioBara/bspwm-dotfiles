#!/usr/bin/env bash

ACTIVE_PLAYER_FILE="/tmp/.active_media_player"
target_player=""
if [ -f "$ACTIVE_PLAYER_FILE" ]; then
    target_player=$(cat "$ACTIVE_PLAYER_FILE" 2>/dev/null)
fi

if [ -n "$target_player" ] && playerctl -l 2>/dev/null | grep -q "^$target_player$"; then
    P_ARG="-p $target_player"
else
    P_ARG=""
fi

send_notification() {
    status=$(playerctl $P_ARG status 2>/dev/null || playerctl status 2>/dev/null)
    artist=$(playerctl $P_ARG metadata artist 2>/dev/null || playerctl metadata artist 2>/dev/null)
    title=$(playerctl $P_ARG metadata title 2>/dev/null || playerctl metadata title 2>/dev/null)
    
    if [ -n "$title" ]; then
        dunstify -a "Media Player" -r 9992 -u low -i "media-playback-start" "$title" "$artist ($status)"
    fi
}

case "$1" in
    play-pause)
        playerctl $P_ARG play-pause 2>/dev/null || playerctl play-pause 2>/dev/null
        send_notification
        ;;
    next)
        playerctl $P_ARG next 2>/dev/null || playerctl next 2>/dev/null
        sleep 0.2
        send_notification
        ;;
    prev)
        playerctl $P_ARG previous 2>/dev/null || playerctl previous 2>/dev/null
        sleep 0.2
        send_notification
        ;;
esac
