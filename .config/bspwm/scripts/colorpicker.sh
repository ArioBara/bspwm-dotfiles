#!/usr/bin/env bash

TMP_IMG="/tmp/colorpick.png"
rm -f "$TMP_IMG"

# Capture pixel / area with maim
maim -s -u "$TMP_IMG" 2>/dev/null

if [ -f "$TMP_IMG" ]; then
    HEX=$(python3 -c '
from PIL import Image
try:
    im = Image.open("/tmp/colorpick.png")
    w, h = im.size
    rgb = im.getpixel((w // 2, h // 2))
    if isinstance(rgb, int):
        print(f"#{rgb:02x}{rgb:02x}{rgb:02x}")
    else:
        print(f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}")
except Exception:
    pass
')
    rm -f "$TMP_IMG"
    if [ -n "$HEX" ]; then
        echo -n "$HEX" | xclip -selection clipboard
        echo -n "$HEX" | xclip -selection primary
        dunstify -a "Color Picker" -r 9996 "󰈊 Color Picker" "Kode HEX: <b>$HEX</b>\nBerhasil disalin ke clipboard!"
    fi
fi
