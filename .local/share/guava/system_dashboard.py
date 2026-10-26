#!/usr/bin/env python3
"""
Real-Time System & Hardware Monitor Dashboard untuk Linux.
Menampilkan CPU load, RAM/Swap usage, visualisasi disk storage, GPU, suhu sensor,
antarmuka jaringan, dan 5 proses teratas dengan mode refresh langsung (Live View).
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
    print("\033[H\033[J", end="", flush=True)

def get_display_width(text):
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
    left = f"╭─ {title} "
    right = f" {badge} ─╮" if badge else " ─╮"
    used = get_display_width(left) + get_display_width(right)
    dashes = "─" * max(0, total_w - used)
    return f"{Theme.BORDER}{left}{dashes}{right}{Theme.RESET}"

def make_bar(percent, length=18):
    """Menghasilkan bar persentase visual ricing yang halus (▰▱)."""
    percent = max(0.0, min(100.0, percent))
    filled = int(length * (percent / 100))
    empty = length - filled
    
    if percent > 85:
        bar_color = Theme.RED
    elif percent > 60:
        bar_color = Theme.YELLOW
    else:
        bar_color = Theme.MINT

    bar = f"{bar_color}{'▰' * filled}{Theme.GRAY}{'▱' * empty}{Theme.RESET}"
    return f"{bar} {Theme.WHITE}{percent:>5.1f}%{Theme.RESET}"

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode('utf-8').strip()
    except Exception:
        return "N/A"

def get_cpu_info():
    model = "N/A"
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if "model name" in line:
                    model = line.split(":")[1].strip()
                    break
    except Exception:
        pass

    def read_stat():
        with open("/proc/stat", "r") as f:
            fields = [float(column) for column in f.readline().strip().split()[1:5]]
        idle, total = fields[3], sum(fields)
        return idle, total

    try:
        idle1, total1 = read_stat()
        time.sleep(0.12)
        idle2, total2 = read_stat()
        idle_delta = idle2 - idle1
        total_delta = total2 - total1
        cpu_usage = 100.0 * (1.0 - idle_delta / total_delta) if total_delta > 0 else 0.0
    except Exception:
        cpu_usage = 0.0

    return model, cpu_usage

def get_memory_info():
    mem_total, mem_avail, mem_cached = 0, 0, 0
    swap_total, swap_free = 0, 0
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                parts = line.split(":")
                key = parts[0].strip()
                val = int(parts[1].split()[0])
                if key == "MemTotal": mem_total = val
                elif key == "MemAvailable": mem_avail = val
                elif key == "Cached": mem_cached = val
                elif key == "SwapTotal": swap_total = val
                elif key == "SwapFree": swap_free = val
    except Exception:
        pass

    mem_used = max(0, mem_total - mem_avail)
    mem_pct = (mem_used / mem_total * 100) if mem_total > 0 else 0
    swap_used = max(0, swap_total - swap_free)
    swap_pct = (swap_used / swap_total * 100) if swap_total > 0 else 0

    return {
        "mem_total_gb": mem_total / (1024**2),
        "mem_used_gb": mem_used / (1024**2),
        "mem_pct": mem_pct,
        "swap_total_gb": swap_total / (1024**2),
        "swap_used_gb": swap_used / (1024**2),
        "swap_pct": swap_pct
    }

def get_disk_mounts():
    mounts = []
    try:
        df_out = run_cmd("df -h -P -x tmpfs -x devtmpfs -x squashfs 2>/dev/null")
        lines = df_out.splitlines()
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 6:
                fs, size, used, avail, pct_str, mp = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
                try:
                    pct = float(pct_str.replace("%", ""))
                except Exception:
                    pct = 0.0
                mounts.append({"fs": fs, "size": size, "used": used, "avail": avail, "pct": pct, "mp": mp})
    except Exception:
        pass
    return mounts

def get_top_processes():
    try:
        out = run_cmd("ps -eo pid,user,%cpu,%mem,comm --sort=-%cpu | head -n 5")
        return out.splitlines()
    except Exception:
        return []

def print_row(content):
    dw = get_display_width(content)
    pad = " " * max(0, 78 - dw)
    print(f"{Theme.BORDER}│{Theme.RESET}{content}{pad}{Theme.BORDER}│{Theme.RESET}")

def render_dashboard():
    hostname = run_cmd("hostname")
    distro = run_cmd("lsb_release -ds 2>/dev/null || cat /etc/issue | head -n 1")
    kernel = run_cmd("uname -r")
    uptime = run_cmd("uptime -p")
    desktop_env = os.getenv("XDG_CURRENT_DESKTOP", run_cmd("echo $DESKTOP_SESSION"))
    shell_env = os.path.basename(os.getenv("SHELL", "sh"))

    cpu_name, cpu_pct = get_cpu_info()
    mem = get_memory_info()

    clear_screen()
    print(make_box_top("🍃 SYSTEM MONITOR DASHBOARD", badge="v2.5", total_w=80))

    # Host summary
    r1 = f"  {Theme.GRAY}Distro  : {Theme.RESET}{Theme.WHITE}{distro[:24]:<24}{Theme.RESET}  {Theme.GRAY}Desktop : {Theme.RESET}{Theme.CYAN}{desktop_env[:18]}{Theme.RESET}"
    r2 = f"  {Theme.GRAY}Kernel  : {Theme.RESET}{Theme.PEACH}{kernel[:24]:<24}{Theme.RESET}  {Theme.GRAY}Host    : {Theme.RESET}{Theme.WHITE}{hostname[:18]}{Theme.RESET}"
    r3 = f"  {Theme.GRAY}Uptime  : {Theme.RESET}{Theme.MINT}{uptime[:24]:<24}{Theme.RESET}  {Theme.GRAY}Shell   : {Theme.RESET}{Theme.CYAN}{shell_env[:18]}{Theme.RESET}"
    print_row(r1)
    print_row(r2)
    print_row(r3)

    print(f"{Theme.BORDER}├{'─'*78}┤{Theme.RESET}")

    # CPU & RAM
    cpu_short = cpu_name.split("@")[0].strip() if "@" in cpu_name else cpu_name[:40]
    print_row(f"  {Theme.PEACH}CPU Model : {Theme.RESET}{Theme.WHITE}{cpu_short}{Theme.RESET}")
    print_row(f"  {Theme.GRAY}CPU Load  : {Theme.RESET}{make_bar(cpu_pct, 20)}")
    
    ram_str = f"{mem['mem_used_gb']:.2f}/{mem['mem_total_gb']:.2f} GB"
    print_row(f"  {Theme.GRAY}RAM Usage : {Theme.RESET}{make_bar(mem['mem_pct'], 20)} {Theme.GRAY}({ram_str}){Theme.RESET}")
    
    if mem['swap_total_gb'] > 0:
        swap_str = f"{mem['swap_used_gb']:.2f}/{mem['swap_total_gb']:.2f} GB"
        print_row(f"  {Theme.GRAY}Swap Usage: {Theme.RESET}{make_bar(mem['swap_pct'], 20)} {Theme.GRAY}({swap_str}){Theme.RESET}")

    print(f"{Theme.BORDER}├{'─'*78}┤{Theme.RESET}")

    # Storage mounts
    print_row(f"  {Theme.CYAN}PARTISI PENYIMPANAN & DISK:{Theme.RESET}")
    mounts = get_disk_mounts()
    for m in mounts[:3]:
        mp_short = m['mp'][:16]
        sz_str = f"{m['used']}/{m['size']}"
        print_row(f"   {Theme.WHITE}{mp_short:<16}{Theme.RESET} {make_bar(m['pct'], 16)} {Theme.GRAY}{sz_str:<12}{Theme.RESET}")

    print(f"{Theme.BORDER}├{'─'*78}┤{Theme.RESET}")

    # Top processes
    print_row(f"  {Theme.PEACH}PROSES TERATAS (CPU CONSUMPTION):{Theme.RESET}")
    procs = get_top_processes()
    if procs:
        hdr = procs[0]
        print_row(f"   {Theme.GRAY}{hdr[:72]}{Theme.RESET}")
        for p in procs[1:4]:
            print_row(f"   {Theme.WHITE}{p[:72]}{Theme.RESET}")

    print(f"{Theme.BORDER}╰{'─'*78}╯{Theme.RESET}")
    print(f" {Theme.DIM}Mode Live Refresh: 2s | Tekan CTRL+C untuk kembali ke menu{Theme.RESET}", end="", flush=True)

def main():
    while True:
        try:
            render_dashboard()
            time.sleep(2)
        except KeyboardInterrupt:
            print(f"\n\n {Theme.PEACH}[*] Keluar dari System Dashboard.{Theme.RESET}")
            sys.exit(0)

if __name__ == "__main__":
    main()

