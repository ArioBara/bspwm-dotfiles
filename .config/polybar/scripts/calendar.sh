#!/usr/bin/env bash

# ==============================================================================
#  CALENDAR POPUP SCRIPT FOR POLYBAR (ZENITY)
# ==============================================================================

# Toggle calendar dialog: if already running, close it and exit
if pgrep -x zenity >/dev/null; then
    killall zenity
    exit 0
fi

# Calendar window dimensions
CAL_W=320
CAL_H=320

# Get current mouse coordinates
eval $(xdotool getmouselocation --shell 2>/dev/null)

# Detect active monitor geometry
MON_FOUND=false

# 1. Try querying via BSPWM
if command -v bspc >/dev/null 2>&1; then
    # If mouse coordinates are available, identify which monitor contains the cursor
    if [ -n "$X" ] && [ -n "$Y" ]; then
        for m in $(bspc query -M --names 2>/dev/null); do
            read -r mx my mw mh <<< $(bspc query -T -m "$m" 2>/dev/null | jq -r '.rectangle | "\(.x) \(.y) \(.width) \(.height)"' 2>/dev/null)
            if [ -n "$mx" ] && (( X >= mx && X < mx + mw && Y >= my && Y < my + mh )); then
                MON_X=$mx
                MON_Y=$my
                MON_W=$mw
                MON_H=$mh
                MON_FOUND=true
                break
            fi
        done
    fi

    # Fallback to focused monitor in bspwm
    if [ "$MON_FOUND" != "true" ]; then
        read -r mx my mw mh <<< $(bspc query -T -m focused 2>/dev/null | jq -r '.rectangle | "\(.x) \(.y) \(.width) \(.height)"' 2>/dev/null)
        if [ -n "$mx" ]; then
            MON_X=$mx
            MON_Y=$my
            MON_W=$mw
            MON_H=$mh
            MON_FOUND=true
        fi
    fi
fi

# 2. Fallback to xrandr if BSPWM query was not possible
if [ "$MON_FOUND" != "true" ] && command -v xrandr >/dev/null 2>&1; then
    while read -r line; do
        if [[ "$line" =~ ([0-9]+)/[0-9]+x([0-9]+)/[0-9]+\+([0-9]+)\+([0-9]+) ]]; then
            mw="${BASH_REMATCH[1]}"
            mh="${BASH_REMATCH[2]}"
            mx="${BASH_REMATCH[3]}"
            my="${BASH_REMATCH[4]}"
            if [ -n "$X" ] && [ -n "$Y" ] && (( X >= mx && X < mx + mw && Y >= my && Y < my + mh )); then
                MON_X=$mx; MON_Y=$my; MON_W=$mw; MON_H=$mh
                MON_FOUND=true
                break
            fi
            f_mx=$mx; f_my=$my; f_mw=$mw; f_mh=$mh
        fi
    done < <(xrandr --listmonitors 2>/dev/null | grep -E "^ [0-9]+:")

    if [ "$MON_FOUND" != "true" ] && [ -n "$f_mw" ]; then
        MON_X=$f_mx; MON_Y=$f_my; MON_W=$f_mw; MON_H=$f_mh
        MON_FOUND=true
    fi
fi

# 3. Ultimate fallback
if [ -z "$MON_W" ]; then
    MON_X=0
    MON_Y=0
    MON_W=1920
    MON_H=1080
fi

# Vertical position: directly below Polybar (bar height 28 + offset-y 6 + padding)
POS_Y=$(( MON_Y + 40 ))

# Horizontal position:
# If mouse clicked on/near the top bar, center popup under click location
if [ -n "$X" ] && [ -n "$Y" ] && (( Y <= MON_Y + 50 && Y >= MON_Y )); then
    POS_X=$(( X - CAL_W / 2 ))
else
    # Otherwise position under the date widget's usual spot on the right side
    POS_X=$(( MON_X + MON_W - CAL_W - 60 ))
fi

# Clamp POS_X within the target monitor bounds with a margin
MIN_X=$(( MON_X + 12 ))
MAX_X=$(( MON_X + MON_W - CAL_W - 12 ))
if (( POS_X > MAX_X )); then
    POS_X=$MAX_X
fi
if (( POS_X < MIN_X )); then
    POS_X=$MIN_X
fi

# Apply one-shot BSPWM rule for precise initial placement
if command -v bspc >/dev/null 2>&1; then
    bspc rule -a Zenity -o state=floating center=off rectangle=${CAL_W}x${CAL_H}+${POS_X}+${POS_Y}
fi

# Launch zenity calendar
zenity --calendar \
    --title="Kalender" \
    --text="Tanggal: $(date '+%A, %d %B %Y')" \
    --day=$(date +%-d) \
    --month=$(date +%-m) \
    --year=$(date +%Y) >/dev/null 2>&1 &

# Ensure precise window placement and focus in case window manager repositions it
(
    for _ in {1..20}; do
        WID=$(xdotool search --onlyvisible --class "zenity" 2>/dev/null | head -n 1)
        if [ -n "$WID" ]; then
            xdotool windowmove "$WID" "$POS_X" "$POS_Y" 2>/dev/null || true
            xdotool windowraise "$WID" 2>/dev/null || true
            break
        fi
        sleep 0.03
    done
) &
