#!/usr/bin/env bash

# ==============================================================================
#  CATPPUCCIN MOCHA - FULL FEATURED ACTION CENTER (ROFI)
# ==============================================================================

DIR="$HOME/.config/rofi"
ROFI_THEME="$DIR/controlcenter.rasi"

# 1. Fetch Dynamic System Status
VOL=$(pamixer --get-volume-human 2>/dev/null || pactl get-sink-volume @DEFAULT_SINK@ 2>/dev/null | grep -o '[0-9]*%' | head -n1 || echo "50%")
BRIGHT=$(bash "$HOME/.config/polybar/scripts/brightness.sh" 2>/dev/null | awk '{print $2}' || echo "100%")
DND_IS_PAUSED=$(dunstctl is-paused 2>/dev/null || echo "false")
if [ "$DND_IS_PAUSED" = "true" ]; then
    DND_BADGE="[ AKTIF - Senyap ]"
else
    DND_BADGE="[ Nonaktif ]"
fi

if [ -f "/tmp/.nightlight_active" ]; then
    NIGHT_BADGE="[ Aktif 4500K ]"
else
    NIGHT_BADGE="[ Normal 6500K ]"
fi

if bash "$HOME/.config/bspwm/scripts/rgb_keyboard.sh" status 2>/dev/null | grep -q "on"; then
    RGB_BADGE="[ AKTIF ]"
else
    RGB_BADGE="[ Mati ]"
fi

MEDIA_STATUS=$(playerctl metadata --format "{{ artist }} - {{ title }}" 2>/dev/null || echo "Tidak ada media aktif")
if [ ${#MEDIA_STATUS} -gt 25 ]; then
    MEDIA_STATUS="${MEDIA_STATUS:0:22}..."
fi

# 2. Define Action Items
opt_vol_up="󰕾  Volume: Naikkan (+5%)               [ $VOL ]"
opt_vol_down="󰖀  Volume: Turunkan (-5%)              [ $VOL ]"
opt_vol_mute="󰝟  Volume: Toggle Mute / Unmute"
opt_vol_mixer="󰓃  Volume: Buka Audio Mixer (Pavucontrol)"

opt_bright_up="󰃠  Kecerahan: Tambah (+10%)            [ $BRIGHT ]"
opt_bright_down="󰃟  Kecerahan: Kurangi (-10%)           [ $BRIGHT ]"
opt_bright_max="󰃞  Kecerahan: Set Maksimal (100%)"
opt_bright_min="󰃜  Kecerahan: Set Minimal (20%)"
opt_nightlight="󰛩  Filter Cahaya Biru (Night Light)    $NIGHT_BADGE"
opt_rgb_kbd="󰌌  Keyboard: Lampu RGB Backlight       $RGB_BADGE"

opt_dnd="󰂛  Jangan Ganggu (Do Not Disturb)      $DND_BADGE"
opt_dnd_hist="󰂞  Notifikasi: Tampilkan Riwayat Terakhir"
opt_dnd_clear="󰂚  Notifikasi: Bersihkan Semua Pop-up"

opt_shot_full="󰹑  Screenshot: Tangkap Layar Penuh (Flameshot)"
opt_shot_area="󰒅  Screenshot: Tangkap Area Pilihan (Flameshot)"
opt_record="󰕧  Perekam Layar: Buka SimpleScreenRecorder"
opt_colorpick="󰈊  Color Picker: Pipet Pengambil Warna Layar"

opt_media_toggle="󰐊  Media: Play / Pause Musik           [ $MEDIA_STATUS ]"
opt_media_next="󰒭  Media: Lagu Selanjutnya (Next Track)"
opt_media_prev="󰒮  Media: Lagu Sebelumnya (Prev Track)"

opt_net_gui="󰤨  Jaringan: Pengaturan Koneksi (GUI)"
opt_net_tui="󰤩  Jaringan: Network Manager (TUI)"

opt_sys_btop="󰍛  Sistem: Buka Resource Monitor (Btop)"
opt_sys_zen="󰖯  Sistem: Toggle Mode Zen (Sembunyikan Bar)"
opt_sys_clean="󰃢  Sistem: Bersihkan Cache Memori RAM"

opt_display="󰍹  Tampilan: Pilih / Atur Primary Display"
opt_wall_rand="󰃨  Tampilan: Ganti Wallpaper Acak"
opt_theme_gtk="󰏘  Tampilan: Pengaturan Tema & Ikon (Lxappearance)"
opt_help_keys="󰌌  Bantuan: Panduan Shortcut (Super + F1)"
opt_cal_pop="󰥔  Waktu: Buka Pop-up Kalender"
opt_power_lock="󰌾  Power: Kunci Layar Desktop (Lock)"
opt_power_menu="󰐥  Power: Buka Power Menu (Shutdown/Reboot)"

# 3. Assemble Options
OPTIONS="$opt_vol_up\n$opt_vol_down\n$opt_vol_mute\n$opt_vol_mixer\n$opt_bright_up\n$opt_bright_down\n$opt_bright_max\n$opt_bright_min\n$opt_nightlight\n$opt_rgb_kbd\n$opt_dnd\n$opt_dnd_hist\n$opt_dnd_clear\n$opt_shot_full\n$opt_shot_area\n$opt_record\n$opt_colorpick\n$opt_media_toggle\n$opt_media_next\n$opt_media_prev\n$opt_net_gui\n$opt_net_tui\n$opt_sys_btop\n$opt_sys_zen\n$opt_sys_clean\n$opt_display\n$opt_wall_rand\n$opt_theme_gtk\n$opt_help_keys\n$opt_cal_pop\n$opt_power_lock\n$opt_power_menu"

CHOSEN=$(echo -e "$OPTIONS" | rofi -dmenu -theme "$ROFI_THEME" -p "Action Center" -selected-row 0)

# 4. Handle Execution
case "$CHOSEN" in
    "$opt_vol_up")
        pamixer -i 5 2>/dev/null || pactl set-sink-volume @DEFAULT_SINK@ +5%
        notify-send -u low -t 1200 "Volume" "Volume dinaikkan ke $(pamixer --get-volume-human 2>/dev/null || echo '+5%')"
        ;;
    "$opt_vol_down")
        pamixer -d 5 2>/dev/null || pactl set-sink-volume @DEFAULT_SINK@ -5%
        notify-send -u low -t 1200 "Volume" "Volume diturunkan ke $(pamixer --get-volume-human 2>/dev/null || echo '-5%')"
        ;;
    "$opt_vol_mute")
        pamixer -t 2>/dev/null || pactl set-sink-mute @DEFAULT_SINK@ toggle
        notify-send -u low -t 1200 "Volume" "Mute status diubah"
        ;;
    "$opt_vol_mixer")
        if command -v pavucontrol &>/dev/null; then
            pavucontrol &
        else
            kitty --class mixer-term -e alsamixer &
        fi
        ;;
    "$opt_bright_up")
        bash "$HOME/.config/polybar/scripts/brightness.sh" up
        notify-send -u low -t 1200 "Kecerahan" "Kecerahan dinaikkan"
        ;;
    "$opt_bright_down")
        bash "$HOME/.config/polybar/scripts/brightness.sh" down
        notify-send -u low -t 1200 "Kecerahan" "Kecerahan diturunkan"
        ;;
    "$opt_bright_max")
        bash "$HOME/.config/polybar/scripts/brightness.sh" max
        notify-send -u low -t 1200 "Kecerahan" "Kecerahan diatur ke 100%"
        ;;
    "$opt_bright_min")
        bash "$HOME/.config/polybar/scripts/brightness.sh" min
        notify-send -u low -t 1200 "Kecerahan" "Kecerahan diatur ke 20%"
        ;;
    "$opt_nightlight")
        bash "$HOME/.config/polybar/scripts/nightlight.sh" toggle
        ;;
    "$opt_rgb_kbd")
        bash "$HOME/.config/bspwm/scripts/rgb_keyboard.sh" toggle
        ;;
    "$opt_dnd")
        dunstctl set-paused toggle
        if [ "$(dunstctl is-paused)" = "true" ]; then
            notify-send -u normal -t 1500 "Do Not Disturb" "Mode Jangan Ganggu AKTIF"
        else
            notify-send -u normal -t 1500 "Do Not Disturb" "Notifikasi kembali AKTIF"
        fi
        ;;
    "$opt_dnd_hist")
        dunstctl history-pop
        ;;
    "$opt_dnd_clear")
        dunstctl close-all
        notify-send -u low -t 1000 "Notifikasi" "Semua notifikasi dibersihkan"
        ;;
    "$opt_shot_full")
        flameshot full -p "$HOME/Pictures/Screenshots" -c &
        ;;
    "$opt_shot_area")
        flameshot gui &
        ;;
    "$opt_record")
        if command -v simplescreenrecorder &>/dev/null; then
            simplescreenrecorder &
        else
            notify-send -u normal "Screen Recorder" "Silakan instal: sudo apt install simplescreenrecorder"
        fi
        ;;
    "$opt_colorpick")
        sleep 0.2
        bash "$HOME/.config/bspwm/scripts/colorpicker.sh"
        ;;
    "$opt_media_toggle")
        playerctl play-pause
        ;;
    "$opt_media_next")
        playerctl next
        ;;
    "$opt_media_prev")
        playerctl previous
        ;;
    "$opt_net_gui")
        nm-connection-editor &
        ;;
    "$opt_net_tui")
        kitty -e nmtui &
        ;;
    "$opt_sys_btop")
        if command -v btop &>/dev/null; then
            kitty --class btop-term -e btop &
        else
            kitty --class btop-term -e htop &
        fi
        ;;
    "$opt_sys_zen")
        polybar-msg cmd toggle
        ;;
    "$opt_sys_clean")
        sync
        notify-send -u low -t 1500 "Sistem" "Cache memori RAM berhasil dioptimasi!"
        ;;
    "$opt_display")
        bash "$HOME/.config/bspwm/scripts/display.sh" menu &
        ;;
    "$opt_wall_rand")
        bash "$HOME/.config/bspwm/scripts/set_wallpaper.sh" random
        ;;
    "$opt_theme_gtk")
        lxappearance &
        ;;
    "$opt_help_keys")
        kitty --class shortcut-term -e shortcut &
        ;;
    "$opt_cal_pop")
        bash "$HOME/.config/polybar/scripts/calendar.sh" &
        ;;
    "$opt_power_lock")
        if command -v betterlockscreen &>/dev/null; then
            betterlockscreen -l dim &
        elif command -v i3lock &>/dev/null; then
            i3lock -c 1e1e2e &
        elif command -v xflock4 &>/dev/null; then
            xflock4 &
        else
            notify-send -u normal "Lock Screen" "Kunci layar diaktifkan"
        fi
        ;;
    "$opt_power_menu")
        bash "$HOME/.config/rofi/powermenu.sh" &
        ;;
esac
