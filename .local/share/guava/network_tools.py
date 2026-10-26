#!/usr/bin/env python3
"""
Linux Network & Wi-Fi Toolkit Pro.
Menyediakan inspeksi koneksi lokal & publik, status sinyal Wi-Fi, pemindaian subnet LAN (IP/MAC Scanner),
port scanner, pemantau port listening (ss/netstat), uji latensi ping, dan speedtest.
"""

import os
import shutil
import socket
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor

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

def run_cmd(cmd, capture=True):
    try:
        if capture:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return res.stdout.strip()
        else:
            return subprocess.run(cmd, shell=True)
    except Exception:
        return "" if capture else None

def get_network_info():
    """Menampilkan detail lengkap koneksi jaringan aktif dalam format card modern."""
    clear_screen()
    print_status_card("📡 INFORMASI JARINGAN", [
        ("Status", "Mengambil informasi IP & koneksi...", Theme.YELLOW),
    ])

    local_ip = run_cmd("ip route get 1.1.1.1 2>/dev/null | awk '{print $7}'")
    interface = run_cmd("ip route get 1.1.1.1 2>/dev/null | awk '{print $5}'")
    gateway = run_cmd("ip route show | grep default | awk '{print $3}'")
    dns_servers = run_cmd("grep 'nameserver' /etc/resolv.conf | awk '{print $2}'")

    public_ip = run_cmd("curl -s --max-time 3 https://api.ipify.org")
    isp_info = run_cmd("curl -s --max-time 3 https://ipapi.co/org 2>/dev/null")
    country = run_cmd("curl -s --max-time 3 https://ipapi.co/country_name 2>/dev/null")

    items = [
        ("Interface", interface or "N/A", Theme.CYAN),
        ("IP Lokal", local_ip or "Tidak terhubung", Theme.MINT),
        ("Gateway", gateway or "N/A", Theme.WHITE),
        ("DNS Server", dns_servers.replace("\n", ", ") if dns_servers else "N/A", Theme.WHITE),
        ("IP Publik", public_ip or "N/A", Theme.PEACH),
        ("ISP / Lokasi", f"{isp_info or 'N/A'} ({country or 'N/A'})", Theme.WHITE),
    ]

    if shutil.which("nmcli"):
        wifi_info = run_cmd("nmcli -t -f active,ssid,bssid,signal,freq dev wifi | grep '^yes'")
        if wifi_info:
            parts = wifi_info.split(":")
            if len(parts) >= 4:
                items.append(("Wi-Fi SSID", parts[1], Theme.MINT))
                items.append(("Sinyal Wi-Fi", f"{parts[3]}% (BSSID: {parts[2]})", Theme.CYAN))

    clear_screen()
    print_status_card("📡 STATUS KONEKSI JARINGAN", items)

def scan_lan_devices():
    """Pemindaian seluruh perangkat aktif dalam satu jaringan lokal (LAN/Wi-Fi)."""
    clear_screen()
    gateway = run_cmd("ip route show | grep default | awk '{print $3}'")
    if not gateway:
        print_status_card("❌ KONEKSI JARINGAN", [
            ("Status", "Tidak ada koneksi jaringan atau gateway aktif", Theme.RED),
        ])
        return

    subnet = ".".join(gateway.split(".")[:3]) + ".0/24"
    print_status_card("🔍 PEMINDAIAN SUBNET LAN", [
        ("Subnet", subnet, Theme.CYAN),
        ("Gateway", gateway, Theme.MINT),
        ("Metode", "Multi-Threaded ARP/Ping Scanner", Theme.PEACH),
    ])

    if shutil.which("arp-scan"):
        os.system("sudo arp-scan --localnet")
    elif shutil.which("nmap"):
        os.system(f"nmap -sn {subnet}")
    else:
        base = ".".join(gateway.split(".")[:3])
        active_hosts = []

        def ping_ip(ip):
            res = subprocess.run(f"ping -c 1 -W 1 {ip} > /dev/null 2>&1", shell=True)
            if res.returncode == 0:
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except Exception:
                    hostname = "Unknown Host"
                active_hosts.append((ip, hostname))

        with ThreadPoolExecutor(max_workers=50) as executor:
            for i in range(1, 255):
                executor.submit(ping_ip, f"{base}.{i}")

        print(f"\n {Theme.BOLD}{Theme.CYAN}Perangkat Ditemukan ({len(active_hosts)}):{Theme.RESET}")
        for ip, host in sorted(active_hosts, key=lambda x: int(x[0].split(".")[-1])):
            print(f"  {Theme.MINT}● {ip:<16}{Theme.RESET} → {Theme.WHITE}{host}{Theme.RESET}")

def scan_ports():
    """Port scanner cepat ke alamat IP atau domain target."""
    clear_screen()
    print_status_card("⚡ PORT SCANNER CEPAT", [
        ("Info", "Memindai port terbuka pada target host", Theme.CYAN),
    ])
    try:
        target = input(f" {Theme.BOLD}Target IP / Domain [e.g. 127.0.0.1]: {Theme.RESET}").strip()
    except (KeyboardInterrupt, EOFError):
        return
    if not target:
        return

    clear_screen()
    print_status_card("⚡ SCAN PORT BERJALAN", [
        ("Target Host", target, Theme.CYAN),
        ("Status", "Sedang memindai port umum...", Theme.YELLOW),
    ])

    if shutil.which("nmap"):
        os.system(f"nmap -F {target}")
    else:
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 6379, 8000, 8080, 9000]
        open_ports = []

        def check_port(p):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.6)
            if s.connect_ex((target, p)) == 0:
                open_ports.append(p)
            s.close()

        with ThreadPoolExecutor(max_workers=20) as executor:
            for p in common_ports:
                executor.submit(check_port, p)

        if open_ports:
            print(f"\n {Theme.BOLD}{Theme.MINT}Port Terbuka Ditemukan:{Theme.RESET}")
            for p in sorted(open_ports):
                print(f"  {Theme.MINT}● Port {p:<6}{Theme.RESET} [OPEN]")
        else:
            print(f"\n {Theme.GRAY}○ Tidak ada port umum yang terbuka terdeteksi.{Theme.RESET}")

def view_listening_ports():
    """Menampilkan port yang sedang didengarkan (listening) oleh layanan di Linux."""
    clear_screen()
    print_status_card("🎧 PORT LISTENING AKTIF", [
        ("Tool", "ss / netstat daemon inspector", Theme.CYAN),
    ])
    if shutil.which("ss"):
        os.system("ss -tulpn | grep LISTEN")
    elif shutil.which("netstat"):
        os.system("netstat -tulnp | grep LISTEN")
    else:
        print(" [!] Tool 'ss' atau 'netstat' tidak ditemukan.")

def test_speed():
    """Uji kecepatan internet (Speedtest)."""
    clear_screen()
    print_status_card("🚀 SPEEDTEST INTERNET", [
        ("Tool", "speedtest-cli", Theme.CYAN),
        ("Status", "Mengukur latensi, download & upload...", Theme.YELLOW),
    ])
    if shutil.which("speedtest-cli"):
        os.system("speedtest-cli --simple")
    elif shutil.which("speedtest"):
        os.system("speedtest")
    else:
        sudo = "" if (hasattr(os, "geteuid") and os.geteuid() == 0) else "sudo "
        run_cmd(f"{sudo}apt install -y speedtest-cli")
        os.system("speedtest-cli --simple")

def show_menu():
    w1 = 37
    w2 = 40

    while True:
        clear_screen()
        print(make_box_top("📡 NETWORK TOOLKIT PRO", badge="v2.5", total_w=80))

        m1 = format_menu_col("1", "Info Jaringan & IP", w1, Theme.CYAN, Theme.WHITE)
        m4 = format_menu_col("4", "Port Listening (ss)", w2, Theme.PEACH, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{m1}{Theme.BORDER}│{Theme.RESET}{m4}{Theme.BORDER}│{Theme.RESET}")

        m2 = format_menu_col("2", "Scan Perangkat LAN", w1, Theme.MINT, Theme.WHITE)
        m5 = format_menu_col("5", "Speedtest Internet", w2, Theme.YELLOW, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{m2}{Theme.BORDER}│{Theme.RESET}{m5}{Theme.BORDER}│{Theme.RESET}")

        m3 = format_menu_col("3", "Port Scanner Cepat", w1, Theme.BLUE, Theme.WHITE)
        m6 = format_menu_col("6", "Uji Latensi Ping", w2, Theme.CYAN, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{m3}{Theme.BORDER}│{Theme.RESET}{m6}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}├{'─'*w1}┴{'─'*w2}┤{Theme.RESET}")
        m0 = format_menu_col("0", "Kembali ke Menu Utama", 78, Theme.RED, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{m0}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}╰{'─'*78}╯{Theme.RESET}")

        try:
            choice = input(f"\n {Theme.BOLD}{Theme.PEACH}◆ guava{Theme.RESET} › {Theme.CYAN}network-tools{Theme.RESET} ❯ ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if choice == "0":
            break
        elif choice == "1":
            get_network_info()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "2":
            scan_lan_devices()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "3":
            scan_ports()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "4":
            view_listening_ports()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "5":
            test_speed()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "6":
            clear_screen()
            print_status_card("📶 UJI LATENSI PING", [
                ("Target", "1.1.1.1 (Cloudflare DNS)", Theme.CYAN),
            ])
            os.system("ping -c 5 1.1.1.1")
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")

def main():
    show_menu()

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n{Theme.PEACH}[*] Program dihentikan.{Theme.RESET}")
        sys.exit(0)

