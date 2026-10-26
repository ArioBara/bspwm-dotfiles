#!/usr/bin/env bash

# ==============================================================================
#  BSPWM & SYSTEM KEYBINDINGS CHEAT SHEET - CATPPUCCIN MOCHA THEME
# ==============================================================================

# Catppuccin Mocha TrueColors
BOLD="\033[1m"
DIM="\033[2m"
MAUVE="\033[38;2;203;166;247m"
PINK="\033[38;2;245;194;231m"
BLUE="\033[38;2;137;180;250m"
LAVENDER="\033[38;2;180;190;254m"
TEAL="\033[38;2;148;226;213m"
GREEN="\033[38;2;166;227;161m"
PEACH="\033[38;2;250;179;135m"
YELLOW="\033[38;2;249;226;175m"
RED="\033[38;2;243;139;168m"
TEXT="\033[38;2;205;214;244m"
SUBTEXT="\033[38;2;166;173;200m"
OVERLAY="\033[38;2;108;112;134m"
SURFACE="\033[38;2;49;50;68m"
RESET="\033[0m"

clear

echo -e "${MAUVE}${BOLD}"
echo "  ╔════════════════════════════════════════════════════════════════════╗"
echo "  ║            󰌌  BSPWM KEYBINDINGS & SHORTCUT CHEATSHEET              ║"
echo "  ║                Arch Linux / Catppuccin Mocha Standard              ║"
echo "  ╚════════════════════════════════════════════════════════════════════╝"
echo -e "${RESET}"

print_section() {
    local icon="$1"
    local title="$2"
    local color="$3"
    echo -e "${color}${BOLD} ${icon}  ${title}${RESET}"
    echo -e "${OVERLAY} ──────────────────────────────────────────────────────────────────────${RESET}"
}

print_row() {
    local key="$1"
    local desc="$2"
    printf "  ${PINK}%-28s${RESET} ${TEXT}: %s${RESET}\n" "$key" "$desc"
}

# 1. Applications & Launchers
print_section "󰀻" "APLIKASI & LAUNCHER" "${BLUE}"
print_row "Super + Enter" "Buka Terminal Kitty"
print_row "Super + Shift + Enter" "Buka Terminal Kitty Mengambang (Floating)"
print_row "Super + Space / Super + D" "Buka Menu Aplikasi (Rofi Launcher)"
print_row "Super + Alt + Space" "Buka Dynamic Theme Switcher (One Piece, Naruto, dll)"
print_row "Super + K / Super + /" "Buka Cheatsheet Pencarian Pintasan Keyboard (Rofi)"
print_row "Super + Alt + B" "Buka Activity & Resource Monitor (btop)"
print_row "Super + Alt + D" "Buka Docker TUI Manager (Dockman)"
print_row "Super + G" "Buka Guava Ricing Toolbox & Suite"
print_row "Super + Shift + C / P" "Buka Action Center / Quick Settings"
print_row "Super + Shift + E / X" "Buka Menu Power / Exit (Shutdown, Reboot, Logout)"
print_row "Super + Tab" "Beralih Antar Jendela (Window Switcher)"
print_row "Super + E" "Buka File Manager (Nemo / Caja)"
print_row "Super + V" "Buka Neovim Code Editor"
print_row "Super + O" "Buka Ranger (TUI File Manager)"
print_row "Super + T" "Buka Jam Digital (tty-clock)"
print_row "Super + C" "Buka Audio Visualizer (CAVA)"
print_row "Super + Alt + M" "Buka CMatrix Digital Rain"
echo ""

# 2. Python Suite & TUI Tools
print_section "🐍" "SUITE PROGRAM & TUI UTILITY (~/Scripts)" "${TEAL}"
print_row "gitman / Super+Alt+G" "Git Projects Dashboard, Status & Sync TUI"
print_row "system-cleaner" "Pembersih Cache Sistem & Disk Maintenance"
print_row "clipvault / Super+Alt+V" "Clipboard History & Snippet Vault"
print_row "palette-forge" "Ekstraktor Warna Wallpaper & Theme Border"
print_row "lanshare" "Transfer File WiFi Laptop <-> HP via QR Code"
print_row "netscout" "WiFi / Network Scanner & Live Ping Visualizer"
print_row "quicknote / Super+Alt+N" "Scratchpad Cepat & Catatan Markdown"
print_row "app-sniper / Super+Alt+S" "Visual Zombie App & RAM Hog Process Killer"
print_row "autostart / Super+Alt+A" "Kelola Aplikasi & Layanan Startup (Autostart Manager)"
print_row "dockman / Super+Alt+D" "Docker TUI Manager (Container Management)"
print_row "ytmusic / Super + Y" "YouTube Music Terminal Player & Visualizer"
print_row "netmon / Super+Ctrl+M" "Mesh Network & Tailscale Monitor"
echo ""

# 2. Window Management
print_section "󰖯" "PENGELOLAAN JENDELA (WINDOW MANAGEMENT)" "${MAUVE}"
print_row "Super + Shift + Q / Q / W" "Tutup Jendela Aktif (Close / Kill)"
print_row "Super + F" "Layar Penuh (Toggle Fullscreen)"
print_row "Super + Shift + Space / S" "Mode Mengambang (Toggle Floating Window)"
print_row "Super + M" "Monocle Mode (Maximize rapi di dalam workspace)"
print_row "Super + - / N" "Sembunyikan Jendela (Minimize / Hide)"
print_row "Super + Shift + - / N" "Tampilkan Jendela Kembali (Restore / Unhide)"
echo ""

# 3. Layout & Navigation
print_section "󰁨" "NAVIGASI & TATA LETAK (LAYOUT & NAVIGATION)" "${TEAL}"
print_row "Super + H / J / K / L" "Pindah Fokus (Kiri, Bawah, Atas, Kanan)"
print_row "Super + Panah Arah" "Pindah Fokus Jendela"
print_row "Super + Shift + H / J / K / L" "Tukar Posisi Jendela (Swap Window)"
print_row "Super + Shift + Panah" "Tukar Posisi Jendela"
print_row "Super + R" "Putar Arah Layout 90 Derajat (Rotate Tree)"
print_row "Super + B" "Ratakan Ukuran Semua Jendela (Balance 50:50)"
print_row "Super + Ctrl + Panah / HJKL" "Preselect Arah Belahan Jendela Baru"
print_row "Super + Ctrl + Space" "Batalkan Preselect Arah"
echo ""

# 4. Workspaces & Multi-Monitor
print_section "󰍹" "RUANG KERJA & MULTI-MONITOR" "${YELLOW}"
print_row "Super + 1 .. 6" "Pindah Workspace 1 - 6 di monitor aktif saat ini"
print_row "Super + Shift + 1 .. 6" "Pindahkan Jendela ke Workspace 1 - 6 di monitor aktif"
print_row "Super + Ctrl + 1 .. 6" "Pindah ke Workspace 1 - 6 di monitor kedua"
print_row "Super + Ctrl + Shift + 1 .. 6" "Pindahkan Jendela ke Workspace 1 - 6 di monitor kedua"
print_row "Super + , / ." "Pindah Fokus Monitor (Layar Sebelumnya / Berikutnya)"
print_row "Super + Shift + , / ." "Kirim Jendela ke Monitor Lain"
print_row "Super + Shift + D" "Buka Menu Switcher Pengaturan Display (Rofi)"
echo ""

# 5. Mouse & Window Gaps
print_section "󰍽" "KONTROL MOUSE & JARAK CELAH (GAPS & RESIZE)" "${PEACH}"
print_row "Super + Klik Kiri + Drag" "Geser / Pindahkan Jendela Bebas (Move)"
print_row "Super + Klik Kanan + Drag" "Ubah Ukuran Jendela Bebas (Resize)"
print_row "Super + Alt + H / J / K / L" "Ubah Ukuran Jendela via Keyboard"
print_row "Super + ]" "Perbesar Celah Jendela (Jendela Otomatis Mengecil)"
print_row "Super + [" "Perkecil Celah Jendela Kembali"
echo ""

# 6. System & Reload
print_section "󰑓" "SISTEM & MULTIMEDIA" "${GREEN}"
print_row "Super + Shift + R / Alt + R" "Restart / Reload BSPWM Window Manager"
print_row "Super + Escape" "Reload Shortcut SXHKD"
print_row "Super + Shift + S / Super+Print" "Screenshot Pilihan Area (Flameshot GUI)"
print_row "Print" "Screenshot Layar Penuh (Flameshot)"
print_row "Super + Alt + R / Super+Shift+Print" "Rekam Layar (SimpleScreenRecorder)"
print_row "Fn / Tombol Volume" "Atur Volume Audio & Mute"
print_row "Scroll Lock / Super + F9" "Nyalakan / Matikan Lampu RGB Keyboard"
echo ""

echo -e "${OVERLAY} ──────────────────────────────────────────────────────────────────────${RESET}"
echo -e "${SUBTEXT} 💡 Tip: Ketik ${BOLD}${MAUVE}shortcut${RESET}${SUBTEXT} kapan saja di terminal untuk membuka panduan ini.${RESET}"
echo -e "${OVERLAY} [Tekan tombol apa saja untuk menutup jendela ini]${RESET}\n"

read -n 1 -s -r
