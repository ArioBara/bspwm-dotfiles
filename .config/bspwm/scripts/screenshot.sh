#!/usr/bin/env bash

SHOT_DIR="$HOME/Pictures/Screenshots"
mkdir -p "$SHOT_DIR"
FILE="$SHOT_DIR/screenshot_$(date +'%Y%m%d_%H%M%S').png"

case "$1" in
    full)
        if command -v flameshot &>/dev/null; then
            flameshot full -p "$SHOT_DIR" -c
            exit 0
        elif command -v maim &>/dev/null; then
            maim "$FILE"
        elif command -v scrot &>/dev/null; then
            scrot "$FILE"
        fi
        ;;
    select|*)
        if command -v flameshot &>/dev/null; then
            flameshot gui
            exit 0
        fi

        # Fallback if flameshot not yet installed
        sleep 0.2
        if command -v maim &>/dev/null; then
            maim -s -u "$FILE" 2>/dev/null
        elif command -v scrot &>/dev/null; then
            scrot -s "$FILE" 2>/dev/null
        fi
        ;;
esac

if [ -f "$FILE" ] && [ -s "$FILE" ]; then
    if command -v xclip &>/dev/null; then
        xclip -selection clipboard -t image/png -i "$FILE"
    fi
    dunstify -a "Screenshot" -r 9995 -i "$FILE" "Screenshot Saved" "$FILE"
fi
