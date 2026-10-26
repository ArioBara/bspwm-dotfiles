#!/usr/bin/env python3
"""
System Cleaner & Junk Remover Mendalam untuk Linux.
Membersihkan cache APT, log systemd journal, cache Flatpak/Snap, cache thumbnail & browser,
artefak build Docker/Pip/NPM/Cargo, file tempat sampah (Trash), dan kernel lama yang tidak terpakai.
"""

import os
import shutil
import subprocess
import sys
import time

import os
import shutil
import subprocess
import sys
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

def get_sudo_prefix():
    return "" if (hasattr(os, "geteuid") and os.geteuid() == 0) else "sudo "

def run_cmd(cmd, capture=False):
    try:
        if capture:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return res.stdout.strip()
        else:
            return subprocess.run(cmd, shell=True)
    except Exception:
        return "" if capture else None

def get_disk_free_gb():
    """Mengambil sisa ruang disk di partisi root dalam satuan GB."""
    try:
        stat = shutil.disk_usage("/")
        return stat.free / (1024**3)
    except Exception:
        return 0.0

def clean_apt_packages():
    """Membersihkan cache paket instalasi APT dan paket yatim piatu."""
    clear_screen()
    print_status_card("🧹 MEMBERSIHKAN APT", [
        ("Target", "Cache paket APT & dependensi yatim", Theme.CYAN),
        ("Status", "Menjalankan autoclean & autoremove...", Theme.YELLOW),
    ])
    sudo = get_sudo_prefix()
    run_cmd(f"{sudo}apt-get clean -y")
    run_cmd(f"{sudo}apt-get autoclean -y")
    run_cmd(f"{sudo}apt-get autoremove --purge -y")
    print_status_card("✨ APT SELESAI", [
        ("Status", "Cache APT & dependensi yatim telah dibersihkan", Theme.MINT),
    ])

def clean_systemd_journal():
    """Memotong log journal systemd yang terlalu besar/lama."""
    clear_screen()
    print_status_card("🧹 SYSTEMD JOURNAL", [
        ("Target", "Log systemd journal > 3 hari atau > 100MB", Theme.CYAN),
        ("Status", "Memangkas berkas log...", Theme.YELLOW),
    ])
    sudo = get_sudo_prefix()
    run_cmd(f"{sudo}journalctl --vacuum-time=3d")
    run_cmd(f"{sudo}journalctl --vacuum-size=100M")
    print_status_card("✨ JOURNAL SELESAI", [
        ("Status", "Log systemd berhasil dirapikan", Theme.MINT),
    ])

def clean_user_caches():
    """Membersihkan folder cache pengguna dan cache thumbnail."""
    clear_screen()
    print_status_card("🧹 CACHE PENGGUNA", [
        ("Target", "Cache thumbnail, browser & shell", Theme.CYAN),
        ("Status", "Menghapus direktori cache usang...", Theme.YELLOW),
    ])
    home = os.path.expanduser("~")
    
    thumb_dirs = [
        os.path.join(home, ".cache", "thumbnails"),
        os.path.join(home, ".thumbnails")
    ]
    for td in thumb_dirs:
        if os.path.exists(td):
            shutil.rmtree(td, ignore_errors=True)
            os.makedirs(td, exist_ok=True)

    cache_dir = os.path.join(home, ".cache")
    if os.path.exists(cache_dir):
        safe_clean_targets = ["google-chrome", "mozilla", "chromium", "pip", "yarn", "npm", "uv", "fontconfig", "mesa_shader_cache", "gstreamer-1.0", "fish"]
        for target in safe_clean_targets:
            tp = os.path.join(cache_dir, target)
            if os.path.exists(tp):
                shutil.rmtree(tp, ignore_errors=True)

    fish_completions = os.path.join(home, ".local", "share", "fish", "generated_completions")
    if os.path.exists(fish_completions):
        shutil.rmtree(fish_completions, ignore_errors=True)
        os.makedirs(fish_completions, exist_ok=True)

    print_status_card("✨ CACHE PENGGUNA BERSIH", [
        ("Status", "Thumbnail, browser & completions dibersihkan", Theme.MINT),
    ])

def clean_flatpak_and_snap():
    """Menghapus runtime Flatpak dan Snap yang sudah tidak digunakan."""
    if shutil.which("flatpak"):
        run_cmd("flatpak uninstall --unused -y 2>/dev/null")
    if shutil.which("snap"):
        run_cmd(r"""LANG=C snap list --all | awk '/disabled/{print $1, $3}' | while read snapname revision; do sudo snap remove "$snapname" --revision="$revision"; done 2>/dev/null""")

def clean_dev_runtimes_cache():
    """Membersihkan cache build tool pengembangan (Pip, NPM, Bun, Cargo, Docker)."""
    clear_screen()
    print_status_card("🧹 CACHE DEVELOPER", [
        ("Target", "Pip, NPM, Bun, Cargo, Docker", Theme.CYAN),
        ("Status", "Menghapus build cache & dangling images...", Theme.YELLOW),
    ])
    
    if shutil.which("pip") or shutil.which("pip3"):
        run_cmd("pip cache purge 2>/dev/null || pip3 cache purge 2>/dev/null")
    if shutil.which("npm"):
        run_cmd("npm cache clean --force 2>/dev/null")
    if shutil.which("yarn"):
        run_cmd("yarn cache clean 2>/dev/null")
    if shutil.which("pnpm"):
        run_cmd("pnpm store prune 2>/dev/null")
    if shutil.which("bun"):
        run_cmd("bun pm cache rm 2>/dev/null")
    if shutil.which("cargo"):
        cargo_cache = os.path.expanduser("~/.cargo/registry/cache")
        if os.path.exists(cargo_cache):
            shutil.rmtree(cargo_cache, ignore_errors=True)
    if shutil.which("docker"):
        run_cmd("docker system prune -f 2>/dev/null")

    print_status_card("✨ CACHE DEVELOPER BERSIH", [
        ("Status", "Seluruh cache package manager & docker dibersihkan", Theme.MINT),
    ])

def clean_trash():
    """Mengosongkan tempat sampah (Trash bin) pengguna."""
    clear_screen()
    print_status_card("🧹 TEMPAT SAMPAH", [
        ("Target", "~/.local/share/Trash", Theme.CYAN),
        ("Status", "Mengosongkan berkas sampah...", Theme.YELLOW),
    ])
    home = os.path.expanduser("~")
    trash_dir = os.path.join(home, ".local", "share", "Trash")
    
    if os.path.exists(trash_dir):
        files_dir = os.path.join(trash_dir, "files")
        info_dir = os.path.join(trash_dir, "info")
        shutil.rmtree(files_dir, ignore_errors=True)
        shutil.rmtree(info_dir, ignore_errors=True)
        os.makedirs(files_dir, exist_ok=True)
        os.makedirs(info_dir, exist_ok=True)

    print_status_card("✨ TEMPAT SAMPAH KOSONG", [
        ("Status", "Tempat sampah berhasil dikosongkan", Theme.MINT),
    ])

def clean_old_kernels():
    """Membersihkan header dan image kernel Linux lama yang tidak aktif."""
    sudo = get_sudo_prefix()
    run_cmd(f"{sudo}apt-get --purge autoremove -y")

def full_system_clean():
    """Menjalankan seluruh rangkaian pembersihan sistem."""
    clear_screen()
    free_before = get_disk_free_gb()

    print_status_card("🚀 PEMBERSIHAN LENGKAP SISTEM", [
        ("Status", "Memulai semua modul pembersihan...", Theme.YELLOW),
        ("Disk Awal", f"{free_before:.2f} GB Bebas", Theme.CYAN),
    ])

    clean_apt_packages()
    clean_systemd_journal()
    clean_user_caches()
    clean_flatpak_and_snap()
    clean_dev_runtimes_cache()
    clean_trash()
    clean_old_kernels()

    free_after = get_disk_free_gb()
    gained = max(0.0, free_after - free_before)

    clear_screen()
    print_status_card("🎉 PEMBERSIHAN SELESAI", [
        ("Ruang Bebas Awal", f"{free_before:.2f} GB", Theme.WHITE),
        ("Ruang Bebas Akhir", f"{free_after:.2f} GB", Theme.WHITE),
        ("Total Dibebaskan", f"+{gained:.2f} GB", Theme.MINT),
        ("Status", "Sistem Bersih & Teroptimasi", Theme.MINT),
    ])

def main():
    w1 = 37
    w2 = 40

    while True:
        clear_screen()
        print(make_box_top("🧹 SYSTEM CLEANER PRO", badge="v2.5", total_w=80))

        # Disk status bar
        free_gb = get_disk_free_gb()
        disk_raw = f"  Ruang Bebas: {free_gb:.2f} GB (/)"
        pad_d = " " * max(0, 78 - get_display_width(disk_raw))
        print(f"{Theme.BORDER}│{Theme.RESET}{Theme.PEACH}  Ruang Bebas: {Theme.MINT}{free_gb:.2f} GB{Theme.RESET}{Theme.GRAY} (/){Theme.RESET}{pad_d}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}├{'─'*78}┤{Theme.RESET}")

        m1 = format_menu_col("1", "Pembersihan Penuh Sistem", w1, Theme.PEACH, Theme.WHITE)
        m4 = format_menu_col("4", "Cache Browser & Thumbnails", w2, Theme.CYAN, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{m1}{Theme.BORDER}│{Theme.RESET}{m4}{Theme.BORDER}│{Theme.RESET}")

        m2 = format_menu_col("2", "Cache APT & Dependensi", w1, Theme.MINT, Theme.WHITE)
        m5 = format_menu_col("5", "Cache Dev (NPM, Docker)", w2, Theme.BLUE, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{m2}{Theme.BORDER}│{Theme.RESET}{m5}{Theme.BORDER}│{Theme.RESET}")

        m3 = format_menu_col("3", "Systemd Journal Logs", w1, Theme.YELLOW, Theme.WHITE)
        m6 = format_menu_col("6", "Kosongkan Tempat Sampah", w2, Theme.PEACH, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{m3}{Theme.BORDER}│{Theme.RESET}{m6}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}├{'─'*w1}┴{'─'*w2}┤{Theme.RESET}")
        m0 = format_menu_col("0", "Kembali ke Menu Utama", 78, Theme.RED, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{m0}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}╰{'─'*78}╯{Theme.RESET}")

        try:
            choice = input(f"\n {Theme.BOLD}{Theme.PEACH}◆ guava{Theme.RESET} › {Theme.CYAN}sys-cleaner{Theme.RESET} ❯ ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if choice == "0":
            break
        elif choice == "1":
            full_system_clean()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "2":
            clean_apt_packages()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "3":
            clean_systemd_journal()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "4":
            clean_user_caches()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "5":
            clean_dev_runtimes_cache()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "6":
            clean_trash()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n{Theme.PEACH}[*] Pembersihan dibatalkan.{Theme.RESET}")
        sys.exit(0)

