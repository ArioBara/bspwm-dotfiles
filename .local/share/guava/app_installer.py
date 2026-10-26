#!/usr/bin/env python3
"""
Script Installer Aplikasi Desktop & Ricing untuk Linux (Mint / Ubuntu / Debian).
Menyediakan katalog lengkap aplikasi multimedia, grafis, produktivitas, dev tools,
serta utilitas ricing/kustomisasi desktop menggunakan package manager APT.
"""

import os
import shutil
import subprocess
import sys
import time
import unicodedata

# Definisi Tema Catppuccin Mocha & ANSI Styling (Ricing Style)
class Theme:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    UNDERLINE = "\033[4m"

    # Borders & Chrome
    BORDER  = "\033[38;5;60m"   # Slate Blue / Dark Lavender
    DIVIDER = "\033[38;5;238m"  # Subtle Gray

    # Catppuccin Accents
    HEADER  = "\033[38;5;183m"  # Soft Mauve
    CYAN    = "\033[38;5;81m"   # Sky Cyan
    BLUE    = "\033[38;5;111m"  # Soft Blue
    PEACH   = "\033[38;5;216m"  # Soft Peach
    MINT    = "\033[38;5;120m"  # Mint Green
    LIME    = "\033[38;5;119m"  # Lime Green
    GREEN   = "\033[38;5;120m"  # Mint Green
    YELLOW  = "\033[38;5;222m"  # Warm Yellow
    RED     = "\033[38;5;203m"  # Coral Red
    WHITE   = "\033[38;5;255m"  # Bright White
    GRAY    = "\033[38;5;244m"  # Slate Muted Gray
    NUM     = "\033[38;5;153m"  # Pale Sky Blue for Numbers

Colors = Theme

def clear_screen():
    """Membersihkan layar terminal agar tampilan antarmuka tetap bersih dan rapi."""
    print("\033[H\033[J", end="", flush=True)

def get_display_width(text):
    """Menghitung visual cell width teks di terminal (mengabaikan ANSI escape dan menangani emoji wide char)."""
    w = 0
    in_esc = False
    for ch in text:
        if ch == "\033":
            in_esc = True
            continue
        if in_esc:
            if ch == "m":
                in_esc = False
            continue
        if ch == "\ufe0f":
            continue
        if unicodedata.east_asian_width(ch) in ("W", "F") or (0x1F300 <= ord(ch) <= 0x1FAFF):
            w += 2
        else:
            w += 1
    return w

def make_box_top(title, badge="v2.5", total_w=80):
    """Membuat garis atas rounded card dengan title dan badge dinamis."""
    left = f"╭─ {title} "
    right = f" {badge} ─╮" if badge else " ─╮"
    used = get_display_width(left) + get_display_width(right)
    dashes = "─" * max(0, total_w - used)
    return f"{Theme.BORDER}{left}{dashes}{right}{Theme.RESET}"

def print_status_card(title, items, total_w=80):
    """Menampilkan card status berbingkai rounded ricing yang modern."""
    top = make_box_top(title, badge="v2.5", total_w=total_w)
    print(top)
    for label, val, val_color in items:
        prefix = f"  {label:<8}: "
        raw = prefix + str(val)
        dw = get_display_width(raw)
        if dw > total_w - 4:
            max_val_w = total_w - 4 - get_display_width(prefix) - 3
            val_str = str(val)[:max_val_w] + "..."
            raw = prefix + val_str
            dw = get_display_width(raw)
        else:
            val_str = str(val)
        pad = " " * max(0, total_w - 2 - dw)
        print(f"{Theme.BORDER}│{Theme.RESET}{Theme.GRAY}  {label:<8}: {Theme.RESET}{val_color}{val_str}{Theme.RESET}{pad}{Theme.BORDER}│{Theme.RESET}")
    dashes = "─" * (total_w - 2)
    print(f"{Theme.BORDER}╰{dashes}╯{Theme.RESET}\n")

def format_menu_col(num, title, width=37, num_color=Theme.NUM, title_color=Theme.WHITE):
    """Memformat satu kolom item menu dengan alignment visual yang presisi."""
    prefix = f" [{num:>2}] "
    dw = get_display_width(prefix + title)
    pad = " " * max(0, width - dw)
    return f" [{Theme.BOLD}{num_color}{num:>2}{Theme.RESET}] {title_color}{title}{Theme.RESET}{pad}"

def format_app_col(idx, name, installed, width):
    """Memformat item aplikasi dengan status bulatan ricing."""
    prefix = f" [{idx:>2}] "
    dot = f"{Theme.MINT}●{Theme.RESET}" if installed else f"{Theme.GRAY}○{Theme.RESET}"
    max_name_w = width - get_display_width(prefix) - 3
    dw_name = get_display_width(name)
    if dw_name > max_name_w:
        short = name
        while get_display_width(short) > max_name_w - 2:
            short = short[:-1]
        name = short + ".."
        dw_name = get_display_width(name)
    pad = " " * max(0, width - get_display_width(prefix) - dw_name - 2)
    return f" [{Theme.BOLD}{Theme.NUM}{idx:>2}{Theme.RESET}] {Theme.WHITE}{name}{Theme.RESET}{pad}{dot} "

def print_banner():
    """Banner minimal ricing untuk kompatibilitas."""
    print(make_box_top("🍃 LINUX APP & RICING INSTALLER", badge="v2.5"))
    raw_sub = "  Debian / Ubuntu / Linux Mint • Official APT Catalog & Desktop Styling"
    pad_sub = " " * (78 - get_display_width(raw_sub))
    print(f"{Theme.BORDER}│{Theme.RESET}{Theme.GRAY}{raw_sub}{Theme.RESET}{pad_sub}{Theme.BORDER}│{Theme.RESET}")

def is_root():
    """Mengecek apakah script dijalankan sebagai root/superuser."""
    return os.geteuid() == 0 if hasattr(os, "geteuid") else False

def get_sudo_prefix():
    """Mengembalikan prefix sudo jika bukan user root."""
    if is_root():
        return ""
    return "sudo "

def run_cmd(command, check=True, shell=True):
    """Menjalankan perintah terminal dengan penanganan error yang rapi."""
    try:
        return subprocess.run(command, shell=shell, check=check)
    except subprocess.CalledProcessError:
        print(f"\n{Colors.RED}[!] Perintah gagal dieksekusi: {command}{Colors.RESET}")
        return None

def check_linux_env():
    """Memeriksa apakah sistem berjalan di Linux dengan package manager APT."""
    if not sys.platform.startswith("linux"):
        print(f"{Colors.YELLOW}[!] Peringatan: Sistem terdeteksi bukan Linux ({sys.platform}).")
        print(f"    Script ini dirancang khusus untuk Linux / Debian / Ubuntu / Mint.{Colors.RESET}")
        confirm = input("Apakah Anda ingin tetap melanjutkan? (y/n): ").strip().lower()
        if confirm != "y":
            print("[*] Dibatalkan oleh pengguna.")
            sys.exit(0)
        return

    if not shutil.which("apt"):
        print(f"{Colors.RED}[!] Package manager 'apt' tidak ditemukan! Pastikan Anda berada di sistem berbasis Debian/Ubuntu/Mint.{Colors.RESET}")
        sys.exit(1)

def is_app_installed(cmd_or_pkg):
    """Mengecek apakah aplikasi sudah terpasang di sistem."""
    first_pkg = cmd_or_pkg.split()[0]
    if shutil.which(first_pkg):
        return True
    if first_pkg == "chromium" and shutil.which("chromium-browser"):
        return True
    if first_pkg == "chromium-browser" and shutil.which("chromium"):
        return True
    
    # Cek via dpkg-query jika bukan executable di PATH
    try:
        res = subprocess.run(
            f"dpkg -s {first_pkg} 2>/dev/null | grep -q 'Status: install ok installed'",
            shell=True
        )
        return res.returncode == 0
    except Exception:
        return False

def get_app_categories():
    """Daftar lengkap kategori, aplikasi harian, dev tools, dan ricing untuk Linux."""
    return {
        "1": {
            "name": "Pemutar Media, Audio & Video Player",
            "desc": "Aplikasi pemutar video, audio visualizer & editor suara",
            "apps": [
                {"name": "VLC Media Player (Pemutar Video & Audio Serbaguna)", "apt_package": "vlc", "cmd": "vlc"},
                {"name": "MPV (Media Player Modern, Minimalis & Ringan)", "apt_package": "mpv", "cmd": "mpv"},
                {"name": "SMPlayer (GUI Canggih Berbasis MPV dengan Subtitle Downloader)", "apt_package": "smplayer", "cmd": "smplayer"},
                {"name": "Audacious (Music Player Ringan ala Winamp)", "apt_package": "audacious", "cmd": "audacious"},
                {"name": "Rhythmbox (Manajer & Pemutar Koleksi Musik)", "apt_package": "rhythmbox", "cmd": "rhythmbox"},
                {"name": "Strawberry Music Player (Audio Player Berkualitas Tinggi)", "apt_package": "strawberry", "cmd": "strawberry"},
                {"name": "Audacity (Editor & Perekam Audio Multi-track)", "apt_package": "audacity", "cmd": "audacity"}
            ]
        },
        "2": {
            "name": "Video Editor, Transcoder & Screen Recording",
            "desc": "Produksi video, converter format & perekam layar desktop",
            "apps": [
                {"name": "OBS Studio (Screen Recording & Live Streaming)", "apt_package": "obs-studio", "cmd": "obs"},
                {"name": "Kdenlive (Editor Video Profesional & Multi-track)", "apt_package": "kdenlive", "cmd": "kdenlive"},
                {"name": "Shotcut (Video Editor Ringan, Lengkap & Open Source)", "apt_package": "shotcut", "cmd": "shotcut"},
                {"name": "HandBrake (Video Transcoder, Compressor & Formatter)", "apt_package": "handbrake", "cmd": "ghb"},
                {"name": "SimpleScreenRecorder (Perekam Layar Sangat Ringan & Cepat)", "apt_package": "simplescreenrecorder", "cmd": "simplescreenrecorder"},
                {"name": "FFmpeg (Mesin Converter & Processor Video/Audio CLI)", "apt_package": "ffmpeg", "cmd": "ffmpeg"},
                {"name": "MediaInfo GUI (Informasi Detail Metadata File Media)", "apt_package": "mediainfo mediainfo-gui", "cmd": "mediainfo-gui"}
            ]
        },
        "3": {
            "name": "Kalkulator, Keamanan & Utilitas Sistem",
            "desc": "Alat bantu esensial harian, password manager & monitor performa",
            "apps": [
                {"name": "Galculator (Kalkulator Saintifik & Grafis Ringan)", "apt_package": "galculator", "cmd": "galculator"},
                {"name": "SpeedCrunch (Kalkulator Presisi Tinggi dengan History)", "apt_package": "speedcrunch", "cmd": "speedcrunch"},
                {"name": "KeePassXC (Pengelola Password Terenkripsi Offline)", "apt_package": "keepassxc", "cmd": "keepassxc"},
                {"name": "Flameshot (Alat Screenshot Interaktif & Anotasi Terbaik)", "apt_package": "flameshot", "cmd": "flameshot"},
                {"name": "Btop (Resource Monitor Modern, Grafis Terminal Canggih)", "apt_package": "btop", "cmd": "btop"},
                {"name": "Htop (Interactive Process Viewer & Task Manager Ringan)", "apt_package": "htop", "cmd": "htop"},
                {"name": "Fastfetch (Penampil Info Sistem Super Cepat Berbasis C)", "apt_package": "fastfetch", "cmd": "fastfetch"},
                {"name": "Neofetch (Penampil Info Sistem Klasik Berbasis Bash)", "apt_package": "neofetch", "cmd": "neofetch"},
                {"name": "BleachBit (Pembersih Cache, Sampah & Privasi Sistem)", "apt_package": "bleachbit", "cmd": "bleachbit"},
                {"name": "Redshift GUI (Filter Cahaya Biru / Night Light)", "apt_package": "redshift-gtk", "cmd": "redshift-gtk"},
                {"name": "File Roller (Manajer Ekstrak Arsip ZIP, RAR, 7Z GNOME/Mint)", "apt_package": "file-roller p7zip-full unrar", "cmd": "file-roller"},
                {"name": "Xarchiver (Manajer Ekstrak Berkas Arsip Ringan XFCE)", "apt_package": "xarchiver p7zip-full unrar", "cmd": "xarchiver"}
            ]
        },
        "4": {
            "name": "Web Browser & Komunikasi / Chat",
            "desc": "Peramban web modern, email client & aplikasi pesan",
            "apps": [
                {"name": "Brave Browser (Peramban Privasi Cepat dengan Adblock Bawaan)", "apt_package": "brave-browser", "cmd": "brave-browser"},
                {"name": "Firefox (Web Browser Native Cepat & Aman)", "apt_package": "firefox", "cmd": "firefox"},
                {"name": "Chromium Browser (Web Browser Native Cepat Tanpa Snap)", "apt_package": "chromium", "cmd": "chromium"},
                {"name": "Thunderbird (Email Client, Kalender & Kontak)", "apt_package": "thunderbird", "cmd": "thunderbird"},
                {"name": "Telegram Desktop (Aplikasi Chat Cepat & Ringan)", "apt_package": "telegram-desktop", "cmd": "telegram-desktop"},
                {"name": "Tailscale (Mesh VPN, WireGuard P2P & Remote Access)", "apt_package": "tailscale", "cmd": "tailscale"},
                {"name": "qBittorrent (BitTorrent Client Cepat & Bebas Iklan)", "apt_package": "qbittorrent", "cmd": "qbittorrent"},
                {"name": "HexChat (Klien Chat IRC Populer)", "apt_package": "hexchat", "cmd": "hexchat"}
            ]
        },
        "5": {
            "name": "Teks Editor, Catatan, PDF & Office Suite",
            "desc": "Aplikasi produktivitas dokumen, pembaca PDF & text editor",
            "apps": [
                {"name": "LibreOffice Suite Lengkap (Writer, Calc, Impress)", "apt_package": "libreoffice libreoffice-l10n-id", "cmd": "libreoffice"},
                {"name": "Geany (IDE / Text Editor Sangat Ringan & Cepat)", "apt_package": "geany geany-plugins", "cmd": "geany"},
                {"name": "FeatherPad (Text Editor Simpel Berbasis Tab)", "apt_package": "featherpad", "cmd": "featherpad"},
                {"name": "Atril (Pembaca Dokumen & PDF Viewer MATE)", "apt_package": "atril", "cmd": "atril"},
                {"name": "Evince (Pembaca Dokumen & PDF Viewer GNOME)", "apt_package": "evince", "cmd": "evince"},
                {"name": "Zathura (Pembaca PDF Minimalis dengan Navigasi Vim)", "apt_package": "zathura zathura-pdf-poppler", "cmd": "zathura"},
                {"name": "Foliate (Pembaca E-Book Modern dengan Tampilan Nyaman)", "apt_package": "foliate", "cmd": "foliate"}
            ]
        },
        "6": {
            "name": "Grafis, Desain 2D/3D & Manipulasi Gambar",
            "desc": "Alat lukis digital, editor vektor, 3D modeling & pengolah RAW",
            "apps": [
                {"name": "GIMP (GNU Image Manipulation Program / Alternatif Photoshop)", "apt_package": "gimp gimp-plugin-registry", "cmd": "gimp"},
                {"name": "Inkscape (Editor Grafis Vektor Profesional / Alternatif AI)", "apt_package": "inkscape", "cmd": "inkscape"},
                {"name": "Krita (Aplikasi Lukis, Sketsa & Ilustrasi Digital)", "apt_package": "krita", "cmd": "krita"},
                {"name": "Pinta (Editor Gambar Sederhana ala Paint.NET)", "apt_package": "pinta", "cmd": "pinta"},
                {"name": "Blender (Suite Pembuatan 3D, Animasi, Visual Effects)", "apt_package": "blender", "cmd": "blender"},
                {"name": "Darktable (Pengolah Foto Fotografi & RAW Developer)", "apt_package": "darktable", "cmd": "darktable"},
                {"name": "Eye of GNOME / EOG (Image Viewer Standar GNOME)", "apt_package": "eog", "cmd": "eog"},
                {"name": "Ristretto (Image Viewer Cepat & Ringan XFCE)", "apt_package": "ristretto", "cmd": "ristretto"}
            ]
        },
        "7": {
            "name": "Manajemen File, Partisi & Tool Administrator",
            "desc": "Manajer berkas visual, partisi disk & manajemen paket",
            "apps": [
                {"name": "GParted (Manajer & Editor Partisi Harddisk / SSD)", "apt_package": "gparted", "cmd": "gparted"},
                {"name": "GNOME Disks Utility (Cek Kesehatan SMART, Format & Mount Disk)", "apt_package": "gnome-disk-utility", "cmd": "gnome-disks"},
                {"name": "Baobab (Disk Usage Analyzer / Visualisasi Kapasitas Disk)", "apt_package": "baobab", "cmd": "baobab"},
                {"name": "Thunar (File Manager Ringan XFCE + Plugin Archive)", "apt_package": "thunar thunar-archive-plugin", "cmd": "thunar"},
                {"name": "PCManFM (File Manager Super Ringan Alternatif)", "apt_package": "pcmanfm", "cmd": "pcmanfm"},
                {"name": "Synaptic Package Manager (Manajer Paket GUI Terlengkap)", "apt_package": "synaptic", "cmd": "synaptic"}
            ]
        },
        "8": {
            "name": "Pengembangan, Coding & Terminal Dev Tools",
            "desc": "Editor kode, terminal emulator canggih, database GUI & git tools",
            "apps": [
                {"name": "Visual Studio Code (Official Microsoft VSCode Editor)", "apt_package": "code", "cmd": "code"},
                {"name": "VSCodium (Open-Source VS Code Binary Tanpa Telemetri Microsoft)", "apt_package": "vscodium", "cmd": "codium"},
                {"name": "Meld (Alat Visual Komparasi File & Folder Diff Viewer)", "apt_package": "meld", "cmd": "meld"},
                {"name": "Gitg (Klien Visual GUI untuk Repositori Git)", "apt_package": "gitg", "cmd": "gitg"},
                {"name": "Alacritty (Terminal Emulator GPU-Accelerated Super Cepat)", "apt_package": "alacritty", "cmd": "alacritty"},
                {"name": "Kitty (Terminal Emulator Berfitur Lengkap dengan Dukungan Gambar)", "apt_package": "kitty", "cmd": "kitty"},
                {"name": "Tilix (Terminal Multiplexer Canggih Berbasis VTE GTK3)", "apt_package": "tilix", "cmd": "tilix"},
                {"name": "Terminator (Terminal Emulator Multi-window & Split Grid)", "apt_package": "terminator", "cmd": "terminator"},
                {"name": "SQLite Browser (Database Manager GUI untuk SQLite)", "apt_package": "sqlitebrowser", "cmd": "sqlitebrowser"},
                {"name": "HTTPie (Klien HTTP / API Testing Modern & User-friendly)", "apt_package": "httpie", "cmd": "http"},
                {"name": "cURL & Wget (Alat Transfer Data Jaringan & CLI Downloader)", "apt_package": "curl wget", "cmd": "curl"},
                {"name": "ADB & Fastboot (Android Debug Bridge, USB Shell & Flashing)", "apt_package": "adb fastboot android-sdk-platform-tools-common", "cmd": "adb"},
                {"name": "Scrcpy (Screen Mirror & Pengontrol HP Android via USB/WiFi)", "apt_package": "scrcpy adb", "cmd": "scrcpy"},
                {"name": "Fish Shell (Friendly Interactive Shell Modern, Cerdas & Cepat)", "apt_package": "fish", "cmd": "fish"},
                {"name": "Starship Prompt (Cross-Shell Fast Prompt untuk Fish, Bash, Zsh)", "apt_package": "starship", "cmd": "starship"},
                {"name": "Fisher (Plugin Manager Resmi untuk Fish Shell)", "apt_package": "fisher", "cmd": "fisher"},
                {"name": "Modern CLI Tools (Fzf, Ripgrep, Bat, Eza, Zoxide untuk Fish & Bash)", "apt_package": "fzf ripgrep fd-find bat eza zoxide", "cmd": "fzf"}
            ]
        },
        "9": {
            "name": "Ricing & Kustomisasi Desktop Estetika",
            "desc": "Docks, widget monitor, launcher, icon theme & wallpaper setter",
            "apps": [
                {"name": "Plank (Dock Minimalis, Cepat & Elegan)", "apt_package": "plank", "cmd": "plank"},
                {"name": "Conky All (Widget Monitor Sistem di Atas Desktop)", "apt_package": "conky-all", "cmd": "conky"},
                {"name": "Rofi (Application Launcher & Window Switcher yang Sangat Ricing)", "apt_package": "rofi", "cmd": "rofi"},
                {"name": "Nitrogen (Wallpaper Setter & Background Manager Cepat)", "apt_package": "nitrogen", "cmd": "nitrogen"},
                {"name": "Picom (Compositor untuk Efek Blur, Shadow & Transparansi)", "apt_package": "picom", "cmd": "picom"},
                {"name": "Papirus Icon Theme (Paket Ikon Modern Paling Populer di Linux)", "apt_package": "papirus-icon-theme", "cmd": "papirus"},
                {"name": "Arc Theme (Tema Desktop Modern & Elegan)", "apt_package": "arc-theme", "cmd": "arc-theme"}
            ]
        },
        "10": {
            "name": "Server, Web Hosting Panel & Remote Administration",
            "desc": "aaPanel Web GUI, OpenSSH Server, Cockpit Dashboard, Nginx, Certbot SSL, UFW & Net Tools",
            "apps": [
                {"name": "aaPanel (Modern Web Hosting & Server Control Panel GUI)", "apt_package": "aapanel", "cmd": "bt"},
                {"name": "OpenSSH Server & Client (Remote Terminal SSH Server)", "apt_package": "openssh-server openssh-client", "cmd": "sshd"},
                {"name": "Cockpit (Web GUI Manajemen Server & Resource Monitor)", "apt_package": "cockpit cockpit-machines cockpit-networkmanager cockpit-storaged", "cmd": "cockpit"},
                {"name": "Nginx & Certbot (High Performance Web Server & Auto SSL)", "apt_package": "nginx certbot python3-certbot-nginx", "cmd": "nginx"},
                {"name": "Apache2 Web Server (Modular HTTP Server)", "apt_package": "apache2 apache2-utils", "cmd": "apache2"},
                {"name": "UFW & Fail2ban (Firewall & Anti Brute-force Protection)", "apt_package": "ufw fail2ban", "cmd": "ufw"},
                {"name": "Server Diagnostics Suite (Iftop, Iotop, Iperf3, Ncdu, Net-tools, Mosh)", "apt_package": "iftop iotop iperf3 ncdu net-tools mosh wireguard", "cmd": "iftop"}
            ]
        },
        "11": {
            "name": "Pengembangan Game / Game Development & Assets Suite",
            "desc": "Godot Engine 4, Blender 3D, Tiled Map Editor, LÖVE 2D, LMMS Music, SDL2 & Raylib",
            "apps": [
                {"name": "Godot Engine 4 (Modern 2D & 3D Open Source Game Engine)", "apt_package": "godot", "cmd": "godot"},
                {"name": "Blender 3D (3D Modeling, Rigging, Animasi Karakter Game)", "apt_package": "blender", "cmd": "blender"},
                {"name": "Tiled Map Editor (Editor Level & Map 2D Berbasis Tile)", "apt_package": "tiled", "cmd": "tiled"},
                {"name": "LÖVE / Love2D (Framework Game 2D Berbasis Lua Cepat)", "apt_package": "love", "cmd": "love"},
                {"name": "LMMS (Linux MultiMedia Studio / Pembuat BGM & Musik Game)", "apt_package": "lmms", "cmd": "lmms"},
                {"name": "Audacity (Editor SFX & Audio Game Multi-track)", "apt_package": "audacity", "cmd": "audacity"},
                {"name": "SDL2 & Audio Dev Libraries (C/C++ Game Engine SDKs)", "apt_package": "libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libopenal-dev", "cmd": "sdl2-config"},
                {"name": "Steam Client (Distribusi & Pengujian Game)", "apt_package": "steam-installer", "cmd": "steam"}
            ]
        },
        "12": {
            "name": "Kompatibilitas Windows, Wine & Proton Gaming Suite",
            "desc": "Wine 64/32-bit, Winetricks, Lutris, Bottles, PlayOnLinux, DXVK & Vulkan Driver",
            "apps": [
                {"name": "Wine Complete (Wine 64-bit, 32-bit Arch & Libwine Runtime)", "apt_package": "wine-complete", "cmd": "wine"},
                {"name": "Winetricks (Manajer DLL, DirectX, Visual C++ & .NET Runtimes)", "apt_package": "winetricks", "cmd": "winetricks"},
                {"name": "Lutris (Gaming Platform untuk Menjalankan Game Windows & Launcher)", "apt_package": "lutris", "cmd": "lutris"},
                {"name": "Bottles (Pengelola Wine Prefix / Bottle Modern Berbasis GUI)", "apt_package": "bottles", "cmd": "bottles"},
                {"name": "PlayOnLinux (Antarmuka Grafis Klasik untuk Instalasi Aplikasi Windows)", "apt_package": "playonlinux", "cmd": "playonlinux"},
                {"name": "Q4Wine (GUI Manajemen Wine Berbasis Qt)", "apt_package": "q4wine", "cmd": "q4wine"},
                {"name": "Vulkan & DXVK Driver (Mesin Akselerasi DirectX ke Vulkan 32/64-bit)", "apt_package": "vulkan-driver", "cmd": "vulkaninfo"}
            ]
        },
        "13": {
            "name": "Konektivitas HP & PC, Screen Sharing & Utilitas Remote",
            "desc": "LocalSend, KDE Connect, Deskreen Second Screen, DroidCam Webcam, RustDesk, AudioRelay & WARP",
            "apps": [
                {"name": "LocalSend (Berbagi File LAN Antar Perangkat / Alternatif AirDrop Bebas Iklan)", "apt_package": "localsend", "cmd": "localsend"},
                {"name": "KDE Connect (Sinkronisasi Notifikasi, Clipboard, Media & Input HP-PC)", "apt_package": "kdeconnect indicator-kdeconnect", "cmd": "kdeconnect-app"},
                {"name": "Deskreen (Ubah HP / Tablet / Laptop Apa Saja Jadi Layar Kedua PC)", "apt_package": "deskreen", "cmd": "deskreen"},
                {"name": "DroidCam (Jadikan Kamera & Mic HP Sebagai Webcam PC HD via USB/WiFi)", "apt_package": "droidcam", "cmd": "droidcam"},
                {"name": "RustDesk (Remote Desktop & Akses Jarak Jauh Open Source / Alternatif AnyDesk)", "apt_package": "rustdesk", "cmd": "rustdesk"},
                {"name": "AudioRelay (Streaming Suara Audio dari PC ke HP atau Sebaliknya)", "apt_package": "audiorelay", "cmd": "audiorelay"},
                {"name": "Cloudflare 1.1.1.1 WARP (DNS & VPN Client Cepat dan Aman)", "apt_package": "cloudflare-warp", "cmd": "warp-cli"}
            ]
        }
    }

def install_packages(apt_pkg_string, item_name):
    """Menjalankan perintah instalasi apt untuk paket yang dipilih dengan pembersihan layar ricing."""
    sudo = get_sudo_prefix()
    
    # 1. Bersihkan layar segera agar menu sebelumnya tidak bertumpuk
    clear_screen()
    
    # 2. Tampilkan status card awal
    pkg_display = apt_pkg_string if len(apt_pkg_string) <= 52 else apt_pkg_string[:49] + "..."
    print_status_card("📦 PROSES INSTALASI", [
        ("Target", item_name, Theme.BOLD + Theme.WHITE),
        ("Paket", pkg_display, Theme.CYAN),
        ("Status", "Menyiapkan repositori & memasang paket via APT...", Theme.PEACH)
    ])

    # Penanganan khusus repositori & binary pihak ketiga
    if "starship" in apt_pkg_string.split():
        fish_cfg_dir = os.path.expanduser("~/.config/fish")
        os.makedirs(fish_cfg_dir, exist_ok=True)
        cmd_starship = (
            f"{sudo}apt install -y curl && "
            f"curl -sS https://starship.rs/install.sh | sh -s -- -y && "
            f"(grep -q 'starship init fish' ~/.config/fish/config.fish 2>/dev/null || echo -e '\\n# Starship Prompt\\nstarship init fish | source' >> ~/.config/fish/config.fish) && "
            f"(grep -q 'starship init bash' ~/.bashrc 2>/dev/null || echo -e '\\n# Starship Prompt\\neval \"$(starship init bash)\"' >> ~/.bashrc)"
        )
        res = run_cmd(cmd_starship)
    elif "fisher" in apt_pkg_string.split():
        cmd_fisher = (
            f"{sudo}apt update -y && {sudo}apt install -y curl fish && "
            f"fish -c 'curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher'"
        )
        res = run_cmd(cmd_fisher)
    elif "localsend" in apt_pkg_string:
        cmd_ls = (
            f"{sudo}apt install -y curl && "
            f"LS_URL=$(curl -s https://api.github.com/repos/localsend/localsend/releases/latest | grep 'browser_download_url.*linux-x86-64.deb' | cut -d '\"' -f 4) && "
            f"curl -fsSL \"$LS_URL\" -o /tmp/localsend.deb && ({sudo}apt install -y /tmp/localsend.deb || flatpak install -y flathub org.localsend.localsend_app) && rm -f /tmp/localsend.deb"
        )
        res = run_cmd(cmd_ls)
    elif "deskreen" in apt_pkg_string:
        cmd_ds = (
            f"{sudo}apt install -y curl && "
            f"DS_URL=$(curl -s https://api.github.com/repos/pavlobu/deskreen/releases/latest | grep 'browser_download_url.*deb' | head -n 1 | cut -d '\"' -f 4) && "
            f"curl -fsSL \"$DS_URL\" -o /tmp/deskreen.deb && ({sudo}apt install -y /tmp/deskreen.deb || flatpak install -y flathub com.github.pavlobu.deskreen) && rm -f /tmp/deskreen.deb"
        )
        res = run_cmd(cmd_ds)
    elif "droidcam" in apt_pkg_string:
        cmd_dc = f"{sudo}apt update -y && ({sudo}apt install -y droidcam v4l2loopback-dkms libappindicator3-1 || {sudo}apt install -y droidcam)"
        res = run_cmd(cmd_dc)
    elif "rustdesk" in apt_pkg_string:
        cmd_rd = (
            f"{sudo}apt install -y curl && "
            f"RD_URL=$(curl -s https://api.github.com/repos/rustdesk/rustdesk/releases/latest | grep 'browser_download_url.*x86_64.deb' | head -n 1 | cut -d '\"' -f 4) && "
            f"curl -fsSL \"$RD_URL\" -o /tmp/rustdesk.deb && {sudo}apt install -y /tmp/rustdesk.deb && rm -f /tmp/rustdesk.deb"
        )
        res = run_cmd(cmd_rd)
    elif "audiorelay" in apt_pkg_string:
        cmd_ar = (
            f"{sudo}apt install -y curl && "
            f"curl -fsSL 'https://dl.audiorelay.net/setups/linux/audiorelay-0.27.5.deb' -o /tmp/audiorelay.deb && "
            f"{sudo}apt install -y /tmp/audiorelay.deb && rm -f /tmp/audiorelay.deb"
        )
        res = run_cmd(cmd_ar)
    elif "cloudflare-warp" in apt_pkg_string:
        cmd_warp = (
            f"{sudo}apt install -y curl gpg lsb-release && "
            f"curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | {sudo}gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg && "
            f"echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ '\"$(lsb_release -cs 2>/dev/null || echo bookworm)\"' main' | {sudo}tee /etc/apt/sources.list.d/cloudflare-warp.list > /dev/null && "
            f"{sudo}apt update -y && {sudo}apt install -y cloudflare-warp"
        )
        res = run_cmd(cmd_warp)
    elif "wine-complete" in apt_pkg_string:
        cmd_wine = f"{sudo}dpkg --add-architecture i386 && {sudo}apt update -y && {sudo}apt install -y wine wine64 wine32 libwine libwine:i386 winetricks"
        res = run_cmd(cmd_wine)
    elif "vulkan-driver" in apt_pkg_string:
        cmd_vulkan = f"{sudo}dpkg --add-architecture i386 && {sudo}apt update -y && {sudo}apt install -y vulkan-tools libvulkan1 libvulkan1:i386 mesa-vulkan-drivers mesa-vulkan-drivers:i386"
        res = run_cmd(cmd_vulkan)
    elif "bottles" in apt_pkg_string:
        res = run_cmd(f"flatpak install -y flathub com.usebottles.bottles 2>/dev/null || ({sudo}apt update -y && {sudo}apt install -y bottles)")
    elif "chromium" in apt_pkg_string.split():
        installer_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "installer", "chromium.txt")
        if not os.path.exists(installer_script):
            installer_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "installer", "chromium.txt")
        
        if os.path.exists(installer_script):
            res = run_cmd(f"bash '{installer_script}'")
        else:
            cmd_chromium = (
                f"if apt-cache policy chromium 2>/dev/null | grep -q 'packages.linuxmint.com'; then "
                f"{sudo}apt update -y && {sudo}apt install -y chromium; "
                f"else "
                f"{sudo}add-apt-repository -y ppa:xtradeb/apps 2>/dev/null || true; "
                f"{sudo}apt update -y && {sudo}apt install -y chromium; "
                f"fi"
            )
            res = run_cmd(cmd_chromium)
    elif "brave-browser" in apt_pkg_string:
        cmd_brave = (
            f"{sudo}apt install -y curl && "
            f"{sudo}curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg && "
            f"echo 'deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main' | {sudo}tee /etc/apt/sources.list.d/brave-browser-release.list > /dev/null && "
            f"{sudo}apt update -y && {sudo}apt install -y brave-browser"
        )
        res = run_cmd(cmd_brave)
    elif "godot" in apt_pkg_string:
        cmd_godot = (
            f"{sudo}apt install -y curl unzip && "
            f"GODOT_URL=$(curl -s https://api.github.com/repos/godotengine/godot/releases/latest | grep 'browser_download_url.*linux.x86_64.zip' | cut -d '\"' -f 4) && "
            f"curl -fsSL \"$GODOT_URL\" -o /tmp/godot.zip && unzip -o /tmp/godot.zip -d /tmp/godot_bin && "
            f"{sudo}install /tmp/godot_bin/Godot* /usr/local/bin/godot && rm -rf /tmp/godot.zip /tmp/godot_bin || {sudo}apt install -y godot3"
        )
        res = run_cmd(cmd_godot)
    elif "aapanel" in apt_pkg_string:
        cmd_aapanel = "URL=https://www.aapanel.com/script/install_6.0_en.sh && if [ -f /usr/bin/curl ];then curl -ksSO \"$URL\" ;else wget --no-check-certificate -O install_6.0_en.sh \"$URL\";fi;sudo bash install_6.0_en.sh aapanel"
        res = run_cmd(cmd_aapanel)
    elif "tailscale" in apt_pkg_string:
        res = run_cmd(f"curl -fsSL https://tailscale.com/install.sh | sh || ({sudo}apt update -y && {sudo}apt install -y {apt_pkg_string})")
    elif "code" in apt_pkg_string.split():
        cmd_vscode = (
            f"{sudo}apt update -y && {sudo}apt install -y wget gpg apt-transport-https && "
            f"wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | {sudo}tee /usr/share/keyrings/packages.microsoft.gpg > /dev/null && "
            f"echo 'deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main' | {sudo}tee /etc/apt/sources.list.d/vscode.list > /dev/null && "
            f"{sudo}apt update -y && {sudo}apt install -y code"
        )
        res = run_cmd(cmd_vscode)
    elif "vscodium" in apt_pkg_string:
        cmd_vscodium = (
            f"{sudo}apt update -y && {sudo}apt install -y wget gpg apt-transport-https && "
            f"wget -qO - https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/raw/master/pub.gpg | gpg --dearmor | {sudo}tee /usr/share/keyrings/vscodium.gpg > /dev/null && "
            f"echo 'deb [ signed-by=/usr/share/keyrings/vscodium.gpg ] https://download.vscodium.com/debs vscodium main' | {sudo}tee /etc/apt/sources.list.d/vscodium.list > /dev/null && "
            f"{sudo}apt update -y && {sudo}apt install -y vscodium"
        )
        res = run_cmd(cmd_vscodium)
    else:
        res = run_cmd(f"{sudo}apt update -y && {sudo}apt install -y {apt_pkg_string}")

    # Jika openssh-server diinstal, pastikan service langsung aktif
    if "openssh-server" in apt_pkg_string:
        run_cmd(f"{sudo}systemctl enable --now ssh 2>/dev/null")

    # Jika fish shell diinstal, siapkan direktori konfigurasi
    if "fish" in apt_pkg_string.split():
        os.makedirs(os.path.expanduser("~/.config/fish/conf.d"), exist_ok=True)
        os.makedirs(os.path.expanduser("~/.config/fish/functions"), exist_ok=True)

    print()
    if res is not None and res.returncode == 0:
        print_status_card("✨ INSTALASI BERHASIL", [
            ("Target", item_name, Theme.BOLD + Theme.WHITE),
            ("Status", "● Paket berhasil terpasang di sistem", Theme.MINT)
        ])
        input(f" {Theme.PEACH}◆ Tekan [ENTER] untuk kembali ke menu...{Theme.RESET}")
        return True
    else:
        print_status_card("⚠️ INSTALASI TERKENDALA", [
            ("Target", item_name, Theme.BOLD + Theme.WHITE),
            ("Status", "● Terjadi kendala saat instalasi (Cek log di atas)", Theme.RED)
        ])
        input(f" {Theme.PEACH}◆ Tekan [ENTER] untuk kembali ke menu...{Theme.RESET}")
        return False

def show_subcategory_menu(cat_key, cat_data):
    """Menampilkan submenu aplikasi dalam format 2 kolom rounded box ricing."""
    apps = cat_data["apps"]
    w1, w2 = 37, 40
    d1 = "─" * w1
    d2 = "─" * w2
    
    # Format nama kategori untuk prompt
    cat_slug = cat_data["name"].split(",")[0].split("/")[0].strip().lower().replace(" ", "-")

    while True:
        clear_screen()
        top_title = f"📦 {cat_data['name'].upper()}"
        if get_display_width(top_title) > 65:
            top_title = top_title[:62] + "..."
        print(make_box_top(top_title, badge=f"Kat {cat_key}"))

        stat_text = f"  Status: {Theme.MINT}● Terpasang{Theme.RESET}   {Theme.GRAY}○ Belum Terpasang{Theme.RESET}"
        raw_stat = "  Status: ● Terpasang   ○ Belum Terpasang"
        pad_stat = " " * (78 - get_display_width(raw_stat))
        print(f"{Theme.BORDER}│{Theme.RESET}{stat_text}{pad_stat}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}├{d1}┬{d2}┤{Theme.RESET}")

        for i in range(0, len(apps), 2):
            idx1 = i + 1
            app1 = apps[i]
            short1 = app1["name"].split(" (")[0].strip()
            inst1 = is_app_installed(app1.get("cmd", app1["apt_package"]))
            col1 = format_app_col(idx1, short1, inst1, w1)

            if i + 1 < len(apps):
                idx2 = i + 2
                app2 = apps[i + 1]
                short2 = app2["name"].split(" (")[0].strip()
                inst2 = is_app_installed(app2.get("cmd", app2["apt_package"]))
                col2 = format_app_col(idx2, short2, inst2, w2)
            else:
                col2 = " " * w2
            print(f"{Theme.BORDER}│{Theme.RESET}{col1}{Theme.BORDER}│{Theme.RESET}{col2}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}├{d1}┼{d2}┤{Theme.RESET}")
        colA = format_menu_col("A", "Pasang Semua di Kategori", width=w1, num_color=Theme.CYAN)
        col0 = format_menu_col("0", "Kembali ke Menu Utama", width=w2, num_color=Theme.RED)
        print(f"{Theme.BORDER}│{Theme.RESET}{colA}{Theme.BORDER}│{Theme.RESET}{col0}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}╰{d1}┴{d2}╯{Theme.RESET}")

        choice = input(f"\n {Theme.MINT}◆{Theme.RESET} {Theme.CYAN}guava{Theme.RESET} {Theme.GRAY}›{Theme.RESET} {Theme.PEACH}{cat_slug}{Theme.RESET} {Theme.CYAN}❯{Theme.RESET} ").strip()

        if choice == "0":
            break
        elif choice.upper() == "A":
            all_pkgs = " ".join([a["apt_package"] for a in apps])
            install_packages(all_pkgs, f"Semua Aplikasi di '{cat_data['name']}'")
            break
        elif choice.isdigit():
            val = int(choice)
            if 1 <= val <= len(apps):
                selected = apps[val - 1]
                short_name = selected["name"].split(" (")[0].strip()
                install_packages(selected["apt_package"], short_name)
            else:
                print(f" {Theme.RED}[!] Nomor di luar jangkauan (1-{len(apps)}).{Theme.RESET}")
                time.sleep(1)
        else:
            print(f" {Theme.RED}[!] Pilihan '{choice}' tidak valid.{Theme.RESET}")
            time.sleep(1)

def install_preset(preset_type):
    """Menginstal paket bundel rekomendasi siap pakai."""
    presets = {
        "1": {
            "name": "Paket Produktivitas & Multimedia Harian",
            "desc": "VLC, Flameshot, Galculator, SpeedCrunch, KeePassXC, Firefox, Geany, Thunar, File Roller, Btop, Fastfetch",
            "apt_packages": "vlc flameshot galculator speedcrunch keepassxc firefox geany thunar thunar-archive-plugin file-roller p7zip-full unrar btop fastfetch"
        },
        "2": {
            "name": "Paket Desain Grafis & Kreator Konten",
            "desc": "GIMP, Inkscape, Krita, Pinta, OBS Studio, HandBrake, Kdenlive, Audacity, Darktable",
            "apt_packages": "gimp gimp-plugin-registry inkscape krita pinta obs-studio handbrake kdenlive audacity darktable"
        },
        "3": {
            "name": "Paket Developer & Power User Essentials",
            "desc": "VS Code, Meld, Gitg, SQLiteBrowser, Alacritty, Tilix, Btop, HTTPie, cURL, Wget, Git, Build Essential, ADB, Scrcpy, Tailscale",
            "apt_packages": "code meld gitg sqlitebrowser alacritty tilix btop httpie curl wget git build-essential adb fastboot scrcpy tailscale"
        },
        "4": {
            "name": "Paket Ricing & Kustomisasi Desktop Lengkap",
            "desc": "Plank Dock, Conky All, Rofi, Nitrogen, Picom, Papirus Icon Theme, Arc Theme, Fastfetch",
            "apt_packages": "plank conky-all rofi nitrogen picom papirus-icon-theme arc-theme fastfetch"
        },
        "5": {
            "name": "Paket Server & Remote Admin Essentials",
            "desc": "OpenSSH Server, Nginx, Certbot SSL, UFW Firewall, Fail2ban, Cockpit GUI & Network Diagnostics",
            "apt_packages": "openssh-server openssh-client nginx certbot python3-certbot-nginx ufw fail2ban cockpit cockpit-machines cockpit-networkmanager cockpit-storaged iftop iotop iperf3 ncdu net-tools mosh wireguard"
        },
        "6": {
            "name": "Paket Game Developer Suite Lengkap",
            "desc": "Godot Engine 4, Blender 3D, Tiled Map Editor, Love2D, LMMS, Audacity, SDL2 Game Dev Libraries",
            "apt_packages": "godot blender tiled love lmms audacity libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libopenal-dev"
        },
        "7": {
            "name": "Paket Kompatibilitas Windows & Gaming",
            "desc": "Wine 64/32-bit Lengkap, Winetricks, Lutris, PlayOnLinux, Vulkan & DXVK Driver",
            "apt_packages": "wine-complete winetricks lutris playonlinux vulkan-driver"
        },
        "8": {
            "name": "Paket Konektivitas HP, Screen Mirror & Remote Hub",
            "desc": "LocalSend, KDE Connect, Deskreen Second Screen, DroidCam Webcam, RustDesk, Tailscale, Scrcpy",
            "apt_packages": "localsend kdeconnect indicator-kdeconnect deskreen droidcam rustdesk audiorelay tailscale scrcpy"
        }
    }

    if preset_type in presets:
        selected = presets[preset_type]
        install_packages(selected["apt_packages"], selected["name"])

def show_preset_menu():
    """Menampilkan menu paket rekomendasi / bundel instan."""
    preset_items = [
        ("1", "Produktivitas & Multimedia"),
        ("2", "Desain Grafis & Konten"),
        ("3", "Developer Essentials"),
        ("4", "Ricing & Desktop Mod"),
        ("5", "Server & Remote Admin"),
        ("6", "Game Developer Suite"),
        ("7", "Wine & Windows Gaming"),
        ("8", "Konektivitas HP & Remote")
    ]
    w1, w2 = 37, 40
    d1 = "─" * w1
    d2 = "─" * w2

    while True:
        clear_screen()
        print(make_box_top("⚡ BUNDEL PRESET REKOMENDASI", badge="v2.5"))
        raw_sub = "  Paket Kurasi Siap Pakai untuk Produktivitas, Kreator & Ricing"
        pad_sub = " " * (78 - get_display_width(raw_sub))
        print(f"{Theme.BORDER}│{Theme.RESET}{Theme.GRAY}{raw_sub}{Theme.RESET}{pad_sub}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}├{d1}┬{d2}┤{Theme.RESET}")

        for i in range(0, len(preset_items), 2):
            num1, title1 = preset_items[i]
            col1 = format_menu_col(num1, title1, width=w1, num_color=Theme.MINT, title_color=Theme.BOLD)
            num2, title2 = preset_items[i + 1]
            col2 = format_menu_col(num2, title2, width=w2, num_color=Theme.MINT, title_color=Theme.BOLD)
            print(f"{Theme.BORDER}│{Theme.RESET}{col1}{Theme.BORDER}│{Theme.RESET}{col2}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}├{d1}┼{d2}┤{Theme.RESET}")
        col0 = format_menu_col("0", "Kembali ke Menu Utama", width=w1, num_color=Theme.RED)
        col_empty = " " * w2
        print(f"{Theme.BORDER}│{Theme.RESET}{col0}{Theme.BORDER}│{Theme.RESET}{col_empty}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}╰{d1}┴{d2}╯{Theme.RESET}")

        choice = input(f"\n {Theme.MINT}◆{Theme.RESET} {Theme.CYAN}guava{Theme.RESET} {Theme.GRAY}›{Theme.RESET} {Theme.PEACH}presets{Theme.RESET} {Theme.CYAN}❯{Theme.RESET} ").strip()
        if choice == "0":
            break
        elif choice in ["1", "2", "3", "4", "5", "6", "7", "8"]:
            install_preset(choice)
            break
        else:
            print(f" {Theme.RED}[!] Pilihan tidak valid.{Theme.RESET}")
            time.sleep(1)

def show_main_menu():
    """Menampilkan antarmuka pemilihan menu utama dalam rounded box ricing."""
    categories = get_app_categories()

    category_titles = [
        ("1", "🎬 Media & Audio Player"),
        ("2", "🎥 Video Editor & Recording"),
        ("3", "🛡️ Keamanan & Utilitas Sistem"),
        ("4", "🌐 Web Browser & Komunikasi"),
        ("5", "📝 Teks Editor & Dokumen"),
        ("6", "🎨 Grafis & Desain 2D/3D"),
        ("7", "📁 Manajemen File & Partisi"),
        ("8", "💻 Coding & Dev Tools"),
        ("9", "🎐 Desktop Ricing Estetika"),
        ("10", "🖥️ Server & Remote Admin"),
        ("11", "🎮 Game Development Suite"),
        ("12", "🍷 Wine & Windows Gaming"),
        ("13", "📱 Konektivitas HP & Remote")
    ]
    w1, w2 = 37, 40
    d1 = "─" * w1
    d2 = "─" * w2

    while True:
        clear_screen()
        print(make_box_top("🍃 LINUX APP & RICING INSTALLER", badge="v2.5"))
        raw_sub = "  Debian / Ubuntu / Linux Mint • Official APT Catalog & Desktop Styling"
        pad_sub = " " * (78 - get_display_width(raw_sub))
        print(f"{Theme.BORDER}│{Theme.RESET}{Theme.GRAY}{raw_sub}{Theme.RESET}{pad_sub}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}├{d1}┬{d2}┤{Theme.RESET}")

        for i in range(0, len(category_titles), 2):
            num1, title1 = category_titles[i]
            col1 = format_menu_col(num1, title1, width=w1, num_color=Theme.MINT, title_color=Theme.BOLD)
            if i + 1 < len(category_titles):
                num2, title2 = category_titles[i + 1]
                col2 = format_menu_col(num2, title2, width=w2, num_color=Theme.MINT, title_color=Theme.BOLD)
            else:
                col2 = " " * w2
            print(f"{Theme.BORDER}│{Theme.RESET}{col1}{Theme.BORDER}│{Theme.RESET}{col2}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}├{d1}┼{d2}┤{Theme.RESET}")

        ctrls = [
            ("P", "Bundel Preset Rekomendasi"),
            ("U", "Perbarui Repositori APT"),
            ("0", "Keluar dari Installer")
        ]

        for i in range(0, len(ctrls), 2):
            k1, label1 = ctrls[i]
            col1 = format_menu_col(k1, label1, width=w1, num_color=Theme.CYAN if k1 != "0" else Theme.RED)
            if i + 1 < len(ctrls):
                k2, label2 = ctrls[i + 1]
                col2 = format_menu_col(k2, label2, width=w2, num_color=Theme.CYAN if k2 != "0" else Theme.RED)
            else:
                col2 = " " * w2
            print(f"{Theme.BORDER}│{Theme.RESET}{col1}{Theme.BORDER}│{Theme.RESET}{col2}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}╰{d1}┴{d2}╯{Theme.RESET}")

        max_cat = len(categories)
        choice = input(f"\n {Theme.MINT}◆{Theme.RESET} {Theme.CYAN}guava{Theme.RESET} {Theme.GRAY}›{Theme.RESET} {Theme.PEACH}app-installer{Theme.RESET} {Theme.CYAN}❯{Theme.RESET} ").strip()

        if choice == "0":
            print(f"\n {Theme.MINT}[*] Sampai jumpa! Selamat menikmati aplikasi di Linux.{Theme.RESET}\n")
            break
        elif choice in categories:
            show_subcategory_menu(choice, categories[choice])
        elif choice.upper() == "P":
            show_preset_menu()
        elif choice.upper() == "U":
            sudo = get_sudo_prefix()
            clear_screen()
            print_status_card("🔄 PEMBARUAN SISTEM", [
                ("Tindakan", "APT Update & Upgrade", Theme.BOLD + Theme.WHITE),
                ("Status", "Memperbarui repositori dan indeks paket Linux...", Theme.PEACH)
            ])
            run_cmd(f"{sudo}apt update -y && {sudo}apt upgrade -y")
            print()
            print_status_card("✨ PEMBARUAN SELESAI", [
                ("Status", "● Repositori & paket sistem berhasil diperbarui", Theme.MINT)
            ])
            input(f" {Theme.PEACH}◆ Tekan [ENTER] untuk kembali ke menu utama...{Theme.RESET}")
        else:
            print(f" {Theme.RED}[!] Pilihan '{choice}' tidak valid. Silakan coba lagi.{Theme.RESET}")
            time.sleep(1)

def main():
    """Fungsi utama program."""
    check_linux_env()
    show_main_menu()

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n{Colors.YELLOW}[*] Program dihentikan oleh pengguna.{Colors.RESET}")
        sys.exit(0)
