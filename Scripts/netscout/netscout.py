#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
netscout: WiFi & Local Network Scanner & Ping Latency Monitor TUI
Author: ArioDev7
Theme: Catppuccin Mocha
"""

import os
import sys
import re
import time
import socket
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
RESET = "\033[0m"

BANNER = rf"""{BLUE}{BOLD}
  _   _ _____ _____ ____   ____ ___  _   _ _____ 
 | \ | | ____|_   _/ ___| / ___/ _ \| | | |_   _|
 |  \| |  _|   | | \___ \| |  | | | | | | | | |  
 | |\  | |___  | |  ___) | |__| |_| | |_| | | |  
 |_| \_|_____| |_| |____/ \____\___/ \___/  |_|  
{RESET}{TEAL}  📡 WiFi & Local Network Scanner & Ping Monitor • by ArioDev7{RESET}
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

def get_default_gateway_and_iface():
    gw = "192.168.1.1"
    iface = "enp0s25"
    try:
        res = subprocess.run(["ip", "route", "show", "default"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        # default via 192.168.1.1 dev enp0s25 proto dhcp src 192.168.1.8 metric 100
        parts = res.stdout.strip().split()
        if "via" in parts and "dev" in parts:
            gw = parts[parts.index("via") + 1]
            iface = parts[parts.index("dev") + 1]
    except Exception:
        pass
    return gw, iface

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def get_device_vendor(mac):
    mac_clean = mac.upper().replace(":", "").replace("-", "")[:6]
    # Simple prefix dictionary for common vendors
    known = {
        "C0FD84": "Huawei / Router",
        "F2F8ED": "Randomized / Android / iOS",
        "2CCC7A": "Xiaomi Communications",
        "EE76B6": "Samsung Electronics",
        "F44D30": "TP-Link Technologies",
        "B4EEB4": "Apple, Inc.",
        "8C8590": "Apple, Inc.",
        "D807B6": "Samsung Electronics",
        "50C7BF": "TP-Link",
        "001A79": "Alcatel",
        "E45F01": "Raspberry Pi",
        "DC4F22": "Espressif IoT (ESP32/8266)"
    }
    return known.get(mac_clean, "Perangkat Jaringan (Network Device)")

def scan_network_devices():
    clear()
    print(BANNER)
    gw, iface = get_default_gateway_and_iface()
    local_ip = get_local_ip()
    subnet = ".".join(local_ip.split(".")[:3]) + ".0/24"

    print(f"{BOLD}{YELLOW}⏳ Sedang memindai perangkat yang terhubung ke jaringan ({subnet})...{RESET}")
    print(f"{SUBTEXT}Menggunakan ARP cache & ping scan cepat...{RESET}\n")

    devices = []
    # 1. Quick arp cache check
    try:
        res = subprocess.run(["ip", "neigh", "show"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        for line in res.stdout.splitlines():
            parts = line.strip().split()
            if len(parts) >= 5 and "lladdr" in parts:
                ip = parts[0]
                mac = parts[parts.index("lladdr") + 1]
                state = parts[-1]
                if state in ["REACHABLE", "STALE", "DELAY"]:
                    vendor = get_device_vendor(mac)
                    is_gw = (ip == gw)
                    is_self = (ip == local_ip)
                    devices.append({"ip": ip, "mac": mac, "vendor": vendor, "is_gw": is_gw, "is_self": is_self})
    except Exception:
        pass

    # 2. Add self if not in list
    if not any(d["is_self"] for d in devices):
        devices.append({"ip": local_ip, "mac": "(Laptop Ini)", "vendor": "Host Laptop (Linux Mint)", "is_gw": False, "is_self": True})

    # Sort by IP address
    def ip_key(d):
        try:
            return [int(x) for x in d["ip"].split(".")]
        except Exception:
            return [999, 999, 999, 999]

    devices.sort(key=ip_key)

    clear()
    print(BANNER)
    print(f"{BOLD}{PEACH}=== PERANGKAT TERHUBUNG DI JARINGAN WIRING/WIFI ==={RESET}")
    print(f"  {SUBTEXT}Interface:{RESET} {BOLD}{TEXT}{iface}{RESET}  │  {SUBTEXT}Router Gateway:{RESET} {BOLD}{GREEN}{gw}{RESET}  │  {SUBTEXT}IP Anda:{RESET} {BOLD}{BLUE}{local_ip}{RESET}\n")

    col_w = [4, 16, 18, 34]
    top = OVERLAY + "┌" + "┬".join("─" * (w + 2) for w in col_w) + "┐" + RESET
    mid = OVERLAY + "├" + "┼".join("─" * (w + 2) for w in col_w) + "┤" + RESET
    bot = OVERLAY + "└" + "┴".join("─" * (w + 2) for w in col_w) + "┘" + RESET

    print(top)
    header = OVERLAY + "│ " + (OVERLAY + " │ ").join([
        cell("No", col_w[0], color=PEACH + BOLD),
        cell("Alamat IP", col_w[1], color=BLUE + BOLD),
        cell("MAC Address", col_w[2], color=TEAL + BOLD),
        cell("Tipe / Perkiraan Vendor", col_w[3], color=YELLOW + BOLD)
    ]) + OVERLAY + " │" + RESET
    print(header)
    print(mid)

    for idx, d in enumerate(devices, start=1):
        v_name = d["vendor"]
        if d["is_gw"]:
            v_name += " (Router)"
        elif d["is_self"]:
            v_name += " (Laptop Ini)"
        
        v_color = GREEN if d["is_gw"] else (BLUE if d["is_self"] else TEXT)

        row = OVERLAY + "│ " + (OVERLAY + " │ ").join([
            cell(f"[{idx:02d}]", col_w[0], color=PINK),
            cell(d['ip'], col_w[1], color=BOLD + TEXT),
            cell(d['mac'], col_w[2], color=SUBTEXT),
            cell(v_name, col_w[3], color=v_color)
        ]) + OVERLAY + " │" + RESET
        print(row)

    print(bot)
    print(f"\n{OVERLAY}Total {len(devices)} perangkat aktif terdeteksi.{RESET}")
    input(f"\n{OVERLAY}[Tekan Enter untuk kembali ke menu]{RESET}")

def live_ping_monitor():
    gw, _ = get_default_gateway_and_iface()
    target = gw

    clear()
    print(BANNER)
    print(f"{BOLD}{TEAL}=== LIVE PING & LATENCY GRAPH VISUALIZER ==={RESET}")
    print(f"{SUBTEXT}Target:{RESET} {BOLD}{YELLOW}{target}{RESET} (Router Gateway) dan {BOLD}{BLUE}8.8.8.8{RESET} (Internet)")
    print(f"{OVERLAY}Tekan [Ctrl+C] kapan saja untuk kembali ke menu utama.{RESET}\n")

    history = []
    bars = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

    try:
        while True:
            t0 = time.time()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            ping_ms = None
            try:
                s.connect((target, 53 if target != gw else 80))
                ping_ms = (time.time() - t0) * 1000
            except Exception:
                try:
                    p = subprocess.run(["ping", "-c", "1", "-W", "1", target], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
                    m = re.search(r"time=([\d\.]+)\s*ms", p.stdout)
                    if m:
                        ping_ms = float(m.group(1))
                except Exception:
                    pass
            finally:
                s.close()

            if ping_ms is not None:
                history.append(ping_ms)
                status_color = GREEN if ping_ms < 20 else (YELLOW if ping_ms < 60 else RED)
                ms_text = f"{status_color}{ping_ms:5.1f} ms{RESET}"
            else:
                history.append(999)
                ms_text = f"{RED}TIMEOUT  {RESET}"

            if len(history) > 40:
                history.pop(0)

            # Build sparkline graph
            graph = ""
            for val in history:
                if val >= 200:
                    graph += f"{RED}█{RESET}"
                elif val >= 100:
                    graph += f"{RED}▇{RESET}"
                elif val >= 60:
                    graph += f"{YELLOW}▅{RESET}"
                elif val >= 30:
                    graph += f"{YELLOW}▄{RESET}"
                elif val >= 15:
                    graph += f"{GREEN}▃{RESET}"
                else:
                    graph += f"{GREEN}▂{RESET}"

            valid = [x for x in history if x < 500]
            avg_ms = sum(valid) / len(valid) if valid else 0
            min_ms = min(valid) if valid else 0
            max_ms = max(valid) if valid else 0

            sys.stdout.write(f"\r  Target: {target:<15} │ Latency: {ms_text} │ Trend: [{graph:<40}] │ Min/Avg/Max: {min_ms:.0f}/{avg_ms:.0f}/{max_ms:.0f} ms ")
            sys.stdout.flush()
            time.sleep(0.6)

    except KeyboardInterrupt:
        print(f"\n\n{GREEN}Monitoring selesai.{RESET}")
        time.sleep(1)

def scan_ports():
    clear()
    print(BANNER)
    print(f"{BOLD}{PEACH}=== PORT SCANNER RINGAN ==={RESET}\n")

    target = input(f"{YELLOW}Masukkan IP / Host target (default: localhost 127.0.0.1): {RESET}").strip() or "127.0.0.1"

    common_ports = [
        (21, "FTP"), (22, "SSH"), (53, "DNS"), (80, "HTTP"),
        (443, "HTTPS"), (3000, "Node / React Web"), (3306, "MySQL / MariaDB"),
        (5432, "PostgreSQL"), (6379, "Redis"), (8080, "HTTP Alt / Proxy"),
        (9000, "Portainer"), (27017, "MongoDB")
    ]

    print(f"\n{SUBTEXT}Memeriksa status port pada {BOLD}{target}{RESET}{SUBTEXT}...{RESET}\n")

    for port, name in common_ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        result = s.connect_ex((target, port))
        s.close()
        if result == 0:
            print(f"  {GREEN}● Port {port:<5} [TERBUKA / OPEN]   - {name}{RESET}")
        else:
            print(f"  {OVERLAY}○ Port {port:<5} (Tertutup)        - {name}{RESET}")

    input(f"\n{OVERLAY}[Tekan Enter untuk kembali]{RESET}")

def main():
    while True:
        clear()
        print(BANNER)
        gw, iface = get_default_gateway_and_iface()
        local_ip = get_local_ip()

        print(f"  {OVERLAY}IP Komputer:{RESET} {BOLD}{BLUE}{local_ip}{RESET}  │  {OVERLAY}Gateway:{RESET} {BOLD}{GREEN}{gw}{RESET}  │  {OVERLAY}Interface:{RESET} {BOLD}{TEXT}{iface}{RESET}")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}\n")

        print(f"  {PEACH}[1]{RESET}  🔍 Siapa Saja di Jaringan Saya? (Scan IP, MAC & Perangkat Terhubung)")
        print(f"  {BLUE}[2]{RESET}  📈 Live Ping & Latency Visualizer (Grafik ASCII Kestabilan Koneksi)")
        print(f"  {TEAL}[3]{RESET}  🛡️  Port Scanner Ringan (Cek Port Web, SSH, Database)")
        print(f"  {RED}[0]{RESET}  🚪 Keluar")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}")

        pilihan = input(f"{YELLOW}Pilih menu [0-3]: {RESET}").strip()

        if pilihan == "0" or pilihan.lower() == "q":
            print(f"{GREEN}Sampai jumpa! 📡{RESET}")
            break
        elif pilihan == "1":
            scan_network_devices()
        elif pilihan == "2":
            live_ping_monitor()
        elif pilihan == "3":
            scan_ports()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{GREEN}Keluar.{RESET}")
