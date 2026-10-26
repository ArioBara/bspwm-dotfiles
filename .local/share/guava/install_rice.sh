#!/usr/bin/env bash

# ==============================================================================
#  CATPPUCCIN MOCHA BSPWM RICING & GUAVA SUITE - COMPLETE AUTO INSTALLER
#  Gundam Edition • Floating Island Polybar • Guava Toolbox • Keybindings
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

BOLD="\033[1m"
MAUVE="\033[38;2;203;166;247m"
TEAL="\033[38;2;148;226;213m"
GREEN="\033[38;2;166;227;161m"
BLUE="\033[38;2;137;180;250m"
YELLOW="\033[38;2;249;226;175m"
PINK="\033[38;2;245;194;231m"
RESET="\033[0m"

echo -e "${MAUVE}${BOLD}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      BSPWM CATPPUCCIN MOCHA RICE & GUAVA SUITE INSTALLER       ║"
echo "║         Gundam Edition • Guava Toolbox • Full Dependencies     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${RESET}"

# 1. Install System Packages & Guava Dependencies via APT
echo -e "${BLUE}[1/9] Memperbarui package list dan menginstal seluruh paket sistem & dependensi Guava...${RESET}"
sudo apt update
sudo apt install -y \
    bspwm \
    sxhkd \
    picom \
    polybar \
    rofi \
    kitty \
    fish \
    feh \
    playerctl \
    dunst \
    pavucontrol \
    alsa-utils \
    pamixer \
    brightnessctl \
    flameshot \
    simplescreenrecorder \
    maim \
    xclip \
    papirus-icon-theme \
    libnotify-bin \
    pulseaudio-utils \
    xdotool \
    jq \
    curl \
    wget \
    unzip \
    tar \
    git \
    rsync \
    qrencode \
    nmap \
    net-tools \
    udisks2 \
    neofetch \
    cmatrix \
    neovim \
    ranger \
    zenity \
    btop \
    python3 \
    python3-pip \
    python3-pil

# 2. Deploy Configuration Files (.config)
echo -e "\n${BLUE}[2/9] Menyinkronkan file konfigurasi dotfiles ke ~/.config/...${RESET}"
mkdir -p "$HOME/.config"
if [ -d "$SCRIPT_DIR/.config" ]; then
    cp -r "$SCRIPT_DIR/.config/"* "$HOME/.config/"
    echo -e "${GREEN}✓ Konfigurasi BSPWM, Polybar, Rofi, Kitty, Fish, Dunst, Picom disalin.${RESET}"
elif [ -d "$HOME/bspwm-catppuccin-rice/.config" ] && [ "$SCRIPT_DIR" != "$HOME/bspwm-catppuccin-rice" ]; then
    cp -r "$HOME/bspwm-catppuccin-rice/.config/"* "$HOME/.config/"
    echo -e "${GREEN}✓ Konfigurasi dari bundle bspwm-catppuccin-rice disalin.${RESET}"
fi

if [ -f "$SCRIPT_DIR/.gtkrc-2.0" ]; then
    cp "$SCRIPT_DIR/.gtkrc-2.0" "$HOME/.gtkrc-2.0"
elif [ -f "$HOME/bspwm-catppuccin-rice/.gtkrc-2.0" ]; then
    cp "$HOME/bspwm-catppuccin-rice/.gtkrc-2.0" "$HOME/.gtkrc-2.0"
fi

# 3. Deploy Fonts & Wallpapers
echo -e "\n${BLUE}[3/9] Memasang Font JetBrainsMono Nerd Font & Wallpaper...${RESET}"
mkdir -p "$HOME/.local/share/fonts" "$HOME/Pictures/Wallpapers" "$HOME/Pictures/Screenshots"
if [ -d "$SCRIPT_DIR/fonts" ]; then
    cp -r "$SCRIPT_DIR/fonts/"* "$HOME/.local/share/fonts/" 2>/dev/null || true
elif [ -d "$HOME/bspwm-catppuccin-rice/fonts" ]; then
    cp -r "$HOME/bspwm-catppuccin-rice/fonts/"* "$HOME/.local/share/fonts/" 2>/dev/null || true
fi

if [ -d "$SCRIPT_DIR/wallpapers" ]; then
    cp -r "$SCRIPT_DIR/wallpapers/"* "$HOME/Pictures/Wallpapers/" 2>/dev/null || true
elif [ -d "$HOME/bspwm-catppuccin-rice/wallpapers" ]; then
    cp -r "$HOME/bspwm-catppuccin-rice/wallpapers/"* "$HOME/Pictures/Wallpapers/" 2>/dev/null || true
fi
fc-cache -f "$HOME/.local/share/fonts" 2>/dev/null || true
echo -e "${GREEN}✓ Font dan wallpaper berhasil dipasang.${RESET}"

# 4. Setup Guava Ricing Toolbox & Registrasi Global CLI
echo -e "\n${BLUE}[4/9] Memasang Guava Ricing Toolbox & Perintah Global 'guava'...${RESET}"
mkdir -p "$HOME/.local/share/guava" "$HOME/.local/bin" "$HOME/.local/share/applications"

GUAVA_SRC=""
if [ -d "$SCRIPT_DIR/guava" ]; then
    GUAVA_SRC="$SCRIPT_DIR/guava"
elif [ -d "$SCRIPT_DIR/bspwm-catppuccin-rice/guava" ]; then
    GUAVA_SRC="$SCRIPT_DIR/bspwm-catppuccin-rice/guava"
elif [ -d "$HOME/bspwm-catppuccin-rice/guava" ]; then
    GUAVA_SRC="$HOME/bspwm-catppuccin-rice/guava"
elif [ -d "/media/sf_Shared/Downloads/scripts/ricing" ]; then
    GUAVA_SRC="/media/sf_Shared/Downloads/scripts/ricing"
fi

if [ -n "$GUAVA_SRC" ] && [ -d "$GUAVA_SRC" ]; then
    cp -r "$GUAVA_SRC/"* "$HOME/.local/share/guava/"
    chmod +x "$HOME/.local/share/guava/"*.py 2>/dev/null || true
    echo -e "${GREEN}✓ Modul Guava Toolbox disalin ke ~/.local/share/guava/.${RESET}"
fi

# Launcher global guava
cat << 'EOF' > "$HOME/.local/bin/guava"
#!/usr/bin/env bash
# Guava Ricing Toolbox Global Launcher
if [ -f "$HOME/.local/share/guava/guava_toolbox.py" ]; then
    exec python3 "$HOME/.local/share/guava/guava_toolbox.py" "$@"
elif [ -f "$HOME/bspwm-catppuccin-rice/guava/guava_toolbox.py" ]; then
    exec python3 "$HOME/bspwm-catppuccin-rice/guava/guava_toolbox.py" "$@"
elif [ -f "/media/sf_Shared/Downloads/scripts/ricing/guava_toolbox.py" ]; then
    exec python3 "/media/sf_Shared/Downloads/scripts/ricing/guava_toolbox.py" "$@"
else
    echo -e "\033[31m[!] Guava Toolbox files not found in ~/.local/share/guava or /media/sf_Shared\033[0m"
    exit 1
fi
EOF
chmod +x "$HOME/.local/bin/guava"

# Registrasi PATH di Fish, Bash, dan Zsh
mkdir -p "$HOME/.config/fish/conf.d"
echo 'fish_add_path -g $HOME/.local/bin' > "$HOME/.config/fish/conf.d/guava_path.fish"
if [ -f "$HOME/.bashrc" ]; then
    grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc" || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
fi
if [ -f "$HOME/.zshrc" ]; then
    grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.zshrc" || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
fi

# Desktop Entry untuk Rofi & Menu Aplikasi
cat << 'EOF' > "$HOME/.local/share/applications/guava.desktop"
[Desktop Entry]
Name=Guava Toolbox
Comment=Linux Ricing, App Installer, Tech Stack & System Suite
Exec=kitty --class guava-term -T "Guava Toolbox" -e guava
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Utility;System;Development;
Keywords=guava;ricing;installer;system;tools;
EOF
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
echo -e "${GREEN}✓ Perintah 'guava' dan guava.desktop berhasil disiapkan.${RESET}"

# 5. Setup Catppuccin Mocha Mauve GTK Theme
echo -e "\n${BLUE}[5/9] Menyiapkan Tema GTK Catppuccin Mocha Mauve...${RESET}"
mkdir -p "$HOME/.themes" "$HOME/.config/gtk-3.0" "$HOME/.config/gtk-4.0"
if [ ! -d "$HOME/.themes/catppuccin-mocha-mauve-standard+default" ]; then
    echo -e "${YELLOW}Mengunduh Catppuccin GTK Theme...${RESET}"
    mkdir -p /tmp/gtk-theme
    curl -Lo /tmp/gtk-theme/catppuccin.zip "https://github.com/catppuccin/gtk/releases/download/v1.0.3/catppuccin-mocha-mauve-standard%2Bdefault.zip"
    unzip -qo /tmp/gtk-theme/catppuccin.zip -d "$HOME/.themes/"
    rm -rf /tmp/gtk-theme
fi

# Link GTK 4 assets
ln -sf "$HOME/.themes/catppuccin-mocha-mauve-standard+default/gtk-4.0/gtk.css" "$HOME/.config/gtk-4.0/gtk.css" 2>/dev/null || true
ln -sf "$HOME/.themes/catppuccin-mocha-mauve-standard+default/gtk-4.0/gtk-dark.css" "$HOME/.config/gtk-4.0/gtk-dark.css" 2>/dev/null || true
ln -sf "$HOME/.themes/catppuccin-mocha-mauve-standard+default/gtk-4.0/assets" "$HOME/.config/gtk-4.0/assets" 2>/dev/null || true

# Apply gsettings for dark mode & Catppuccin theme
gsettings set org.gnome.desktop.interface gtk-theme "catppuccin-mocha-mauve-standard+default" 2>/dev/null || true
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark' 2>/dev/null || true
gsettings set org.cinnamon.desktop.interface gtk-theme "catppuccin-mocha-mauve-standard+default" 2>/dev/null || true
gsettings set org.x.apps.portal color-scheme 'prefer-dark' 2>/dev/null || true
echo -e "${GREEN}✓ Tema GTK Catppuccin Mocha diterapkan.${RESET}"

# 6. Setup Papirus-Dark with Violet Folders
echo -e "\n${BLUE}[6/9] Mengonfigurasi Ikon Papirus-Dark (Folder Ungu/Violet)...${RESET}"
if [ ! -f "$HOME/.local/bin/papirus-folders" ]; then
    curl -sLo "$HOME/.local/bin/papirus-folders" "https://raw.githubusercontent.com/PapirusDevelopmentTeam/papirus-folders/master/papirus-folders"
    chmod +x "$HOME/.local/bin/papirus-folders"
fi
mkdir -p "$HOME/.local/share/icons"
if [ ! -d "$HOME/.local/share/icons/Papirus-Dark" ] && [ -d /usr/share/icons/Papirus-Dark ]; then
    cp -r /usr/share/icons/Papirus "$HOME/.local/share/icons/" 2>/dev/null || true
    cp -r /usr/share/icons/Papirus-Dark "$HOME/.local/share/icons/" 2>/dev/null || true
fi
XDG_DATA_DIRS="$HOME/.local/share:$XDG_DATA_DIRS" "$HOME/.local/bin/papirus-folders" -C violet -t Papirus-Dark -u 2>/dev/null || true
gsettings set org.gnome.desktop.interface icon-theme "Papirus-Dark" 2>/dev/null || true
gsettings set org.cinnamon.desktop.interface icon-theme "Papirus-Dark" 2>/dev/null || true
gtk-update-icon-cache -f "$HOME/.local/share/icons/Papirus-Dark" 2>/dev/null || true
echo -e "${GREEN}✓ Ikon Papirus Ungu diterapkan.${RESET}"

# 7. Setup Global 'shortcut' CLI Command & SXHKD Keybindings
echo -e "\n${BLUE}[7/9] Menyiapkan Perintah Global 'shortcut' & Keybinding SXHKD...${RESET}"
if [ -f "$HOME/.config/bspwm/scripts/shortcut.sh" ]; then
    chmod +x "$HOME/.config/bspwm/scripts/shortcut.sh"
    ln -sf "$HOME/.config/bspwm/scripts/shortcut.sh" "$HOME/.local/bin/shortcut"
    ln -sf "$HOME/.config/bspwm/scripts/shortcut.sh" "$HOME/.local/bin/shortcut.sh"
    chmod +x "$HOME/.local/bin/shortcut" "$HOME/.local/bin/shortcut.sh"
    echo -e "${GREEN}✓ Perintah 'shortcut' terdaftar global di \$PATH.${RESET}"
fi

# Symlink opencode if installed
if [ -f "$HOME/.opencode/bin/opencode" ]; then
    ln -sf "$HOME/.opencode/bin/opencode" "$HOME/.local/bin/opencode"
    chmod +x "$HOME/.local/bin/opencode" 2>/dev/null || true
fi

# 8. Setup Desktop Entry BSPWM for Display Manager
echo -e "\n${BLUE}[8/9] Menyiapkan Desktop Entry BSPWM untuk Login Manager...${RESET}"
if [ ! -f /usr/share/xsessions/bspwm.desktop ]; then
    echo "[Desktop Entry]
Name=bspwm
Comment=Binary space partitioning window manager
Exec=bspwm
Type=Application
DesktopNames=bspwm" | sudo tee /usr/share/xsessions/bspwm.desktop >/dev/null
    echo -e "${GREEN}✓ /usr/share/xsessions/bspwm.desktop dibuat.${RESET}"
fi

# 9. Firefox Dark Mode, Permissions & Wallpaper Initialization
echo -e "\n${BLUE}[9/9] Menyelaraskan Firefox Dark Theme, Izin Script & Wallpaper...${RESET}"
for p in "$HOME/.config/mozilla/firefox/"*.default-release "$HOME/.config/mozilla/firefox/"*.default; do
    if [ -d "$p" ]; then
        cat << 'EOF' > "$p/user.js"
user_pref("layout.css.prefers-color-scheme.content-override", 0);
user_pref("widget.content.gtk-theme", "catppuccin-mocha-mauve-standard+default");
user_pref("browser.theme.toolbar-theme", 0);
user_pref("browser.theme.dark-private-windows", true);
EOF
    fi
done

# Ensure all scripts have executable permissions
chmod +x "$HOME/.config/bspwm/bspwmrc" 2>/dev/null || true
chmod +x "$HOME/.config/bspwm/scripts/"*.sh 2>/dev/null || true
chmod +x "$HOME/.config/polybar/launch.sh" 2>/dev/null || true
chmod +x "$HOME/.config/polybar/scripts/"*.sh 2>/dev/null || true
chmod +x "$HOME/.config/rofi/"*.sh 2>/dev/null || true
chmod +x "$HOME/.local/share/guava/"*.py 2>/dev/null || true

if [ -f "$HOME/.config/bspwm/scripts/set_wallpaper.sh" ]; then
    bash "$HOME/.config/bspwm/scripts/set_wallpaper.sh" 2>/dev/null || true
fi

echo -e "\n${GREEN}${BOLD}════════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}  INSTALASI & KONFIGURASI SELESAI DENGAN SUKSES! 🎉${RESET}"
echo -e "${GREEN}${BOLD}════════════════════════════════════════════════════════════════${RESET}"
echo -e "${MAUVE}Komponen yang telah terkonfigurasi:${RESET}"
echo -e " • ${TEAL}Window Manager${RESET}  : BSPWM (Catppuccin Mocha, Gaps, 4 Workspaces)"
echo -e " • ${TEAL}Hotkeys${RESET}         : SXHKD (Standard Arch Linux / i3 / BSPWM)"
echo -e " • ${TEAL}Status Bar${RESET}      : Polybar (Capsule Island - Quick Launchers, Workspaces, Battery, Calendar)"
echo -e " • ${TEAL}Action Center${RESET}   : Quick Settings (Volume, Brightness, DND, Flameshot, Recorder, Color Picker)"
echo -e " • ${TEAL}App Launcher${RESET}    : Rofi (Modern Grid, Power Menu & Action Center - Mouse & Keyboard)"
echo -e " • ${TEAL}Guava Suite${RESET}     : Guava Toolbox (App Installer, Tech Stack, AI Agents, System Tools)"
echo -e " • ${TEAL}Terminal${RESET}        : Kitty (JetBrainsMono Nerd Font + Smart Copy-Paste)"
echo -e " • ${TEAL}Shell${RESET}           : Fish Shell (Catppuccin syntax + Git prompt)"
echo -e " • ${TEAL}GTK Theme${RESET}       : Catppuccin Mocha Mauve (Nemo, Firefox, GTK3/4)"
echo -e " • ${TEAL}Icon Theme${RESET}      : Papirus-Dark (Folder Ungu/Violet)"
echo -e " • ${TEAL}Notification${RESET}    : Dunst (Catppuccin notifications + Volume bar)"
echo -e " • ${TEAL}Media & Tools${RESET}   : Flameshot (Screenshot), SimpleScreenRecorder (Perekam Layar), Btop, Ranger"
echo -e " • ${TEAL}Wallpaper${RESET}       : Gundam Neo-Tokyo (Gundam Edition)"
echo ""
echo -e "${BLUE}${BOLD}Keybindings Utama:${RESET}"
echo -e " • ${BOLD}Super + F1${RESET}                  : Buka Contekan Shortcut (Floating Cheatsheet)"
echo -e " • ${BOLD}Super + G${RESET}                   : Buka Guava Ricing Toolbox (CLI Suite)"
echo -e " • ${BOLD}Super + Enter${RESET}               : Buka Kitty Terminal"
echo -e " • ${BOLD}Super + Shift+Enter${RESET}         : Buka Floating Kitty Terminal"
echo -e " • ${BOLD}Super + D${RESET}                   : Buka Rofi Application Launcher"
echo -e " • ${BOLD}Super + Shift+C / P${RESET}         : Buka Action Center / Control Panel"
echo -e " • ${BOLD}Super + Shift+E / X${RESET}         : Buka Rofi Power Menu (Shutdown, Reboot, Lock)"
echo -e " • ${BOLD}Super + Shift+S / Super+Print${RESET}: Screenshot Pilihan Area (Flameshot GUI)"
echo -e " • ${BOLD}Print${RESET}                       : Screenshot Layar Penuh (Flameshot)"
echo -e " • ${BOLD}Super + Alt+R / Shift+Print${RESET}  : Buka Perekam Layar (SimpleScreenRecorder)"
echo -e " • ${BOLD}Super + O${RESET}                   : Buka Ranger (TUI File Manager)"
echo -e " • ${BOLD}Super + V${RESET}                   : Buka Neovim Code Editor"
echo -e " • ${BOLD}Super + Shift+Q / W${RESET}         : Tutup Window Aktif (Close)"
echo -e " • ${BOLD}Super + F${RESET}                   : Layar Penuh (Maximize / Fullscreen)"
echo -e " • ${BOLD}Super + M${RESET}                   : Monocle Mode (Maximize di dalam workspace)"
echo -e " • ${BOLD}Super + - / N${RESET}               : Sembunyikan Jendela (Minimize / Hide)"
echo -e " • ${BOLD}Super + Shift + -/N${RESET}         : Tampilkan Kembali Jendela (Restore / Unhide)"
echo -e " • ${BOLD}Super + Tab${RESET}                 : Beralih & Pilih Jendela (Window Switcher)"
echo -e " • ${BOLD}Super + Shift+Space / S${RESET}     : Toggle Floating Mode"
echo -e " • ${BOLD}Super + 1..4${RESET}                : Pindah Workspace 1-4"
echo -e " • ${BOLD}Super + Shift + 1..4${RESET}        : Pindahkan Jendela ke Workspace 1-4"
echo -e " • ${BOLD}Super + H / J / K / L${RESET}         : Pindah Fokus Jendela"
echo -e " • ${BOLD}Super + Shift + HJKL${RESET}        : Tukar Posisi Jendela (Swap)"
echo -e " • ${BOLD}Super + R${RESET}                   : Putar Layout 90 Derajat (Rotate)"
echo -e " • ${BOLD}Super + B${RESET}                   : Ratakan Ukuran Jendela (Balance 50:50)"
echo -e " • ${BOLD}Super + ] / [${RESET}               : Perbesar / Perkecil Celah Jendela (Gaps)"
echo -e " • ${BOLD}Super + Klik Kiri${RESET}           : Geser Window (Move)"
echo -e " • ${BOLD}Super + Klik Kanan${RESET}          : Ubah Ukuran Window (Resize)"
echo -e " • ${BOLD}Super + Alt + W${RESET}             : Ganti Wallpaper secara acak"
echo -e " • ${BOLD}Super + Shift + R${RESET}           : Reload BSPWM Window Manager"
echo -e " • ${BOLD}Super + Esc${RESET}                 : Reload SXHKD Hotkeys Daemon"
echo ""
echo -e "${MAUVE}Cara memulai session:${RESET}"
echo -e " 1. Logout dari session saat ini."
echo -e " 2. Pada halaman login, klik ikon sesi desktop dan pilih ${BOLD}bspwm${RESET}."
echo -e " 3. Masukkan password untuk masuk ke setup ricing baru Anda!"
echo ""
