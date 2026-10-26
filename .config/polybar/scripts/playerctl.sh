#!/usr/bin/env bash

# ==============================================================================
#  POLYBAR PLAYERCTL MODULE - AUTO-DETECT & CONTROL ACTIVE MEDIA
# ==============================================================================

ACTIVE_PLAYER_FILE="/tmp/.active_media_player"

# 1. Handle Click & Scroll Actions directly on the active player
if [ -n "$1" ]; then
    action="$1"
    target_player=""
    if [ -f "$ACTIVE_PLAYER_FILE" ]; then
        target_player=$(cat "$ACTIVE_PLAYER_FILE" 2>/dev/null)
    fi

    # Verify if target player is still running
    if [ -n "$target_player" ] && playerctl -l 2>/dev/null | grep -q "^$target_player$"; then
        P_ARG="-p $target_player"
    else
        P_ARG=""
    fi

    case "$action" in
        play-pause)
            playerctl $P_ARG play-pause 2>/dev/null || playerctl play-pause 2>/dev/null
            ;;
        next)
            playerctl $P_ARG next 2>/dev/null || playerctl next 2>/dev/null
            ;;
        previous)
            playerctl $P_ARG previous 2>/dev/null || playerctl previous 2>/dev/null
            ;;
        vol-up)
            playerctl $P_ARG volume 0.05+ 2>/dev/null || playerctl volume 0.05+ 2>/dev/null
            ;;
        vol-down)
            playerctl $P_ARG volume 0.05- 2>/dev/null || playerctl volume 0.05- 2>/dev/null
            ;;
    esac
    exit 0
fi

# 2. Get list of all available media players
players=$(playerctl -l 2>/dev/null)

if [ -z "$players" ]; then
    echo "󰝚 No Media"
    rm -f "$ACTIVE_PLAYER_FILE" 2>/dev/null
    exit 0
fi

selected_player=""
selected_status=""

# Step A: Priority 1 - Find any player that is actively "Playing"
for p in $players; do
    st=$(playerctl -p "$p" status 2>/dev/null)
    if [ "$st" = "Playing" ]; then
        selected_player="$p"
        selected_status="Playing"
        break
    fi
done

# Step B: Priority 2 - If none is playing, find any player that is "Paused"
if [ -z "$selected_player" ]; then
    for p in $players; do
        st=$(playerctl -p "$p" status 2>/dev/null)
        if [ "$st" = "Paused" ]; then
            selected_player="$p"
            selected_status="Paused"
            break
        fi
    done
fi

# If no player is actively Playing or Paused
if [ -z "$selected_player" ]; then
    echo "󰝚 No Media"
    rm -f "$ACTIVE_PLAYER_FILE" 2>/dev/null
    exit 0
fi

# Save selected player for click actions
echo "$selected_player" > "$ACTIVE_PLAYER_FILE"

# Extract metadata for the selected player
artist=$(playerctl -p "$selected_player" metadata artist 2>/dev/null)
title=$(playerctl -p "$selected_player" metadata title 2>/dev/null)

# Format display text
if [ -n "$artist" ] && [ -n "$title" ]; then
    text="$artist - $title"
elif [ -n "$title" ]; then
    text="$title"
elif [ -n "$artist" ]; then
    text="$artist"
else
    # Fallback to readable player name
    clean_p="${selected_player%%.*}"
    text="${clean_p^}"
fi

# Truncate if too long
if [ ${#text} -gt 35 ]; then
    text="$(echo "$text" | cut -c 1-32)..."
fi

if [ "$selected_status" = "Playing" ]; then
    echo "󰎆 $text"
else
    echo "󰏤 $text (Paused)"
fi
