#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
system-cleaner: Linux Mint System & Storage Maintenance TUI
Author: ArioDev7
Theme: Catppuccin Mocha
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Catppuccin Mocha Colors
MAUVE = "\033[38;2;203;166;247m"
PINK = "\033[38;2;245;194;231m"
BLUE = "\033[38;2;137;180;250m"
TEAL = "\033[38;2;148;226;213m"
GREEN = "\033[38;2;166;227;161m"
PEACH = "\033[38;2;250;179;135m"
YELLOW = "\033[38;2;249;226;175m"
RED = "\033[38;2;243;139;168m"
TEXT = "\033[38;2;205;214;244m"
SUBTEXT = "\033[38;2;166;173;200m"
OVERLAY = "\033[38;2;108;112;134m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

BANNER = rf"""{TEAL}{BOLD}
  ____  _   _ ____ _____ _____ __  __    ____ _     _____    _    _   _ _____ ____  
 / ___|| | | / ___|_   _| ____|  \/  |  / ___| |   | ____|  / \  | \ | | ____|  _ \ 
 \___ \| |_| \___ \ | | |  _| | |\/| | | |   | |   |  _|   / _ \ |  \| |  _| | |_) |
  ___) |  _  |___) || | | |___| |  | | | |___| |___| |___ / ___ \| |\  | |___|  _ < 
 |____/|_| |_|____/ |_| |_____|_|  |_|  \____|_____|_____/_/   \_\_| \_|_____|_| \_\
{RESET}{MAUVE}  🧹 Linux Mint & Workspace Storage Optimizer • Catppuccin Mocha{RESET}
"""

def clear():
    os.system("clear")

def cell(text: str, width: int, color: str = "", align: str = "left") -> str:
    text = str(text)
    if len(text) > width:
        text = text[:width - 1] + "…" if width > 2 else text[:width]
    if align == "right":
        padded = text.rjust(width)
    elif align == "center":
        padded = text.center(width)
    else:
        padded = text.ljust(width)
    if color:
        return f"{color}{padded}{RESET}"
    return padded

def format_bytes(b):
    if b < 1024:
        return f"{b} B"
    elif b < 1024 ** 2:
        return f"{b / 1024:.1f} KB"
    elif b < 1024 ** 3:
        return f"{b / (1024 ** 2):.1f} MB"
    else:
        return f"{b / (1024 ** 3):.2f} GB"

def get_dir_size(path):
    p = Path(path)
    if not p.exists():
        return 0
    total = 0
    try:
        if p.is_file():
            return p.stat().st_size
        for root, dirs, files in os.walk(p):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    total += os.path.getsize(fp)
                except (OSError, FileNotFoundError):
                    pass
    except Exception:
        pass
    return total

def get_apt_cache_size():
    return get_dir_size("/var/cache/apt/archives")

def get_journal_size():
    try:
        res = subprocess.run(["journalctl", "--disk-usage"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out = res.stdout.strip()
        # e.g. "Archived and active journals take up 32.0M in the file system."
        return out if out else "0 B"
    except Exception:
        return "N/A"

def scan_targets():
    home = Path.home()
    targets = [
        {"id": "thumb", "name": "Thumbnail Cache", "path": home / ".cache" / "thumbnails", "type": "user"},
        {"id": "trash", "name": "Tempat Sampah (Trash)", "path": home / ".local" / "share" / "Trash", "type": "user"},
        {"id": "pip", "name": "Python Pip Cache", "path": home / ".cache" / "pip", "type": "user"},
        {"id": "npm", "name": "Node / NPM Cache", "path": home / ".npm" / "_cacache", "type": "user"},
        {"id": "cargo", "name": "Rust / Cargo Registry Cache", "path": home / ".cargo" / "registry" / "cache", "type": "user"},
        {"id": "bun", "name": "Bun Package Cache", "path": home / ".bun" / "install" / "cache", "type": "user"},
        {"id": "firefox", "name": "Firefox Browser Cache", "path": home / ".cache" / "mozilla", "type": "user"},
        {"id": "apt", "name": "APT Package Archives", "path": Path("/var/cache/apt/archives"), "type": "root"},
    ]
    for t in targets:
        t["size"] = get_dir_size(t["path"])
    return targets

def quick_clean(targets):
    clear()
    print(BANNER)
    print(f"{BOLD}{BLUE}=== PEMBERSIHAN CEPAT (QUICK CLEAN) ==={RESET}")
    print(f"{SUBTEXT}Membersihkan thumbnail, trash, dan cache pengembangan aman tanpa root...{RESET}\n")

    user_targets = [t for t in targets if t["type"] == "user" and t["size"] > 0]
    if not user_targets:
        print(f"{GREEN}✓ Semua cache pengguna sudah bersih! Tidak ada yang perlu dibersihkan.{RESET}")
        input(f"\n{OVERLAY}[Tekan Enter untuk kembali]{RESET}")
        return

    total_freed = 0
    for t in user_targets:
        p = t["path"]
        print(f"  {YELLOW}Menghapus {t['name']} ({format_bytes(t['size'])})...{RESET}")
        try:
            if p.exists():
                if p.is_file():
                    p.unlink()
                else:
                    for item in p.iterdir():
                        if item.is_dir():
                            shutil.rmtree(item, ignore_errors=True)
                        else:
                            item.unlink(missing_ok=True)
                total_freed += t["size"]
                print(f"  {GREEN}✓ {t['name']} berhasil dibersihkan.{RESET}")
        except Exception as e:
            print(f"  {RED}Gagal: {e}{RESET}")

    print(f"\n{BOLD}{GREEN}🎉 Selesai! Berhasil membebaskan {format_bytes(total_freed)} ruang disk!{RESET}")
    input(f"\n{OVERLAY}[Tekan Enter untuk kembali]{RESET}")

def deep_clean():
    clear()
    print(BANNER)
    print(f"{BOLD}{RED}=== PEMBERSIHAN SISTEM TINGKAT DALAM (ROOT/APT) ==={RESET}")
    print(f"{YELLOW}Aksi ini akan menjalankan apt-get clean, autoremove, dan merapikan log sistem.{RESET}\n")

    confirm = input(f"{PEACH}Lanjutkan dengan hak akses root (sudo)? (y/n): {RESET}").strip().lower()
    if confirm != "y":
        return

    print(f"\n{BLUE}1. Membersihkan cache unduhan APT (apt-get clean)...{RESET}")
    subprocess.run(["sudo", "apt-get", "clean"])

    print(f"\n{BLUE}2. Menghapus paket dependensi yang tak terpakai (autoremove)...{RESET}")
    subprocess.run(["sudo", "apt-get", "autoremove", "-y"])

    print(f"\n{BLUE}3. Mengompresi dan merapikan log sistem journalctl (simpan 3 hari terakhir)...{RESET}")
    subprocess.run(["sudo", "journalctl", "--vacuum-time=3d"])

    print(f"\n{BOLD}{GREEN}✓ Pembersihan sistem mendalam selesai!{RESET}")
    input(f"\n{OVERLAY}[Tekan Enter untuk kembali]{RESET}")

def find_large_files():
    clear()
    print(BANNER)
    print(f"{BOLD}{YELLOW}=== PENCARIAN FILE BESAR (> 100 MB) ==={RESET}")
    print(f"{SUBTEXT}Memindai folder pengguna (~), ini mungkin memerlukan beberapa detik...{RESET}\n")

    home = Path.home()
    large_files = []

    for root, dirs, files in os.walk(home):
        # Skip cache & temp
        dirs[:] = [d for d in dirs if d not in [".cache", ".local", ".git", ".npm", ".cargo", "node_modules"]]
        for f in files:
            fp = Path(root) / f
            try:
                if not fp.is_symlink():
                    sz = fp.stat().st_size
                    if sz > 100 * (1024 ** 2): # > 100MB
                        large_files.append((fp, sz))
            except (OSError, FileNotFoundError):
                pass

    large_files.sort(key=lambda x: x[1], reverse=True)

    if not large_files:
        print(f"{GREEN}✓ Tidak ditemukan file tunggal berukuran > 100 MB.{RESET}")
    else:
        col_w = [4, 14, 52]
        top = OVERLAY + "┌" + "┬".join("─" * (w + 2) for w in col_w) + "┐" + RESET
        mid = OVERLAY + "├" + "┼".join("─" * (w + 2) for w in col_w) + "┤" + RESET
        bot = OVERLAY + "└" + "┴".join("─" * (w + 2) for w in col_w) + "┘" + RESET

        print(top)
        header = OVERLAY + "│ " + (OVERLAY + " │ ").join([
            cell("No", col_w[0], color=PEACH + BOLD),
            cell("Ukuran", col_w[1], color=RED + BOLD),
            cell("Nama & Lokasi File", col_w[2], color=BLUE + BOLD)
        ]) + OVERLAY + " │" + RESET
        print(header)
        print(mid)

        for i, (p, sz) in enumerate(large_files[:20], start=1):
            rel = str(p).replace(str(home), "~")
            row = OVERLAY + "│ " + (OVERLAY + " │ ").join([
                cell(f"[{i}]", col_w[0], color=PINK),
                cell(format_bytes(sz), col_w[1], color=YELLOW),
                cell(rel, col_w[2], color=TEXT)
            ]) + OVERLAY + " │" + RESET
            print(row)

        print(bot)

    input(f"\n{OVERLAY}[Tekan Enter untuk kembali]{RESET}")

def show_disk_usage():
    clear()
    print(BANNER)
    print(f"{BOLD}{BLUE}=== STATUS PARTISI & KESEHATAN PENYIMPANAN ==={RESET}\n")
    subprocess.run(["df", "-h", "-x", "tmpfs", "-x", "devtmpfs", "-x", "squashfs"])
    input(f"\n{OVERLAY}[Tekan Enter untuk kembali]{RESET}")

def main():
    while True:
        clear()
        print(BANNER)
        targets = scan_targets()
        total_user_junk = sum(t["size"] for t in targets if t["type"] == "user")
        total_root_junk = sum(t["size"] for t in targets if t["type"] == "root")

        print(f"  {SUBTEXT}Ringkasan Cache & Berkas Sampah:{RESET}")
        col_w = [4, 30, 14, 15]
        top = OVERLAY + "┌" + "┬".join("─" * (w + 2) for w in col_w) + "┐" + RESET
        mid = OVERLAY + "├" + "┼".join("─" * (w + 2) for w in col_w) + "┤" + RESET
        bot = OVERLAY + "└" + "┴".join("─" * (w + 2) for w in col_w) + "┘" + RESET

        print(top)
        header = OVERLAY + "│ " + (OVERLAY + " │ ").join([
            cell("No", col_w[0], color=PEACH + BOLD),
            cell("Kategori Sampah", col_w[1], color=BLUE + BOLD),
            cell("Ukuran", col_w[2], color=YELLOW + BOLD),
            cell("Akses", col_w[3], color=TEAL + BOLD)
        ]) + OVERLAY + " │" + RESET
        print(header)
        print(mid)

        for i, t in enumerate(targets, start=1):
            sz_str = format_bytes(t["size"])
            c_color = RED if t["size"] > 50 * 1024**2 else (YELLOW if t["size"] > 0 else GREEN)
            a_color = PEACH if t["type"] == "user" else RED
            acc_str = "User (Aman)" if t["type"] == "user" else "Root (Sudo)"
            row = OVERLAY + "│ " + (OVERLAY + " │ ").join([
                cell(f"[{i}]", col_w[0], color=PINK),
                cell(t["name"], col_w[1], color=TEXT),
                cell(sz_str, col_w[2], color=c_color),
                cell(acc_str, col_w[3], color=a_color)
            ]) + OVERLAY + " │" + RESET
            print(row)

        print(bot)
        print(f"  {OVERLAY}Total Cache Pengguna: {BOLD}{PEACH}{format_bytes(total_user_junk)}{RESET}  │  {OVERLAY}Log Journal: {BOLD}{YELLOW}{get_journal_size()}{RESET}\n")

        print(f"  {GREEN}[1]{RESET}  🚀 Bersihkan Cepat (Quick Clean: Trash, Thumbnails, Pip, NPM)")
        print(f"  {RED}[2]{RESET}  🛡️  Bersihkan Sistem Root (APT clean, Autoremove, Journal vacuum)")
        print(f"  {YELLOW}[3]{RESET}  🔍 Pindai File Raksasa (> 100 MB)")
        print(f"  {BLUE}[4]{RESET}  💾 Cek Penggunaan Partisi Disk (df -h)")
        print(f"  {RED}[0]{RESET}  🚪 Keluar")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}")

        pilihan = input(f"{YELLOW}Pilih menu [0-4]: {RESET}").strip()

        if pilihan == "0" or pilihan.lower() == "q":
            print(f"{GREEN}Sampai jumpa! Sistem tetap bersih & kencang 🚀{RESET}")
            break
        elif pilihan == "1":
            quick_clean(targets)
        elif pilihan == "2":
            deep_clean()
        elif pilihan == "3":
            find_large_files()
        elif pilihan == "4":
            show_disk_usage()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{GREEN}Keluar.{RESET}")
