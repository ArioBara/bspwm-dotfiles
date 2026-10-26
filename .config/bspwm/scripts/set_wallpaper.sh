#!/usr/bin/env bash

WALL_DIR="$HOME/.config/bspwm/wallpapers"

if [ -n "$1" ] && [ -f "$1" ]; then
    WALL="$1"
elif [ -n "$1" ] && [ -f "$WALL_DIR/$1" ]; then
    WALL="$WALL_DIR/$1"
elif [ -n "$1" ] && [ "$1" != "random" ] && find "$WALL_DIR" -maxdepth 1 -type f -iname "*$1*" | grep -q .; then
    WALL=$(find "$WALL_DIR" -maxdepth 1 -type f -iname "*$1*" | head -n 1)
elif [ "$1" = "random" ]; then
    WALL=$(find "$WALL_DIR" -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) | shuf -n 1)
elif [ -f "$HOME/.current_wallpaper" ] && [ -s "$HOME/.current_wallpaper" ] && [ -f "$(cat "$HOME/.current_wallpaper")" ]; then
    WALL=$(cat "$HOME/.current_wallpaper")
else
    WALL=$(find "$WALL_DIR" -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) | head -n 1)
fi

if [ -n "$WALL" ]; then
    feh --bg-fill "$WALL" 2>/dev/null || true
    echo "$WALL" > "$HOME/.current_wallpaper"
fi
