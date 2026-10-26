#!/usr/bin/env bash

# ==============================================================================
#  BSPWM SMART WINDOW CLOSER
# ==============================================================================
# Menutup jendela secara aman dan andal, termasuk aplikasi Electron (VS Code,
# Discord, Spotify, dll.) yang sering mengabaikan WM_DELETE_WINDOW standar bspc.

WIN_ID=$(bspc query -N -n focused 2>/dev/null)
if [ -z "$WIN_ID" ]; then
    WIN_ID=$(xdotool getactivewindow 2>/dev/null)
fi

[ -z "$WIN_ID" ] && exit 0

# Coba cara standar bspc terlebih dahulu
bspc node "$WIN_ID" -c 2>/dev/null

# Tunggu sesaat dan periksa apakah jendela masih ada
sleep 0.12
if bspc query -N -n "$WIN_ID" >/dev/null 2>&1; then
    # Fallback menggunakan xdotool windowclose yang efektif untuk VS Code & Electron
    xdotool windowclose "$WIN_ID" 2>/dev/null || bspc node "$WIN_ID" -k 2>/dev/null
fi
