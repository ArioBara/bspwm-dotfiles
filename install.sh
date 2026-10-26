#!/usr/bin/env bash
# ==============================================================================
#  BSPWM & RICING SUITE INSTALLER - BY ARIOBARA
# ==============================================================================
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$HOME/.config-backup-$(date +%Y%m%d_%H%M%S)"

echo "=================================================================="
echo "  Installing BSPWM Dotfiles & Custom Ricing Applications"
echo "=================================================================="

# 1. Backup existing configurations
mkdir -p "$BACKUP_DIR"
for cfg in bspwm sxhkd polybar rofi picom dunst kitty fish cava btop ranger neofetch flameshot papirus-folders; do
    if [ -d "$HOME/.config/$cfg" ]; then
        cp -r "$HOME/.config/$cfg" "$BACKUP_DIR/"
    fi
done
echo "[+] Existing configs backed up to: $BACKUP_DIR"

# 2. Copy .config, .themes, .local, and Scripts
mkdir -p "$HOME/.config" "$HOME/.themes" "$HOME/.local/bin" "$HOME/.local/share/applications" "$HOME/Scripts"

cp -r "$REPO_DIR/.config/"* "$HOME/.config/"
cp -r "$REPO_DIR/.themes/"* "$HOME/.themes/" 2>/dev/null || true
cp -r "$REPO_DIR/.local/bin/"* "$HOME/.local/bin/"
cp -r "$REPO_DIR/.local/share/"* "$HOME/.local/share/"
cp -r "$REPO_DIR/Scripts/"* "$HOME/Scripts/"

# Update hardcoded /home/ario paths in .desktop and config files if username differs
if [ "$HOME" != "/home/ario" ]; then
    find "$HOME/.config" "$HOME/.local/share/applications" "$HOME/Scripts" -type f \
        -exec sed -i "s|/home/ario|$HOME|g" {} + 2>/dev/null || true
fi

# 3. Ensure executable permissions
chmod +x "$HOME/.config/bspwm/bspwmrc"
chmod +x "$HOME/.config/bspwm/scripts/"*.sh 2>/dev/null || true
chmod +x "$HOME/.config/polybar/launch.sh" 2>/dev/null || true
chmod +x "$HOME/.config/rofi/"*.sh 2>/dev/null || true
chmod +x "$HOME/.local/bin/"* 2>/dev/null || true
chmod +x "$HOME/.local/share/guava/"*.py "$HOME/.local/share/guava/"*.sh 2>/dev/null || true
find "$HOME/Scripts" -name "*.py" -exec chmod +x {} +

# 4. Create CLI & Ricing Symlinks in ~/.local/bin
ln -sf "$HOME/Scripts/app-sniper/sniper.py" "$HOME/.local/bin/app-sniper"
ln -sf "$HOME/Scripts/autostart-manager/autostart.py" "$HOME/.local/bin/autostart"
ln -sf "$HOME/Scripts/autostart-manager/autostart.py" "$HOME/.local/bin/autostart-manager"
ln -sf "$HOME/Scripts/clipvault/clipvault.py" "$HOME/.local/bin/clipvault"
ln -sf "$HOME/Scripts/desktop-menu/desktop_menu.py" "$HOME/.local/bin/desktop-menu"
ln -sf "$HOME/Scripts/desktop-menu/desktop_menu.py" "$HOME/.local/bin/desktop-menu-daemon"
ln -sf "$HOME/.local/bin/dockman" "$HOME/.local/bin/docker-manager"
ln -sf "$HOME/Scripts/gitman/gitman.py" "$HOME/.local/bin/gitman"
ln -sf "$HOME/Scripts/lanshare/lanshare.py" "$HOME/.local/bin/lanshare"
ln -sf "$HOME/Scripts/tailscale-honcho-monitor/monitor.py" "$HOME/.local/bin/netmon"
ln -sf "$HOME/Scripts/netscout/netscout.py" "$HOME/.local/bin/netscout"
ln -sf "$HOME/Scripts/palette-forge/forge.py" "$HOME/.local/bin/palette-forge"
ln -sf "$HOME/Scripts/quicknote/quicknote.py" "$HOME/.local/bin/quicknote"
ln -sf "$HOME/Scripts/make_showcase_video.py" "$HOME/.local/bin/record-showcase"
ln -sf "$HOME/.config/bspwm/scripts/rgb_keyboard.sh" "$HOME/.local/bin/rgb-keyboard"
ln -sf "$HOME/.config/bspwm/scripts/rgb_keyboard.sh" "$HOME/.local/bin/rgb_keyboard.sh"
ln -sf "$HOME/.config/bspwm/scripts/shortcut.sh" "$HOME/.local/bin/shortcut"
ln -sf "$HOME/.config/bspwm/scripts/shortcut.sh" "$HOME/.local/bin/shortcut.sh"
ln -sf "$HOME/Scripts/system-cleaner/cleaner.py" "$HOME/.local/bin/system-cleaner"
ln -sf "$HOME/.config/bspwm/scripts/theme_switcher.sh" "$HOME/.local/bin/theme"
ln -sf "$HOME/Scripts/ytmusic-tui/ytmusic.py" "$HOME/.local/bin/ytmusic"

echo "[+] Symlinks created in ~/.local/bin"
echo "[+] Done! Log into BSPWM or reload with: Super + Shift + R"
