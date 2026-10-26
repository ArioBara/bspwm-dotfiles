#!/usr/bin/env bash

# ==============================================================================
#  SEARCHABLE KEYBINDING CHEATSHEET (ROFI)
# ==============================================================================
# Menampilkan seluruh shortcut keyboard sistem dalam daftar interaktif
# yang bisa dicari/filter secara instan menggunakan Rofi.
# ==============================================================================

CHOICE=$(cat << 'EOF' | rofi -dmenu -i -theme ~/.config/rofi/mocha.rasi -p "󰌌 Cari Shortcut" -lines 15
󰀻 Super + Enter               │ Buka Terminal Kitty
󰀻 Super + Shift + Enter       │ Buka Terminal Kitty Mengambang (Floating)
󰀻 Super + Space / Super + D   │ Buka Menu Aplikasi (Rofi Launcher)
󰏘 Super + Alt + Space         │ Buka Theme & Style Switcher
󰡨 Super + Alt + D             │ Buka Docker TUI Manager (Dockman)
󰊢 Gitman                      │ Git Project Manager (gitman)
🧹 System Cleaner              │ Pembersih Cache & Ruang Disk (system-cleaner)
📋 ClipVault                   │ Clipboard History & Snippet Vault (clipvault)
🎨 Palette Forge              │ Ekstrak Warna Wallpaper & Border (palette-forge)
📲 LANShare                    │ Transfer File WiFi Laptop ⇄ HP (lanshare)
📡 NetScout                   │ Scan Perangkat Terhubung & Ping (netscout)
📝 QuickNote                   │ Scratchpad Cepat & Markdown Notes (quicknote)
🎯 App Sniper                  │ Pembasmi Proses Macet & RAM Hog (app-sniper)
⚙️ Super + Alt + A             │ Autostart Manager (Atur Aplikasi Startup)
󰌌 Super + K                   │ Buka Pencarian Pintasan Keyboard Ini
󰌌 Super + F1                  │ Buka Panduan Pintasan Lengkap di Terminal
󰖯 Super + W / Super + Q       │ Tutup Jendela Aktif (Close Window)
󰖯 Super + Shift + Q           │ Paksa Tutup Jendela (Force Kill)
󰖯 Super + F                   │ Layar Penuh (Toggle Fullscreen)
󰖯 Super + Shift + Space       │ Mode Jendela Mengambang (Toggle Floating)
󰖯 Super + M                   │ Mode Monocle (Maximize di dalam workspace)
󰖯 Super + - / N               │ Sembunyikan Jendela (Minimize / Hide)
󰖯 Super + Shift + - / N       │ Tampilkan Jendela Kembali (Restore / Unhide)
󰁨 Super + Panah / H J K L     │ Pindah Fokus Jendela (Kiri, Bawah, Atas, Kanan)
󰁨 Super + Shift + Panah / HJKL│ Tukar Posisi Jendela (Swap Window)
󰁨 Super + R                   │ Putar Arah Belahan Layout 90 Derajat
󰁨 Super + B                   │ Ratakan Ukuran Jendela Seimbang (Balance 50:50)
󰍹 Super + 1 .. 6              │ Pindah ke Workspace 1 - 6 (Monitor Aktif)
󰍹 Super + Shift + 1 .. 6      │ Pindahkan Jendela ke Workspace 1 - 6
󰍹 Super + Ctrl + 1 .. 6       │ Pindah ke Workspace 1 - 6 di Monitor Kedua
󰍹 Super + , / .               │ Pindah Fokus ke Monitor Lain
󰍹 Super + Shift + D           │ Pengaturan Tampilan Multi-Monitor (Display)
󰍜 Klik Kanan / Menu           │ Menu Konteks Desktop (Aplikasi, Tools & Kontrol)
󰍜 Super + Shift + C / Super+P │ Buka Action Center / Quick Settings
󰐥 Super + Shift + E / Super+X │ Buka Menu Power (Shutdown, Reboot, Logout)
󰹑 Super + Shift + S           │ Screenshot Pilihan Area + Anotasi (Flameshot)
󰹑 Print                       │ Screenshot Layar Penuh (Full Screen)
󰕾 Tombol Fn / Volume          │ Kontrol Volume Suara & Mute
󰌌 Super + F9 / Scroll Lock    │ Nyalakan / Matikan Lampu RGB Keyboard
󰑓 Super + Shift + R           │ Restart / Muat Ulang BSPWM Window Manager
󰑓 Super + Escape              │ Muat Ulang Shortcut SXHKD
📖 Buka Tampilan Lengkap di Terminal │ Tampilkan Cheatsheet Berwarna di Kitty
EOF
)

case "$CHOICE" in
    *"Menu Konteks Desktop"*)
        /home/ario/.local/bin/desktop-menu &
        ;;
    *"Theme & Style Switcher"*)
        ~/.config/bspwm/scripts/theme_switcher.sh &
        ;;
    *"Docker TUI Manager"*)
        kitty --class dockman-term -T "🐳 Docker TUI Manager" -e /home/ario/.local/bin/dockman &
        ;;
    *"Gitman"*)
        kitty --class gitman-term -T "󰊢 Git Project Dashboard (Gitman)" -e /home/ario/.local/bin/gitman &
        ;;
    *"System Cleaner"*)
        kitty --class cleaner-term -T "🧹 System & Storage Cleaner" -e /home/ario/.local/bin/system-cleaner &
        ;;
    *"ClipVault"*)
        kitty --class clipvault-term -T "📋 ClipVault Manager" -e /home/ario/.local/bin/clipvault &
        ;;
    *"Palette Forge"*)
        kitty --class palette-term -T "🎨 Palette Forge Theme Engine" -e /home/ario/.local/bin/palette-forge &
        ;;
    *"LANShare"*)
        kitty --class lanshare-term -T "📲 LANShare WiFi Transfer" -e /home/ario/.local/bin/lanshare &
        ;;
    *"NetScout"*)
        kitty --class netscout-term -T "📡 NetScout Network Scanner" -e /home/ario/.local/bin/netscout &
        ;;
    *"QuickNote"*)
        kitty --class quicknote-term -T "📝 QuickNote Scratchpad" -e /home/ario/.local/bin/quicknote &
        ;;
    *"App Sniper"*)
        kitty --class sniper-term -T "🎯 App Sniper Process Killer" -e /home/ario/.local/bin/app-sniper &
        ;;
    *"Autostart Manager"*)
        kitty --class autostart-term -T "⚙️ Autostart Manager" -e /home/ario/.local/bin/autostart-manager &
        ;;
    *"Menu Aplikasi"*)
        ~/.config/rofi/launcher.sh &
        ;;
    *"Action Center"*)
        ~/.config/rofi/controlcenter.sh &
        ;;
    *"Menu Power"*)
        ~/.config/rofi/powermenu.sh &
        ;;
    *"Multi-Monitor"*)
        ~/.config/bspwm/scripts/display.sh &
        ;;
    *"Screenshot Pilihan Area"*)
        sleep 0.2 && flameshot gui &
        ;;
    *"Terminal Kitty Mengambang"*)
        kitty --class kitty-float &
        ;;
    *"Terminal Kitty"*)
        kitty &
        ;;
    *"Panduan Pintasan Lengkap"*|*"Tampilan Lengkap di Terminal"*)
        kitty --class shortcut-term -e ~/.config/bspwm/scripts/shortcut.sh &
        ;;
    *)
        exit 0
        ;;
esac
