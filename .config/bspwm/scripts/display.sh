#!/usr/bin/env bash

# ==============================================================================
#  BSPWM DISPLAY MANAGER - CATPPUCCIN MOCHA THEME
# ==============================================================================
# Mengatur primary monitor (VGA-1 / eDP-1 / HDMI), dual screen, dan workspace.

CONF_FILE="$HOME/.config/bspwm/display.conf"
ROFI_THEME="$HOME/.config/rofi/controlcenter.rasi"

# Deteksi monitor internal (laptop) dan eksternal
detect_monitors() {
    INTERNAL_MON=$(xrandr --query | grep -E "(eDP|LVDS)[0-9-]* connected" | awk '{print $1}' | head -n1)
    [ -z "$INTERNAL_MON" ] && INTERNAL_MON="eDP-1"

    EXTERNAL_MON=$(xrandr --query | grep " connected" | awk '{print $1}' | grep -v "$INTERNAL_MON" | head -n1)
}

# Reload wallpaper & polybar
reload_desktop() {
    # Update wallpaper di semua layar aktif
    if [ -f "$HOME/.config/bspwm/scripts/set_wallpaper.sh" ]; then
        setsid -f bash "$HOME/.config/bspwm/scripts/set_wallpaper.sh" >/dev/null 2>&1
    fi

    # Restart Polybar untuk mendeteksi monitor baru
    if [ -f "$HOME/.config/polybar/launch.sh" ]; then
        setsid -f bash "$HOME/.config/polybar/launch.sh" >/dev/null 2>&1
    fi
}

# 1. Mode Dual Screen: Monitor Eksternal sebagai Primary
set_vga_primary() {
    detect_monitors
    if [ -z "$EXTERNAL_MON" ]; then
        notify-send -u normal -i video-display "Display" "Monitor eksternal tidak terdeteksi!"
        set_edp_only
        return
    fi

    # VGA-1 sebagai primary (kanan), eDP-1 sebagai secondary (kiri)
    xrandr --output "$EXTERNAL_MON" --primary --auto \
           --output "$INTERNAL_MON" --auto --left-of "$EXTERNAL_MON"

    # Atur workspaces di bspwm (1-6 di setiap monitor)
    bspc monitor "$EXTERNAL_MON" -d 1 2 3 4 5 6
    bspc monitor "$INTERNAL_MON" -d 1 2 3 4 5 6

    # Simpan preferensi
    echo "MODE=\"vga_primary\"" > "$CONF_FILE"
    echo "PRIMARY_MONITOR=\"$EXTERNAL_MON\"" >> "$CONF_FILE"
    echo "SECONDARY_MONITOR=\"$INTERNAL_MON\"" >> "$CONF_FILE"

    reload_desktop
    notify-send -u low -i video-display "Display" "Primary Display: $EXTERNAL_MON (Eksternal)\nSecondary: $INTERNAL_MON (Laptop)"
}

# 2. Mode Dual Screen: Layar Laptop sebagai Primary
set_edp_primary() {
    detect_monitors
    if [ -z "$EXTERNAL_MON" ]; then
        set_edp_only
        return
    fi

    # eDP-1 sebagai primary (kiri), VGA-1 sebagai secondary (kanan)
    xrandr --output "$INTERNAL_MON" --primary --auto \
           --output "$EXTERNAL_MON" --auto --right-of "$INTERNAL_MON"

    # Atur workspaces di bspwm (1-6 di setiap monitor)
    bspc monitor "$INTERNAL_MON" -d 1 2 3 4 5 6
    bspc monitor "$EXTERNAL_MON" -d 1 2 3 4 5 6

    # Simpan preferensi
    echo "MODE=\"edp_primary\"" > "$CONF_FILE"
    echo "PRIMARY_MONITOR=\"$INTERNAL_MON\"" >> "$CONF_FILE"
    echo "SECONDARY_MONITOR=\"$EXTERNAL_MON\"" >> "$CONF_FILE"

    reload_desktop
    notify-send -u low -i video-display "Display" "Primary Display: $INTERNAL_MON (Laptop)\nSecondary: $EXTERNAL_MON (Eksternal)"
}

# 3. Hanya Monitor Eksternal (Layar Laptop Mati)
set_vga_only() {
    detect_monitors
    if [ -z "$EXTERNAL_MON" ]; then
        notify-send -u normal -i video-display "Display" "Monitor eksternal tidak terdeteksi!"
        set_edp_only
        return
    fi

    xrandr --output "$EXTERNAL_MON" --primary --auto \
           --output "$INTERNAL_MON" --off

    bspc monitor "$EXTERNAL_MON" -d 1 2 3 4 5 6

    echo "MODE=\"vga_only\"" > "$CONF_FILE"
    echo "PRIMARY_MONITOR=\"$EXTERNAL_MON\"" >> "$CONF_FILE"

    reload_desktop
    notify-send -u low -i video-display "Display" "Hanya Layar Eksternal ($EXTERNAL_MON) Aktif"
}

# 4. Hanya Layar Laptop (Monitor Eksternal Mati / Tidak Ada)
set_edp_only() {
    detect_monitors
    if [ -n "$EXTERNAL_MON" ]; then
        xrandr --output "$EXTERNAL_MON" --off
    fi

    xrandr --output "$INTERNAL_MON" --primary --auto

    bspc monitor "$INTERNAL_MON" -d 1 2 3 4 5 6

    echo "MODE=\"edp_only\"" > "$CONF_FILE"
    echo "PRIMARY_MONITOR=\"$INTERNAL_MON\"" >> "$CONF_FILE"

    reload_desktop
    notify-send -u low -i video-display "Display" "Hanya Layar Laptop ($INTERNAL_MON) Aktif"
}

# 5. Mirror / Duplicate
set_mirror() {
    detect_monitors
    if [ -z "$EXTERNAL_MON" ]; then
        set_edp_only
        return
    fi

    xrandr --output "$INTERNAL_MON" --primary --auto \
           --output "$EXTERNAL_MON" --auto --same-as "$INTERNAL_MON"

    bspc monitor "$INTERNAL_MON" -d 1 2 3 4 5 6

    echo "MODE=\"mirror\"" > "$CONF_FILE"
    reload_desktop
    notify-send -u low -i video-display "Display" "Mode Mirror Diaktifkan ($INTERNAL_MON = $EXTERNAL_MON)"
}

# 6. Apply saved or auto configuration
apply_config() {
    detect_monitors
    if [ -f "$CONF_FILE" ]; then
        source "$CONF_FILE"
    fi

    if [ -n "$EXTERNAL_MON" ]; then
        case "$MODE" in
            "vga_primary") set_vga_primary ;;
            "edp_primary") set_edp_primary ;;
            "vga_only")    set_vga_only ;;
            "mirror")      set_mirror ;;
            *)             set_vga_primary ;; # Default jika terdeteksi monitor eksternal
        esac
    else
        set_edp_only
    fi
}

# 7. Interactive Rofi Menu
show_menu() {
    detect_monitors
    local ext_label="${EXTERNAL_MON:-Tidak Tersambung}"
    local int_label="$INTERNAL_MON"

    local opt1="󰍹  Set $ext_label sebagai Primary (Dual Screen - Extended)"
    local opt2="󰌢  Set $int_label sebagai Primary (Dual Screen - Extended)"
    local opt3="󰍺  Hanya Monitor Eksternal ($ext_label Saja)"
    local opt4="󰌢  Hanya Layar Laptop ($int_label Saja)"
    local opt5="󰑈  Mirror / Duplikat Layar"
    local opt6="󰑓  Deteksi Otomatis (Auto Detect)"

    local options="$opt1\n$opt2\n$opt3\n$opt4\n$opt5\n$opt6"
    local chosen=$(echo -e "$options" | rofi -dmenu -theme "$ROFI_THEME" -p "Display Setup" -selected-row 0)

    case "$chosen" in
        "$opt1") set_vga_primary ;;
        "$opt2") set_edp_primary ;;
        "$opt3") set_vga_only ;;
        "$opt4") set_edp_only ;;
        "$opt5") set_mirror ;;
        "$opt6") apply_config ;;
    esac
}

# Handler argumen CLI
case "$1" in
    "vga-primary"|"vga"|"external")
        set_vga_primary
        ;;
    "edp-primary"|"edp"|"laptop")
        set_edp_primary
        ;;
    "vga-only"|"external-only")
        set_vga_only
        ;;
    "edp-only"|"laptop-only")
        set_edp_only
        ;;
    "mirror")
        set_mirror
        ;;
    "menu")
        show_menu
        ;;
    "apply"|"auto"|*)
        apply_config
        ;;
esac
