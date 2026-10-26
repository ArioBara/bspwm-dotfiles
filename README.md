# 🌿 BSPWM Catppuccin Mocha Dotfiles & Custom Ricing Suite

Koleksi konfigurasi **BSPWM (Binary Space Partitioning Window Manager)** lengkap beserta **14+ aplikasi TUI/GUI kustom** bertema **Catppuccin Mocha** untuk produktivitas developer dan *ricing* di Linux.

---

## ✨ Komponen Utama

### 1. Window Manager & Desktop Ecosystem (`.config/`)
| Komponen | Direktori | Deskripsi |
| :--- | :--- | :--- |
| **Window Manager** | `.config/bspwm/` | Konfigurasi tiling, border Catppuccin Mocha, floating rules khusus untuk semua utilitas TUI, multi-monitor (`display.sh`), dynamic theme switcher (`theme_switcher.sh`), dan koleksi wallpaper. |
| **Hotkey Daemon** | `.config/sxhkd/` | Shortcut keyboard lengkap untuk navigasi jendela, multi-monitor, launcher Rofi, dan pemicu aplikasi TUI. |
| **Status Bar** | `.config/polybar/` | Top floating bar modular (`config.ini`, `modules.ini`, `colors.ini`, `launch.sh`). |
| **App Launcher & Menus** | `.config/rofi/` | App Launcher (`launcher.sh`), Power Menu (`powermenu.sh`), Action/Control Center (`controlcenter.sh`), Desktop Context Menu, dan Window Switcher. |
| **Terminal Emulator** | `.config/kitty/` | Kitty terminal dengan `JetBrainsMono Nerd Font`, powerline tab bar, dan palet dinamis. |
| **Shell** | `.config/fish/` | Fish shell dengan prompt Git Catppuccin Mocha kustom dan alias produktivitas. |
| **Compositor & Notifikasi** | `.config/picom/`, `.config/dunst/` | Compositor X11 & daemon notifikasi ringan bertema senada. |
| **CLI & Media Utilities** | `.config/btop/`, `.config/cava/`, `.config/ranger/`, `.config/neofetch/`, `.config/flameshot/` | Konfigurasi monitor sistem, audio visualizer, file manager terminal, info sistem, dan screenshot. |
| **GTK Themes** | `.themes/`, `.config/gtk-3.0/`, `.config/gtk-4.0/` | Tema GTK `catppuccin-mocha-mauve-standard+default`. |

---

### 2. Custom Ricing & Developer Applications (`Scripts/` & `.local/`)
Semua aplikasi di bawah ini memiliki aturan *floating window* khusus di `bspwmrc` dan `.desktop` entry untuk diakses langsung dari Rofi:

| Aplikasi / Perintah | Lokasi Sumber | Fungsi |
| :--- | :--- | :--- |
| **`guava`** | `.local/share/guava/` | **Guava Ricing Toolbox** — Dashboard sistem, tech stack installer, backup manager, network tools, dan AI agents manager. |
| **`gitman`** | `Scripts/gitman/gitman.py` | **Git Project Dashboard** — Kelola banyak repositori Git secara visual di terminal. |
| **`dockman`** | `.local/bin/dockman` | **Docker TUI Manager** — Kelola container, image, dan log Docker secara interaktif. |
| **`clipvault`** | `Scripts/clipvault/clipvault.py` | **Smart Clipboard & Snippet Vault** — Penyimpanan riwayat clipboard dan kode snippet. |
| **`quicknote`** | `Scripts/quicknote/quicknote.py` | **QuickNote Scratchpad** — Catatan cepat berbasis Markdown langsung dari shortcut. |
| **`app-sniper`** | `Scripts/app-sniper/sniper.py` | **Visual Process & Zombie Killer** — Cari dan hentikan proses yang memakan resource. |
| **`autostart-manager`** | `Scripts/autostart-manager/autostart.py` | **Autostart Manager** — Kelola aplikasi dan daemon yang berjalan saat startup. |
| **`palette-forge`** | `Scripts/palette-forge/forge.py` | **Palette Forge** — Generator dan pengelola palet warna ricing. |
| **`netscout`** | `Scripts/netscout/netscout.py` | **NetScout** — Pemindai jaringan lokal dan port scanner interaktif. |
| **`lanshare`** | `Scripts/lanshare/lanshare.py` | **LANShare** — Berbagi file cepat antar perangkat di jaringan lokal. |
| **`netmon`** | `Scripts/tailscale-honcho-monitor/monitor.py` | **Mesh & Honcho Monitor** — Monitor jaringan Tailscale & layanan Honcho. |
| **`system-cleaner`** | `Scripts/system-cleaner/cleaner.py` | **System Cleaner** — Pembersih cache, log journalctl, dan paket tidak terpakai. |
| **`ytmusic`** | `Scripts/ytmusic-tui/ytmusic.py` | **YouTube Music TUI** — Pemutar musik terminal ringan bertema Catppuccin. |
| **`desktop-menu`** | `Scripts/desktop-menu/desktop_menu.py` | **Desktop Right-Click Context Menu** — Menu klik kanan interaktif di desktop BSPWM. |

---

## ⌨️ Shortcut Utama (`sxhkd` & Cinnamon)

| Shortcut | Aksi |
| :--- | :--- |
| `Super + Return` | Buka Terminal Kitty |
| `Super + Shift + Return` | Buka Floating Terminal Kitty |
| `Super + Space` / `Super + D` | Rofi Application Launcher |
| `Super + Tab` | Rofi Window Switcher |
| `Super + P` / `Super + Shift + C` | Rofi Control Center / Action Center |
| `Super + X` / `Super + Shift + E` | Rofi Power Menu |
| `Super + F1` / `Super + /` | Rofi Shortcut Cheatsheet Interaktif |
| `Super + Alt + Space` | Dynamic Theme Switcher |
| `Super + Shift + D` | Rofi Multi-Monitor Display Setup |
| `Super + Alt + G` | Buka **Gitman** (Git Dashboard) |
| `Super + Alt + D` | Buka **Dockman** (Docker TUI Manager) |
| `Super + Alt + V` | Buka **ClipVault** (Clipboard Manager) |
| `Super + Alt + N` | Buka **QuickNote** (Scratchpad) |
| `Super + Alt + S` | Buka **App Sniper** (Process Killer) |
| `Super + Alt + A` | Buka **Autostart Manager** |
| `Super + G` | Buka **Guava Ricing Toolbox** |
| `Super + Y` | Buka **YouTube Music TUI** |
| `Super + Shift + S` / `Super + Print` | Screenshot Area & Edit (**Flameshot GUI**) |
| `Print` | Screenshot Fullscreen ke `~/Pictures/Screenshots` & Clipboard |
| `Super + Alt + R` / `Super + Shift + Print` | Buka **SimpleScreenRecorder** |

---

## 🚀 Cara Instalasi

```bash
git clone https://github.com/ArioBara/bspwm-dotfiles.git ~/bspwm-dotfiles
cd ~/bspwm-dotfiles
chmod +x install.sh
./install.sh
```

Script `install.sh` akan otomatis mem-backup konfigurasi lama Anda ke `~/.config-backup-<timestamp>`, menyalin seluruh file `.config`, `.themes`, `Scripts`, `.local`, serta membuat seluruh *symlink* di `~/.local/bin`.
