#!/usr/bin/env bash

# Power menu options with modern nerd font icons
shutdown="󰐥"
reboot="󰜉"
lock="󰌾"
suspend="󰤄"
logout="󰍃"

# Prompt
uptime=$(uptime -p | sed -e 's/up //g')
prompt="System ($uptime)"

options="$shutdown\n$reboot\n$lock\n$suspend\n$logout"

chosen="$(echo -e "$options" | rofi -dmenu -m -1 -theme "$HOME/.config/rofi/powermenu.rasi" -p "$prompt")"

case "$chosen" in
    "$shutdown")
        systemctl poweroff || sudo poweroff
        ;;
    "$reboot")
        systemctl reboot || sudo reboot
        ;;
    "$lock")
        if command -v cinnamon-screensaver-command &>/dev/null && [ "$XDG_CURRENT_DESKTOP" = "X-Cinnamon" ]; then
            cinnamon-screensaver-command -l
        elif command -v xflock4 &>/dev/null; then
            xflock4
        elif command -v betterlockscreen &>/dev/null; then
            betterlockscreen -l
        elif command -v loginctl &>/dev/null; then
            loginctl lock-session
        fi
        ;;
    "$suspend")
        systemctl suspend
        ;;
    "$logout")
        if [ "$XDG_CURRENT_DESKTOP" = "X-Cinnamon" ]; then
            cinnamon-session-quit --logout --no-prompt
        else
            bspc quit
        fi
        ;;
esac
