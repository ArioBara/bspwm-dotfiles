#!/usr/bin/env python3
"""
Cybersecurity & Penetration Testing Toolkit untuk Linux / Debian.
Mendukung instalasi tool keamanan native (Nmap, Metasploit, Burp Suite, Wireshark, Aircrack-ng),
penyebaran Kali Linux via Docker Container Resmi, dan Kali NetHunter Proot environment.
"""

import os
import subprocess
import shutil
import sys
import time

import os
import subprocess
import shutil
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
        prefix = f"  {label:<10}: "
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
        print(f"{Theme.BORDER}│{Theme.RESET}{Theme.GRAY}  {label:<10}: {Theme.RESET}{val_color}{val_str}{Theme.RESET}{pad}{Theme.BORDER}│{Theme.RESET}")
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

def get_sudo_prefix():
    return "" if (hasattr(os, "geteuid") and os.geteuid() == 0) else "sudo "

def run_cmd(command):
    try:
        return subprocess.run(command, shell=True)
    except Exception as e:
        print(f"{Theme.RED}[!] Error: {e}{Theme.RESET}")
        return None

def get_tool_categories():
    """Daftar paket pengujian keamanan native untuk Linux."""
    return {
        "1": {
            "name": "Info Recon & OSINT",
            "desc": "Pemindaian jaringan, port scanning, OSINT, DNS & subnet mapping",
            "check": "nmap",
            "packages": "nmap masscan whois dnsutils nikto enum4linux arp-scan netdiscover traceroute tshark wireshark"
        },
        "2": {
            "name": "Web Security & Audit",
            "desc": "SQL Injection, fuzzing, directory brute-force, CMS auditor",
            "check": "sqlmap",
            "packages": "sqlmap gobuster ffuf dirb wpscan zaproxy commix nikto"
        },
        "3": {
            "name": "Password & Hash Crack",
            "desc": "Wordlists, online authentication brute-force, dan offline hash cracking",
            "check": "john",
            "packages": "john hydra hashcat medusa wordlists crunch fcrackzip pdfcrack"
        },
        "4": {
            "name": "Wireless & Wi-Fi Audit",
            "desc": "Analisis protokol nirkabel 802.11, monitor mode, WPA/WPA2 handshake",
            "check": "aircrack-ng",
            "packages": "aircrack-ng reaver pixiewps kismet iw wireless-tools hcxtools hcxdumptool"
        },
        "5": {
            "name": "Reverse & Exploitation",
            "desc": "Metasploit Framework, debugger, decompiler & static analysis",
            "check": "gdb",
            "packages": "gdb radare2 binwalk sleuthkit foremost yara nasm"
        }
    }

def install_native_packages(title, pkg_str):
    """Memasang paket keamanan melalui apt pada sistem Linux."""
    clear_screen()
    print_status_card("📦 INSTALASI TOOLKIT", [
        ("Kategori", title, Theme.CYAN),
        ("Metode", "APT Package Manager", Theme.PEACH),
    ])
    sudo = get_sudo_prefix()
    cmd = f"{sudo}apt update -y && {sudo}apt install -y {pkg_str}"
    res = run_cmd(cmd)
    if res and res.returncode == 0:
        print_status_card("✨ STATUS INSTALASI", [
            ("Status", "BERHASIL DIINSTAL", Theme.MINT),
            ("Toolkit", title, Theme.WHITE),
        ])
    else:
        print_status_card("❌ STATUS INSTALASI", [
            ("Status", "GAGAL DIEKSEKUSI", Theme.RED),
            ("Toolkit", title, Theme.WHITE),
        ])

def install_metasploit_official():
    """Menginstal Metasploit Framework resmi melalui skrip installer Rapid7."""
    clear_screen()
    print_status_card("📦 INSTALASI METASPLOIT", [
        ("Framework", "Metasploit Framework (Rapid7 Official)", Theme.CYAN),
        ("Status", "Mengunduh dan mengeksekusi installer...", Theme.YELLOW),
    ])
    sudo = get_sudo_prefix()
    cmd = f"curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && chmod 755 msfinstall && {sudo}./msfinstall && rm -f msfinstall"
    run_cmd(cmd)
    print_status_card("✨ STATUS METASPLOIT", [
        ("Status", "Selesai", Theme.MINT),
        ("Akses CLI", "msfconsole", Theme.PEACH),
    ])

def setup_kali_docker():
    """Menyiapkan dan menjalankan Kali Linux Rolling melalui Docker Container resmi."""
    clear_screen()
    if not shutil.which("docker"):
        print_status_card("❌ DOCKER TIDAK DITEMUKAN", [
            ("Keterangan", "Docker belum terpasang di sistem", Theme.RED),
            ("Solusi", "Pasang via tech_stack.py [Cloud & Virtualization]", Theme.PEACH),
        ])
        return

    print_status_card("🐳 KALI LINUX DOCKER", [
        ("Image", "kalilinux/kali-rolling (Official)", Theme.CYAN),
        ("Status", "Pulling docker container image...", Theme.YELLOW),
    ])
    run_cmd("docker pull kalilinux/kali-rolling")

    print_status_card("✨ KALI LINUX SIAP", [
        ("Status", "Image Berhasil Diunduh", Theme.MINT),
        ("Perintah", "docker run -it --rm --net=host kalilinux/kali-rolling", Theme.PEACH),
    ])

    try:
        start_now = input(f" {Theme.BOLD}Masuk ke shell Kali Linux sekarang? (y/n): {Theme.RESET}").strip().lower()
        if start_now == "y":
            clear_screen()
            os.system("docker run -it --rm --net=host -v $HOME/kali_workspace:/root kalilinux/kali-rolling /bin/bash")
    except (KeyboardInterrupt, EOFError):
        pass

def install_burpsuite_community():
    """Mengunduh dan memasang PortSwigger Burp Suite Community Edition."""
    clear_screen()
    print_status_card("📦 INSTALASI BURP SUITE", [
        ("Software", "Burp Suite Community Edition + Java JRE", Theme.CYAN),
        ("Status", "Memasang dependensi Java JRE...", Theme.YELLOW),
    ])
    sudo = get_sudo_prefix()
    run_cmd(f"{sudo}apt update && {sudo}apt install -y openjdk-21-jre openjdk-17-jre")

    burp_installed = shutil.which("burpsuite")
    if burp_installed:
        print_status_card("✨ STATUS BURP SUITE", [
            ("Status", "Sudah Terpasang", Theme.MINT),
            ("Lokasi", burp_installed, Theme.WHITE),
        ])
    else:
        res = run_cmd(f"{sudo}apt install -y burpsuite")
        if not res or res.returncode != 0:
            print_status_card("🌐 DOWNLOAD BURP SUITE", [
                ("Sumber", "PortSwigger Official CDN", Theme.CYAN),
                ("Status", "Mengunduh standalone installer...", Theme.YELLOW),
            ])
            run_cmd("curl -fsSL 'https://portswigger.net/burp/releases/download?product=community&version=latest&type=Linux' -o burpsuite_installer.sh && chmod +x burpsuite_installer.sh && ./burpsuite_installer.sh && rm -f burpsuite_installer.sh")

        print_status_card("✨ STATUS BURP SUITE", [
            ("Status", "Selesai Dipasang", Theme.MINT),
        ])

def show_menu():
    categories = get_tool_categories()
    w1 = 37
    w2 = 40

    while True:
        clear_screen()
        print(make_box_top("🛡️ CYBERSECURITY & PENTEST TOOLKIT", badge="v2.5", total_w=80))

        # Status terpasang
        st_c1 = shutil.which(categories["1"]["check"]) is not None
        st_c2 = shutil.which(categories["2"]["check"]) is not None
        st_c3 = shutil.which(categories["3"]["check"]) is not None
        st_c4 = shutil.which(categories["4"]["check"]) is not None
        st_c5 = shutil.which(categories["5"]["check"]) is not None
        st_c6 = shutil.which("msfconsole") is not None
        st_c7 = shutil.which("burpsuite") is not None
        st_c8 = shutil.which("docker") is not None

        # Row 1
        r1_l = format_app_col("1", categories["1"]["name"], st_c1, w1)
        r1_r = format_app_col("5", categories["5"]["name"], st_c5, w2)
        print(f"{Theme.BORDER}│{Theme.RESET}{r1_l}{Theme.BORDER}│{Theme.RESET}{r1_r}{Theme.BORDER}│{Theme.RESET}")

        # Row 2
        r2_l = format_app_col("2", categories["2"]["name"], st_c2, w1)
        r2_r = format_app_col("6", "Metasploit Framework", st_c6, w2)
        print(f"{Theme.BORDER}│{Theme.RESET}{r2_l}{Theme.BORDER}│{Theme.RESET}{r2_r}{Theme.BORDER}│{Theme.RESET}")

        # Row 3
        r3_l = format_app_col("3", categories["3"]["name"], st_c3, w1)
        r3_r = format_app_col("7", "Burp Suite Community", st_c7, w2)
        print(f"{Theme.BORDER}│{Theme.RESET}{r3_l}{Theme.BORDER}│{Theme.RESET}{r3_r}{Theme.BORDER}│{Theme.RESET}")

        # Row 4
        r4_l = format_app_col("4", categories["4"]["name"], st_c4, w1)
        r4_r = format_app_col("8", "Kali Linux Docker", st_c8, w2)
        print(f"{Theme.BORDER}│{Theme.RESET}{r4_l}{Theme.BORDER}│{Theme.RESET}{r4_r}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}├{'─'*w1}┼{'─'*w2}┤{Theme.RESET}")

        ctrl_a = format_menu_col("A", "Install Semua Native Suite", w1, Theme.PEACH, Theme.WHITE)
        ctrl_0 = format_menu_col("0", "Kembali ke Menu Utama", w2, Theme.RED, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{ctrl_a}{Theme.BORDER}│{Theme.RESET}{ctrl_0}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}╰{'─'*w1}┴{'─'*w2}╯{Theme.RESET}")

        try:
            choice = input(f"\n {Theme.BOLD}{Theme.PEACH}◆ guava{Theme.RESET} › {Theme.CYAN}pentest-toolkit{Theme.RESET} ❯ ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if choice == "0":
            break
        elif choice in categories:
            cat = categories[choice]
            install_native_packages(cat["name"], cat["packages"])
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "6":
            install_metasploit_official()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "7":
            install_burpsuite_community()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "8":
            setup_kali_docker()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice.upper() == "A":
            all_pkgs = " ".join([c["packages"] for c in categories.values()])
            install_native_packages("Semua Suite Native", all_pkgs)
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")

def main():
    show_menu()

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n{Theme.PEACH}[*] Program dihentikan.{Theme.RESET}")
        sys.exit(0)

