#!/usr/bin/env python3
"""
Mencadangkan file konfigurasi (~/.config, ~/.config/fish, ~/.bashrc, ~/.zshrc, dconf), daftar paket APT/Flatpak,
ekstensi VSCode, serta menyediakan fitur Restore otomatis untuk pemulihan sistem yang cepat.
"""

import datetime
import os
import shutil
import subprocess
import sys
import tarfile
import time

import datetime
import os
import shutil
import subprocess
import sys
import tarfile
import time
import unicodedata

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
    """Menghitung visual cell width teks di terminal."""
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
        prefix = f"  {label:<12}: "
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
        print(f"{Theme.BORDER}│{Theme.RESET}{Theme.GRAY}  {label:<12}: {Theme.RESET}{val_color}{val_str}{Theme.RESET}{pad}{Theme.BORDER}│{Theme.RESET}")
    dashes = "─" * (total_w - 2)
    print(f"{Theme.BORDER}╰{dashes}╯{Theme.RESET}\n")

def format_menu_col(num, title, width=37, num_color=Theme.NUM, title_color=Theme.WHITE):
    """Memformat satu kolom item menu dengan alignment visual yang presisi."""
    prefix = f" [{num:>2}] "
    dw = get_display_width(prefix + title)
    pad = " " * max(0, width - dw)
    return f" [{Theme.BOLD}{num_color}{num:>2}{Theme.RESET}] {title_color}{title}{Theme.RESET}{pad}"

def run_cmd(cmd, capture=False):
    try:
        if capture:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return res.stdout.strip()
        else:
            return subprocess.run(cmd, shell=True)
    except Exception:
        return "" if capture else None

def get_existing_backups():
    """Mengambil daftar arsip backup di ~/MintBackups."""
    backup_dir = os.path.expanduser("~/MintBackups")
    if not os.path.isdir(backup_dir):
        return []
    files = [f for f in os.listdir(backup_dir) if f.startswith("system_backup_") and f.endswith(".tar.gz")]
    files.sort(reverse=True)
    res = []
    for f in files:
        p = os.path.join(backup_dir, f)
        sz = os.path.getsize(p) / (1024**2)
        res.append((p, f, sz))
    return res

def create_backup(target_dest=None):
    """Membuat arsip cadangan konfigurasi dan daftar paket sistem."""
    clear_screen()
    home = os.path.expanduser("~")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    default_backup_dir = os.path.join(home, "MintBackups")
    target_dest = default_backup_dir
    os.makedirs(target_dest, exist_ok=True)

    print_status_card("💾 MEMULAI PENCADANGAN", [
        ("Lokasi", target_dest, Theme.CYAN),
        ("Status", "Mengekspor daftar paket & konfigurasi...", Theme.YELLOW),
    ])

    temp_staging = os.path.join(target_dest, f"mint_backup_staging_{timestamp}")
    os.makedirs(temp_staging, exist_ok=True)

    # 1. Ekspor Daftar Paket APT
    apt_file = os.path.join(temp_staging, "installed_apt_packages.list")
    run_cmd(f"dpkg --get-selections > '{apt_file}'")

    # 2. Ekspor Daftar Flatpak
    if shutil.which("flatpak"):
        flatpak_file = os.path.join(temp_staging, "installed_flatpaks.list")
        run_cmd(f"flatpak list --app --columns=application > '{flatpak_file}' 2>/dev/null")

    # 3. Ekspor Ekstensi VSCode / Codium
    for ide in ["code", "codium"]:
        if shutil.which(ide):
            ext_file = os.path.join(temp_staging, f"vscode_extensions_{ide}.list")
            run_cmd(f"{ide} --list-extensions > '{ext_file}' 2>/dev/null")

    # 4. Ekspor Pengaturan Desktop (dconf / Cinnamon / GNOME)
    if shutil.which("dconf"):
        dconf_file = os.path.join(temp_staging, "desktop_dconf_settings.ini")
        run_cmd(f"dconf dump / > '{dconf_file}' 2>/dev/null")

    # 5. Salin Dotfiles Penting
    dotfiles_staging = os.path.join(temp_staging, "dotfiles")
    os.makedirs(dotfiles_staging, exist_ok=True)

    dotfiles_to_copy = [
        ".bashrc", ".zshrc", ".profile", ".gitconfig", ".nanorc",
        ".config/fish", ".config/omf", ".config/starship.toml",
        ".config/kitty", ".config/alacritty", ".config/rofi",
        ".config/picom", ".config/neofetch", ".config/fastfetch",
        ".config/dunst", ".config/btop", ".config/htop"
    ]

    for item in dotfiles_to_copy:
        src = os.path.join(home, item)
        if os.path.exists(src):
            dst = os.path.join(dotfiles_staging, item)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)

    archive_name = f"system_backup_{timestamp}.tar.gz"
    archive_path = os.path.join(target_dest, archive_name)

    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(temp_staging, arcname=f"mint_backup_{timestamp}")

    shutil.rmtree(temp_staging, ignore_errors=True)
    size_mb = os.path.getsize(archive_path) / (1024**2)

    clear_screen()
    print_status_card("✨ PENCADANGAN SELESAI", [
        ("File Arsip", archive_name, Theme.MINT),
        ("Ukuran", f"{size_mb:.2f} MB", Theme.CYAN),
        ("Lokasi", target_dest, Theme.WHITE),
        ("Status", "Backup Siap Dipulihkan", Theme.MINT),
    ])

def restore_backup():
    """Mengembalikan (restore) dotfiles dan menginstal ulang paket dari file arsip."""
    clear_screen()
    home = os.path.expanduser("~")
    backups = get_existing_backups()

    if backups:
        items = []
        for idx, (p, fn, sz) in enumerate(backups[:5], start=1):
            items.append((f"[{idx}] {fn[:22]}", f"{sz:.2f} MB", Theme.WHITE))
        print_status_card("📂 ARSIP BACKUP DITEMUKAN", items)

    try:
        archive_input = input(f" {Theme.BOLD}Pilih nomor arsip atau masukkan path [1-{len(backups)}]: {Theme.RESET}").strip()
    except (KeyboardInterrupt, EOFError):
        return

    if not archive_input:
        return

    if archive_input.isdigit() and 1 <= int(archive_input) <= len(backups):
        archive_path = backups[int(archive_input) - 1][0]
    else:
        archive_path = os.path.abspath(os.path.expanduser(archive_input))

    if not os.path.isfile(archive_path) or not archive_path.endswith(".tar.gz"):
        clear_screen()
        print_status_card("❌ FILE TIDAK VALID", [
            ("Path", archive_path, Theme.RED),
            ("Status", "Bukan file arsip .tar.gz valid", Theme.YELLOW),
        ])
        return

    clear_screen()
    print_status_card("⏳ MEMULIHKAN SISTEM", [
        ("Arsip", os.path.basename(archive_path), Theme.CYAN),
        ("Status", "Mengekstrak dan menerapkan konfigurasi...", Theme.YELLOW),
    ])

    extract_dir = os.path.join(home, f"mint_restore_temp_{int(time.time())}")
    os.makedirs(extract_dir, exist_ok=True)

    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(path=extract_dir)

    subfolders = [os.path.join(extract_dir, f) for f in os.listdir(extract_dir) if os.path.isdir(os.path.join(extract_dir, f))]
    target_root = subfolders[0] if subfolders else extract_dir

    # 1. Restore Dotfiles
    dotfiles_dir = os.path.join(target_root, "dotfiles")
    if os.path.exists(dotfiles_dir):
        for root, dirs, files in os.walk(dotfiles_dir):
            rel = os.path.relpath(root, dotfiles_dir)
            dest_root = os.path.join(home, rel) if rel != "." else home
            os.makedirs(dest_root, exist_ok=True)
            for f in files:
                src_file = os.path.join(root, f)
                dst_file = os.path.join(dest_root, f)
                shutil.copy2(src_file, dst_file)

    # 2. Restore Desktop Dconf Settings
    dconf_file = os.path.join(target_root, "desktop_dconf_settings.ini")
    if os.path.exists(dconf_file) and shutil.which("dconf"):
        run_cmd(f"dconf load / < '{dconf_file}' 2>/dev/null")

    # 3. Restore Flatpak Apps
    flatpak_file = os.path.join(target_root, "installed_flatpaks.list")
    if os.path.exists(flatpak_file) and shutil.which("flatpak"):
        try:
            install_flatpaks = input(f" {Theme.BOLD}Instal ulang paket Flatpak? (y/n): {Theme.RESET}").strip().lower()
            if install_flatpaks == "y":
                with open(flatpak_file, "r") as fl:
                    for line in fl:
                        app = line.strip()
                        if app:
                            run_cmd(f"flatpak install -y flathub {app}")
        except (KeyboardInterrupt, EOFError):
            pass

    shutil.rmtree(extract_dir, ignore_errors=True)

    clear_screen()
    print_status_card("✨ PEMULIHAN SELESAI", [
        ("Dotfiles", "Dipulihkan ke direktori home", Theme.MINT),
        ("Dconf", "Pengaturan desktop diterapkan", Theme.MINT),
        ("Status", "Sistem berhasil dipulihkan", Theme.MINT),
    ])

def main():
    w1 = 37
    w2 = 40

    while True:
        clear_screen()
        print(make_box_top("💾 SYSTEM BACKUP & RESTORE", badge="v2.5", total_w=80))

        # Recent backup preview
        backups = get_existing_backups()
        if backups:
            last_bk = backups[0]
            bk_raw = f"  Backup Terbaru: {last_bk[1][:32]} ({last_bk[2]:.1f} MB)"
            pad_b = " " * max(0, 78 - get_display_width(bk_raw))
            print(f"{Theme.BORDER}│{Theme.RESET}{Theme.PEACH}  Backup Terbaru: {Theme.MINT}{last_bk[1][:32]}{Theme.RESET}{Theme.GRAY} ({last_bk[2]:.1f} MB){Theme.RESET}{pad_b}{Theme.BORDER}│{Theme.RESET}")
        else:
            msg = "  (Belum ada file backup di ~/MintBackups)"
            pad_b = " " * max(0, 78 - get_display_width(msg))
            print(f"{Theme.BORDER}│{Theme.RESET}{Theme.GRAY}{msg}{Theme.RESET}{pad_b}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}├{'─'*w1}┬{'─'*w2}┤{Theme.RESET}")

        m1 = format_menu_col("1", "Buat Cadangan Baru", w1, Theme.MINT, Theme.WHITE)
        m2 = format_menu_col("2", "Pulihkan Sistem (Restore)", w2, Theme.PEACH, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{m1}{Theme.BORDER}│{Theme.RESET}{m2}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}├{'─'*w1}┴{'─'*w2}┤{Theme.RESET}")
        m0 = format_menu_col("0", "Kembali ke Menu Utama", 78, Theme.RED, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{m0}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}╰{'─'*78}╯{Theme.RESET}")

        try:
            choice = input(f"\n {Theme.BOLD}{Theme.PEACH}◆ guava{Theme.RESET} › {Theme.CYAN}sys-backup{Theme.RESET} ❯ ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if choice == "0":
            break
        elif choice == "1":
            create_backup()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "2":
            restore_backup()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n{Theme.PEACH}[*] Operasi dibatalkan.{Theme.RESET}")
        sys.exit(0)

