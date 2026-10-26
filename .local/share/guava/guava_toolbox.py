#!/usr/bin/env python3
"""
GUAVA TOOLBOX - Master Control Suite untuk Linux (Mint / Ubuntu / Debian)
Dibuat oleh: ArioDev7
Menghubungkan dan mengelola seluruh toolkit ricing, dev environment, AI agents,
manajemen sistem, backup, jaringan, dan keamanan dalam satu antarmuka terpadu.
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

def get_script_dir():
    """Mendapatkan direktori tempat script guava_toolbox berada."""
    return os.path.dirname(os.path.abspath(__file__))

def run_subscript(script_name):
    """Menjalankan salah satu modul python di folder ricing dengan pembersihan layar."""
    script_path = os.path.join(get_script_dir(), script_name)
    if not os.path.exists(script_path):
        clear_screen()
        print_status_card("⚠️ MODUL TIDAK DITEMUKAN", [
            ("File", script_name, Theme.RED),
            ("Status", f"Tidak ditemukan di {get_script_dir()}", Theme.GRAY)
        ])
        input(f" {Theme.PEACH}◆ Tekan [ENTER] untuk kembali ke menu...{Theme.RESET}")
        return

    clear_screen()
    try:
        subprocess.run([sys.executable, script_path])
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print_status_card("⚠️ KENDALA EKSEKUSI", [
            ("Modul", script_name, Theme.RED),
            ("Error", str(e), Theme.GRAY)
        ])
        input(f" {Theme.PEACH}◆ Tekan [ENTER] untuk kembali ke menu...{Theme.RESET}")

def install_global_shortcut():
    """Memasang executable shortcut 'guava' ke ~/.local/bin agar dapat dipanggil dari mana saja (Fish, Bash, Zsh)."""
    home = os.path.expanduser("~")
    local_bin = os.path.join(home, ".local", "bin")
    os.makedirs(local_bin, exist_ok=True)
    shortcut_path = os.path.join(local_bin, "guava")
    script_path = os.path.join(get_script_dir(), "guava_toolbox.py")

    content = f"""#!/bin/sh
exec python3 "{script_path}" "$@"
"""
    try:
        with open(shortcut_path, "w") as f:
            f.write(content)
        os.chmod(shortcut_path, 0o755)
        print_status_card("✨ SHORTCUT BERHASIL DIPASANG", [
            ("Perintah", "guava", Theme.MINT),
            ("Lokasi", shortcut_path, Theme.CYAN),
            ("Akses", "Ketik 'guava' langsung di Fish Shell atau terminal mana saja", Theme.WHITE)
        ])
    except Exception as e:
        print_status_card("⚠️ GAGAL MEMASANG SHORTCUT", [
            ("Error", str(e), Theme.RED)
        ])

def get_system_summary():
    """Mengambil ringkasan sistem yang rapi dan ringkas untuk status bar header."""
    try:
        distro = subprocess.check_output("lsb_release -ds 2>/dev/null || cat /etc/issue | head -n 1", shell=True).decode().strip()
        kernel = subprocess.check_output("uname -r", shell=True).decode().strip().split("-")[0]
        shell_env = os.path.basename(os.getenv("SHELL", "sh"))
        shell_str = "fish" if "fish" in shell_env else ("fish ready" if shutil.which("fish") else shell_env)

        info = f"{distro} • Kernel {kernel} • Shell: {shell_str} • by ArioDev7"
        if get_display_width(info) > 74:
            while get_display_width(info) > 71:
                info = info[:-1]
            info += "..."
        return info
    except Exception:
        return "Linux System • Kernel 6.x • Shell: fish/bash • by ArioDev7"

def show_main_menu():
    """Menu utama terpadu Guava Toolbox dalam format 2 kolom rounded box ricing."""
    modules = [
        ("1", "ai_agents.py", "🤖 AI Agents & Coding Suite"),
        ("2", "app_installer.py", "📦 App Installer & Ricing"),
        ("3", "tech_stack.py", "⚡ Tech Stack & Dev Env"),
        ("4", "mount_external_hdd.py", "💽 Mount & Automount Ext HDD"),
        ("5", "git_manager.py", "🐙 Multi-Repo Git Manager"),
        ("6", "install_nethunter.py", "🛡️ Cybersecurity & Pentest"),
        ("7", "share_files.py", "🌐 Instant LAN File Sharing"),
        ("8", "system_cleaner.py", "🧹 Deep System Cleaner Pro"),
        ("9", "system_backup.py", "💾 Backup & Restore Dotfiles"),
        ("10", "system_dashboard.py", "📊 Live Hardware Monitor"),
        ("11", "network_tools.py", "📡 Network & Wi-Fi Toolkit")
    ]
    w1, w2 = 37, 40
    d1 = "─" * w1
    d2 = "─" * w2

    while True:
        clear_screen()
        print(make_box_top("🌿 GUAVA TOOLBOX", badge="v2.5"))

        sys_line = get_system_summary()
        raw_sys = f"  {sys_line}"
        pad_sys = " " * max(0, 78 - get_display_width(raw_sys))
        print(f"{Theme.BORDER}│{Theme.RESET}{Theme.GRAY}  {sys_line}{Theme.RESET}{pad_sys}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}├{d1}┬{d2}┤{Theme.RESET}")

        # Tampilkan modul dalam 2 kolom tanpa deskripsi panjang
        for i in range(0, len(modules), 2):
            num1, _, title1 = modules[i]
            col1 = format_menu_col(num1, title1, width=w1, num_color=Theme.MINT, title_color=Theme.BOLD)
            if i + 1 < len(modules):
                num2, _, title2 = modules[i + 1]
                col2 = format_menu_col(num2, title2, width=w2, num_color=Theme.MINT, title_color=Theme.BOLD)
            else:
                col2 = " " * w2
            print(f"{Theme.BORDER}│{Theme.RESET}{col1}{Theme.BORDER}│{Theme.RESET}{col2}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}├{d1}┼{d2}┤{Theme.RESET}")

        ctrls = [
            ("F", "Buka Fish Shell Interactive"),
            ("G", "Pasang Shortcut 'guava'"),
            ("U", "Update Repositori Sistem"),
            ("0", "Keluar dari Toolbox")
        ]

        for i in range(0, len(ctrls), 2):
            k1, label1 = ctrls[i]
            col1 = format_menu_col(k1, label1, width=w1, num_color=Theme.CYAN if k1 != "0" else Theme.RED)
            k2, label2 = ctrls[i + 1]
            col2 = format_menu_col(k2, label2, width=w2, num_color=Theme.CYAN if k2 != "0" else Theme.RED)
            print(f"{Theme.BORDER}│{Theme.RESET}{col1}{Theme.BORDER}│{Theme.RESET}{col2}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}╰{d1}┴{d2}╯{Theme.RESET}")

        choice = input(f"\n {Theme.MINT}◆{Theme.RESET} {Theme.CYAN}guava{Theme.RESET} {Theme.PEACH}❯{Theme.RESET} ").strip()

        if choice == "0":
            print(f"\n {Theme.MINT}[*] Terima kasih telah menggunakan Guava Toolbox! 🍃{Theme.RESET}\n")
            break
        elif choice.upper() == "F":
            clear_screen()
            if shutil.which("fish"):
                print_status_card("🐟 FISH SHELL", [
                    ("Status", "Memasuki sesi Fish Shell interaktif...", Theme.CYAN),
                    ("Petunjuk", "Ketik 'exit' untuk kembali ke Guava Toolbox", Theme.PEACH)
                ])
                subprocess.run(["fish"])
            else:
                print_status_card("⚠️ FISH SHELL BELUM TERPASANG", [
                    ("Status", "Fish Shell belum terpasang di sistem", Theme.RED)
                ])
                print(f" {Theme.PEACH}◆ Pasang Fish Shell via APT sekarang? (y/n): {Theme.RESET}", end="")
                if input().strip().lower() == "y":
                    sudo = "" if (hasattr(os, "geteuid") and os.geteuid() == 0) else "sudo "
                    subprocess.run(f"{sudo}apt update && {sudo}apt install -y fish", shell=True)
                    input(f"\n {Theme.PEACH}Tekan [ENTER] untuk kembali ke menu...{Theme.RESET}")
        elif choice.upper() == "G":
            clear_screen()
            install_global_shortcut()
            input(f"\n {Theme.PEACH}◆ Tekan [ENTER] untuk kembali ke menu...{Theme.RESET}")
        elif choice.upper() == "U":
            clear_screen()
            print_status_card("🔄 PEMBARUAN SISTEM", [
                ("Tindakan", "APT Update & Upgrade", Theme.BOLD + Theme.WHITE),
                ("Status", "Memperbarui repositori dan paket Linux...", Theme.PEACH)
            ])
            sudo = "" if (hasattr(os, "geteuid") and os.geteuid() == 0) else "sudo "
            subprocess.run(f"{sudo}apt update && {sudo}apt upgrade -y", shell=True)
            print()
            print_status_card("✨ PEMBARUAN SELESAI", [
                ("Status", "● Repositori & sistem berhasil diperbarui", Theme.MINT)
            ])
            input(f" {Theme.PEACH}◆ Tekan [ENTER] untuk kembali ke menu utama...{Theme.RESET}")
        elif choice.isdigit():
            val = int(choice)
            if 1 <= val <= len(modules):
                target_script = modules[val - 1][1]
                run_subscript(target_script)
            else:
                print(f" {Theme.RED}[!] Nomor menu di luar jangkauan (1-{len(modules)}).{Theme.RESET}")
                time.sleep(1)
        else:
            print(f" {Theme.RED}[!] Pilihan tidak dikenali.{Theme.RESET}")
            time.sleep(1)

def main():
    try:
        show_main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[*] Guava Toolbox dihentikan oleh pengguna (Ctrl+C).{Colors.RESET}\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
