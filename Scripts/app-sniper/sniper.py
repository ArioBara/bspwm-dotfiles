#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app-sniper: Visual Zombie App & Resource Hog Process Killer TUI
Author: ArioDev7
Theme: Catppuccin Mocha
"""

import os
import sys
import time
import signal
import psutil
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
RESET = "\033[0m"

BANNER = rf"""{RED}{BOLD}
     _    ____  ____    ____  _   _ ___ ____  _____ ____  
    / \  |  _ \|  _ \  / ___|| \ | |_ _|  _ \| ____|  _ \ 
   / _ \ | |_) | |_) | \___ \|  \| || || |_) |  _| | |_) |
  / ___ \|  __/|  __/   ___) | |\  || ||  __/| |___|  _ < 
 /_/   \_\_|   |_|     |____/|_| \_|___|_|   |_____|_| \_\
{RESET}{YELLOW}  🎯 Visual Zombie App & Resource Hog Killer • by ArioDev7{RESET}
"""

GUI_APPS_KEYWORDS = {
    "chrome", "firefox", "brave", "edge", "code", "vscodium",
    "nemo", "caja", "thunar", "kitty", "alacritty", "discord",
    "spotify", "mpv", "vlc", "obs", "gimp", "inkscape", "steam",
    "slack", "telegram", "antigravity", "simplescreenrecorder"
}

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

def format_mem(rss_bytes):
    mb = rss_bytes / (1024 * 1024)
    if mb > 1024:
        return f"{mb / 1024:.2f} GB"
    return f"{mb:.1f} MB"

def get_processes(sort_by="mem", filter_gui=False, query=""):
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_info', 'username']):
        try:
            info = p.info
            p_name = info['name'] or "Unknown"
            if filter_gui and not any(kw in p_name.lower() for kw in GUI_APPS_KEYWORDS):
                continue
            if query and query.lower() not in p_name.lower():
                continue

            rss = info['memory_info'].rss if info['memory_info'] else 0
            procs.append({
                "pid": info['pid'],
                "name": p_name,
                "status": info['status'],
                "cpu": info['cpu_percent'] or 0.0,
                "rss": rss,
                "user": info['username'] or "-"
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if sort_by == "mem":
        procs.sort(key=lambda x: x["rss"], reverse=True)
    elif sort_by == "cpu":
        procs.sort(key=lambda x: x["cpu"], reverse=True)
    elif sort_by == "zombie":
        procs = [p for p in procs if p["status"] == psutil.STATUS_ZOMBIE or "zombie" in p["status"].lower()]

    return procs

def draw_table(procs, page=0, page_size=15):
    col_w = [4, 7, 24, 14, 12, 12]
    top = OVERLAY + "┌" + "┬".join("─" * (w + 2) for w in col_w) + "┐" + RESET
    mid = OVERLAY + "├" + "┼".join("─" * (w + 2) for w in col_w) + "┤" + RESET
    bot = OVERLAY + "└" + "┴".join("─" * (w + 2) for w in col_w) + "┘" + RESET

    print(top)
    header = OVERLAY + "│ " + (OVERLAY + " │ ").join([
        cell("No", col_w[0], color=PEACH + BOLD),
        cell("PID", col_w[1], color=BLUE + BOLD),
        cell("Nama Proses", col_w[2], color=TEXT + BOLD),
        cell("Penggunaan RAM", col_w[3], color=YELLOW + BOLD),
        cell("Status", col_w[4], color=TEAL + BOLD),
        cell("Pengguna", col_w[5], color=GREEN + BOLD)
    ]) + OVERLAY + " │" + RESET
    print(header)
    print(mid)

    start = page * page_size
    current_page_procs = procs[start:start + page_size]

    for idx, p in enumerate(current_page_procs, start=1):
        mem_str = format_mem(p["rss"])
        is_high_ram = p["rss"] > 300 * (1024 * 1024)
        mem_color = RED if is_high_ram else (YELLOW if p["rss"] > 100 * (1024 * 1024) else TEXT)

        status_str = p["status"]
        if status_str == "running":
            st_color = GREEN
        elif "zombie" in status_str.lower():
            st_color = RED
        else:
            st_color = SUBTEXT

        row = OVERLAY + "│ " + (OVERLAY + " │ ").join([
            cell(f"[{idx:02d}]", col_w[0], color=PINK),
            cell(str(p["pid"]), col_w[1], color=BLUE),
            cell(p["name"], col_w[2], color=TEXT),
            cell(mem_str, col_w[3], color=mem_color),
            cell(status_str, col_w[4], color=st_color),
            cell(p["user"], col_w[5], color=SUBTEXT)
        ]) + OVERLAY + " │" + RESET
        print(row)

    print(bot)
    return current_page_procs

def kill_process(pid, proc_name, sig):
    sig_name = "SIGKILL (-9 Paksa)" if sig == signal.SIGKILL else "SIGTERM (Ramah)"
    try:
        os.kill(pid, sig)
        print(f"{GREEN}✓ Berhasil mengirim sinyal {sig_name} ke {proc_name} (PID: {pid})!{RESET}")
    except PermissionError:
        print(f"{YELLOW}Izin ditolak. Mencoba menghentikan dengan hak akses sudo...{RESET}")
        subprocess.run(["sudo", "kill", f"-{int(sig)}", str(pid)])
    except ProcessLookupError:
        print(f"{YELLOW}Proses sudah tidak aktif.{RESET}")
    except Exception as e:
        print(f"{RED}Gagal: {e}{RESET}")
    time.sleep(1)

def kill_by_name():
    clear()
    print(BANNER)
    print(f"{BOLD}{RED}=== BASMI SEMUA PROSES BERDASARKAN NAMA ==={RESET}\n")

    name = input(f"{YELLOW}Masukkan nama proses yang ingin dihentikan sekaligus (contoh: chrome, node): {RESET}").strip()
    if not name:
        return

    matches = [p for p in psutil.process_iter(['pid', 'name']) if name.lower() in p.info['name'].lower()]
    if not matches:
        print(f"{YELLOW}Tidak ditemukan proses aktif dengan nama '{name}'.{RESET}")
        time.sleep(1.2)
        return

    print(f"\n{RED}Ditemukan {len(matches)} proses yang cocok:{RESET}")
    for p in matches[:10]:
        print(f"  • PID {p.info['pid']} : {p.info['name']}")

    confirm = input(f"\n{PEACH}Hentikan paksa seluruh {len(matches)} proses di atas? (y/n): {RESET}").strip().lower()
    if confirm == "y":
        for p in matches:
            try:
                os.kill(p.info['pid'], signal.SIGKILL)
            except Exception:
                pass
        print(f"{GREEN}✓ Seluruh proses '{name}' berhasil dibasmi!{RESET}")
        time.sleep(1.2)

def main():
    sort_mode = "mem"
    gui_only = False
    search_query = ""

    while True:
        clear()
        print(BANNER)

        procs = get_processes(sort_by=sort_mode, filter_gui=gui_only, query=search_query)

        filter_label = f"GUI Saja" if gui_only else "Semua Proses"
        query_label = f" | Pencarian: '{search_query}'" if search_query else ""
        sort_label = "RAM Terbesar" if sort_mode == "mem" else ("CPU Terbesar" if sort_mode == "cpu" else "Zombie Hunter")

        print(f"  {SUBTEXT}Filter:{RESET} {BOLD}{BLUE}{filter_label}{query_label}{RESET}  │  {SUBTEXT}Urutan:{RESET} {BOLD}{PEACH}{sort_label}{RESET}  │  {SUBTEXT}Total:{RESET} {BOLD}{TEXT}{len(procs)}{RESET} proses")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}\n")

        visible = draw_table(procs, page=0, page_size=15)

        print(f"\n  {GREEN}[K]{RESET}  🎯 Hentikan Proses Terpilih (Ketik nomor baris)")
        print(f"  {RED}[9]{RESET}  💥 Force Kill -9 Proses Terpilih (Langsung basmi tanpa ampun)")
        print(f"  {BLUE}[M]{RESET}  🔄 Urutkan Berdasarkan RAM  │  {YELLOW}[C]{RESET} Urutkan CPU  │  {RED}[Z]{RESET} Cek Zombie")
        print(f"  {TEAL}[G]{RESET}  🪟 Toggle Hanya Aplikasi GUI (Chrome, Code, Nemo, dll)")
        print(f"  {PEACH}[F]{RESET}  🔍 Cari Berdasarkan Nama     │  {RED}[X]{RESET} Basmi Massal Nama Proses")
        print(f"  {RED}[0]{RESET}  🚪 Keluar")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}")

        pilihan = input(f"{YELLOW}Pilih aksi [nomor / K / 9 / M / C / Z / G / F / X / 0]: {RESET}").strip()

        if pilihan == "0" or pilihan.lower() == "q":
            print(f"{GREEN}Sampai jumpa! Sistem aman & bebas proses beku 🎯{RESET}")
            break
        elif pilihan.lower() == "m":
            sort_mode = "mem"
            search_query = ""
        elif pilihan.lower() == "c":
            sort_mode = "cpu"
            search_query = ""
        elif pilihan.lower() == "z":
            sort_mode = "zombie"
            search_query = ""
        elif pilihan.lower() == "g":
            gui_only = not gui_only
        elif pilihan.lower() == "f":
            search_query = input(f"{PEACH}Filter nama proses: {RESET}").strip()
        elif pilihan.lower() == "x":
            kill_by_name()
        elif pilihan.lower() == "k" or pilihan.lower() == "9":
            sig = signal.SIGKILL if pilihan == "9" else signal.SIGTERM
            target_no = input(f"{PEACH}Pilih nomor baris [1-{len(visible)}] untuk dihentikan: {RESET}").strip()
            if target_no.isdigit() and 1 <= int(target_no) <= len(visible):
                target_proc = visible[int(target_no) - 1]
                kill_process(target_proc["pid"], target_proc["name"], sig)
        elif pilihan.isdigit():
            val = int(pilihan)
            if 1 <= val <= len(visible):
                target_proc = visible[val - 1]
                kill_process(target_proc["pid"], target_proc["name"], signal.SIGTERM)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{GREEN}Keluar.{RESET}")
