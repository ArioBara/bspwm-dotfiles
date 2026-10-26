#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
autostart-manager: Linux Mint & BSPWM Autostart Applications & Services Manager
Author: ArioDev7
Theme: Catppuccin Mocha
"""

import os
import sys
import re
import time
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
SURFACE = "\033[38;2;49;50;68m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

USER_AUTOSTART = Path.home() / ".config" / "autostart"
SYSTEM_AUTOSTART = Path("/etc/xdg/autostart")
BSPWMRC_PATH = Path.home() / ".config" / "bspwm" / "bspwmrc"

BANNER = rf"""{MAUVE}{BOLD}
     _   _   _ _____ ___  ____ _____  _    ____ _____ 
    / \ | | | |_   _/ _ \/ ___|_   _|/ \  |  _ \_   _|
   / _ \| | | | | || | | \___ \ | | / _ \ | |_) || |  
  / ___ \ |_| | | || |_| |___) || |/ ___ \|  _ < | |  
 /_/   \_\___/  |_| \___/|____/ |_/_/   \_\_| \_\|_|  
{RESET}{TEAL}  ⚙️  Autostart Manager • Kelola Aplikasi & Layanan Startup • by ArioDev7{RESET}
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

# -----------------------------------------------------------------------------
# XDG AUTOSTART HANDLERS (~/.config/autostart & /etc/xdg/autostart)
# -----------------------------------------------------------------------------

def parse_desktop_file(filepath):
    info = {
        "path": filepath,
        "filename": filepath.name,
        "name": filepath.stem,
        "exec": "",
        "comment": "",
        "enabled": True,
        "is_user": filepath.parent == USER_AUTOSTART
    }

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("Name=") and not info["name"] or info["name"] == filepath.stem:
                    info["name"] = line.split("=", 1)[1].strip()
                elif line.startswith("Exec="):
                    info["exec"] = line.split("=", 1)[1].strip()
                elif line.startswith("Comment="):
                    info["comment"] = line.split("=", 1)[1].strip()
                elif line.startswith("Hidden="):
                    val = line.split("=", 1)[1].strip().lower()
                    if val == "true":
                        info["enabled"] = False
                elif line.startswith("X-GNOME-Autostart-enabled="):
                    val = line.split("=", 1)[1].strip().lower()
                    if val == "false":
                        info["enabled"] = False
    except Exception:
        pass

    return info

def get_xdg_autostarts():
    apps = {}

    # 1. System autostarts
    if SYSTEM_AUTOSTART.exists():
        for f in SYSTEM_AUTOSTART.glob("*.desktop"):
            info = parse_desktop_file(f)
            apps[f.name] = info

    # 2. User autostarts (overrides system)
    USER_AUTOSTART.mkdir(parents=True, exist_ok=True)
    for f in USER_AUTOSTART.glob("*.desktop"):
        info = parse_desktop_file(f)
        apps[f.name] = info

    app_list = list(apps.values())
    app_list.sort(key=lambda x: x["name"].lower())
    return app_list

def toggle_xdg_autostart(app):
    USER_AUTOSTART.mkdir(parents=True, exist_ok=True)
    target_user_file = USER_AUTOSTART / app["filename"]

    new_state = not app["enabled"]
    state_str = "HIDUP (ON)" if new_state else "MATI (OFF)"

    # If file doesn't exist in user dir yet, copy from system
    if not target_user_file.exists():
        if app["path"].exists():
            shutil.copy2(app["path"], target_user_file)
        else:
            with open(target_user_file, "w") as f:
                f.write("[Desktop Entry]\nType=Application\n")
                f.write(f"Name={app['name']}\n")
                f.write(f"Exec={app['exec']}\n")

    # Read and modify flags
    lines = []
    has_hidden = False
    has_gnome = False

    with open(target_user_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("Hidden="):
                lines.append(f"Hidden={'false' if new_state else 'true'}\n")
                has_hidden = True
            elif line.startswith("X-GNOME-Autostart-enabled="):
                lines.append(f"X-GNOME-Autostart-enabled={'true' if new_state else 'false'}\n")
                has_gnome = True
            else:
                lines.append(line)

    if not has_hidden:
        lines.append(f"Hidden={'false' if new_state else 'true'}\n")
    if not has_gnome:
        lines.append(f"X-GNOME-Autostart-enabled={'true' if new_state else 'false'}\n")

    with open(target_user_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"\n{GREEN}✓ Status aplikasi '{app['name']}' berhasil diubah menjadi: {BOLD}{state_str}{RESET}")
    time.sleep(1)

def add_custom_xdg_autostart():
    clear()
    print(BANNER)
    print(f"{BOLD}{GREEN}=== TAMBAH APLIKASI AUTOSTART BARU ==={RESET}\n")

    name = input(f"{PEACH}Nama Aplikasi (contoh: Discord, Spotify, Telegram): {RESET}").strip()
    if not name:
        print(f"{RED}Nama tidak boleh kosong!{RESET}")
        time.sleep(1)
        return

    cmd = input(f"{PEACH}Perintah Eksekusi / Terminal (contoh: discord, spotify, /path/to/script.sh): {RESET}").strip()
    if not cmd:
        print(f"{RED}Perintah tidak boleh kosong!{RESET}")
        time.sleep(1)
        return

    comment = input(f"{PEACH}Keterangan Singkat (opsional): {RESET}").strip() or f"Autostart {name}"

    slug = re.sub(r'[^a-zA-Z0-9_\-]', '', name.lower().replace(" ", "-")) + ".desktop"
    target_file = USER_AUTOSTART / slug

    content = f"""[Desktop Entry]
Type=Application
Version=1.0
Name={name}
Comment={comment}
Exec={cmd}
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
"""
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n{GREEN}✓ Aplikasi '{name}' berhasil didaftarkan ke Autostart sistem!{RESET}")
    time.sleep(1.2)

def delete_user_autostart(app):
    if not app["is_user"]:
        print(f"{YELLOW}Aplikasi ini adalah bawaan sistem (/etc/xdg/autostart). Gunakan opsi toggle untuk mematikannya.{RESET}")
        time.sleep(1.5)
        return

    confirm = input(f"{RED}Yakin ingin menghapus konfigurasi autostart '{app['name']}'? (y/n): {RESET}").strip().lower()
    if confirm == "y":
        try:
            app["path"].unlink(missing_ok=True)
            print(f"{GREEN}✓ Berhasil dihapus.{RESET}")
        except Exception as e:
            print(f"{RED}Gagal menghapus: {e}{RESET}")
        time.sleep(1)

# -----------------------------------------------------------------------------
# BSPWM STARTUP SERVICES (~/.config/bspwm/bspwmrc)
# -----------------------------------------------------------------------------

BSPWM_SERVICES = [
    {
        "id": "picom",
        "name": "Picom Compositor (Transparansi & Efek Jendela)",
        "pattern": r"picom\s+--config",
        "desc": "Efek visual transparansi dan bayangan jendela (saat ini dinonaktifkan demi performa)."
    },
    {
        "id": "polybar",
        "name": "Polybar (Top Status Bar / Panel Atas)",
        "pattern": r"polybar/launch\.sh",
        "desc": "Panel informasi atas: workspace, jam, status RAM, CPU, dan tray sistem."
    },
    {
        "id": "dunst",
        "name": "Dunst (Notification Daemon / Pop-up Pesan)",
        "pattern": r"dunst\s+-config",
        "desc": "Daemon pop-up notifikasi sistem di sudut kanan atas layar."
    },
    {
        "id": "wallpaper",
        "name": "Wallpaper Daemon (set_wallpaper.sh)",
        "pattern": r"set_wallpaper\.sh",
        "desc": "Memasang wallpaper desktop secara otomatis saat sistem pertama kali login."
    },
    {
        "id": "playerctld",
        "name": "Playerctl Daemon (Kontrol Tombol Media Keyboard)",
        "pattern": r"playerctld\s+daemon",
        "desc": "Menghubungkan tombol multimedia Fn keyboard ke pemutar musik."
    }
]

def get_bspwm_services_status():
    if not BSPWMRC_PATH.exists():
        return []

    with open(BSPWMRC_PATH, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    results = []
    for s in BSPWM_SERVICES:
        pat = s["pattern"]
        # Find matching line
        match = re.search(r"^(#?\s*.*" + pat + r".*)$", content, re.MULTILINE)
        enabled = False
        if match:
            line = match.group(1).strip()
            # If line doesn't start with '#', it's enabled
            enabled = not line.startswith("#")

        results.append({
            "id": s["id"],
            "name": s["name"],
            "desc": s["desc"],
            "pattern": pat,
            "enabled": enabled
        })

    return results

def toggle_bspwm_service(srv):
    if not BSPWMRC_PATH.exists():
        return

    # Backup bspwmrc
    bak_path = BSPWMRC_PATH.with_suffix(".bak")
    shutil.copy2(BSPWMRC_PATH, bak_path)

    with open(BSPWMRC_PATH, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    new_lines = []
    pat = srv["pattern"]
    new_state = not srv["enabled"]

    for line in lines:
        if re.search(pat, line):
            stripped = line.strip()
            if new_state: # Turn ON: remove leading '#'
                cleaned = re.sub(r"^#+\s*", "", line)
                new_lines.append(cleaned)
            else: # Turn OFF: add leading '# '
                if not stripped.startswith("#"):
                    new_lines.append(f"# {line}")
                else:
                    new_lines.append(line)
        else:
            new_lines.append(line)

    with open(BSPWMRC_PATH, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    st_label = f"{GREEN}AKTIF (ON){RESET}" if new_state else f"{RED}NONAKTIF (OFF){RESET}"
    print(f"\n{GREEN}✓ Layanan '{srv['name']}' berhasil diubah menjadi: {st_label}")
    print(f"{SUBTEXT}Salinan cadangan tersimpan di {bak_path.name}.{RESET}")
    time.sleep(1.2)

# -----------------------------------------------------------------------------
# UI RENDERERS
# -----------------------------------------------------------------------------

def show_xdg_menu():
    page = 0
    page_size = 12
    search_q = ""

    while True:
        clear()
        print(BANNER)
        all_apps = get_xdg_autostarts()

        if search_q:
            filtered = [a for a in all_apps if search_q.lower() in a["name"].lower() or search_q.lower() in a["exec"].lower()]
        else:
            filtered = all_apps

        total_pages = max(1, (len(filtered) + page_size - 1) // page_size)
        page = max(0, min(page, total_pages - 1))
        start_idx = page * page_size
        visible = filtered[start_idx:start_idx + page_size]

        q_info = f" • Pencarian: '{search_q}'" if search_q else ""
        print(f"  {BOLD}{BLUE}=== APLIKASI AUTOSTART DESKTOP (XDG) ==={RESET} {SUBTEXT}(Hal {page+1}/{total_pages}{q_info}){RESET}")
        print(f"  {SUBTEXT}Ketik nomor baris untuk langsung MENGHIDUPKAN (ON) atau MEMATIKAN (OFF).{RESET}\n")

        col_w = [4, 13, 30, 32]
        top = OVERLAY + "┌" + "┬".join("─" * (w + 2) for w in col_w) + "┐" + RESET
        mid = OVERLAY + "├" + "┼".join("─" * (w + 2) for w in col_w) + "┤" + RESET
        bot = OVERLAY + "└" + "┴".join("─" * (w + 2) for w in col_w) + "┘" + RESET

        print(top)
        header = OVERLAY + "│ " + (OVERLAY + " │ ").join([
            cell("No", col_w[0], color=PEACH + BOLD),
            cell("Status", col_w[1], color=BLUE + BOLD),
            cell("Nama Aplikasi", col_w[2], color=TEXT + BOLD),
            cell("Perintah / File", col_w[3], color=YELLOW + BOLD)
        ]) + OVERLAY + " │" + RESET
        print(header)
        print(mid)

        for idx, app in enumerate(visible, start=1):
            st_text = "[ON]  Aktif" if app["enabled"] else "[OFF] Mati"
            st_color = GREEN if app["enabled"] else RED
            app_name = app["name"]
            exec_preview = app["exec"] or app["filename"]
            row = OVERLAY + "│ " + (OVERLAY + " │ ").join([
                cell(f"[{idx:02d}]", col_w[0], color=PINK),
                cell(st_text, col_w[1], color=st_color),
                cell(app_name, col_w[2], color=TEXT),
                cell(exec_preview, col_w[3], color=SUBTEXT)
            ]) + OVERLAY + " │" + RESET
            print(row)

        print(bot)

        print(f"\n  {GREEN}[A]{RESET} ➕ Tambah Aplikasi Baru  │  {YELLOW}[F]{RESET} 🔍 Filter Cari Nama   │  {RED}[D]{RESET} ❌ Hapus Custom")
        if total_pages > 1:
            print(f"  {BLUE}[N]{RESET} ➔ Halaman Berikutnya     │  {BLUE}[P]{RESET} ⬅️  Halaman Sebelumnya")
        print(f"  {RED}[0]{RESET} ⬅️  Kembali ke Menu Utama")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}")

        pilihan = input(f"{YELLOW}Pilih aksi [nomor / A / F / D / N / P / 0]: {RESET}").strip()

        if pilihan == "0":
            break
        elif pilihan.lower() == "a":
            add_custom_xdg_autostart()
        elif pilihan.lower() == "f":
            search_q = input(f"{PEACH}Filter nama aplikasi (kosongkan untuk reset): {RESET}").strip()
            page = 0
        elif pilihan.lower() == "n" and total_pages > 1:
            page = (page + 1) % total_pages
        elif pilihan.lower() == "p" and total_pages > 1:
            page = (page - 1) % total_pages
        elif pilihan.lower() == "d":
            del_no = input(f"{RED}Ketik nomor baris aplikasi yang ingin dihapus: {RESET}").strip()
            if del_no.isdigit() and 1 <= int(del_no) <= len(visible):
                delete_user_autostart(visible[int(del_no) - 1])
        elif pilihan.isdigit():
            val = int(pilihan)
            if 1 <= val <= len(visible):
                toggle_xdg_autostart(visible[val - 1])

def show_bspwm_menu():
    while True:
        clear()
        print(BANNER)
        services = get_bspwm_services_status()

        print(f"  {BOLD}{MAUVE}=== LAYANAN STARTUP BSPWM (bspwmrc) ==={RESET}")
        print(f"  {SUBTEXT}Layanan inti yang dieksekusi saat window manager pertama kali dimulai.{RESET}")
        print(f"  {SUBTEXT}Pilih nomor layanan untuk mengaktifkan / menonaktifkan.{RESET}\n")

        col_w = [4, 13, 56]
        top = OVERLAY + "┌" + "┬".join("─" * (w + 2) for w in col_w) + "┐" + RESET
        mid = OVERLAY + "├" + "┼".join("─" * (w + 2) for w in col_w) + "┤" + RESET
        bot = OVERLAY + "└" + "┴".join("─" * (w + 2) for w in col_w) + "┘" + RESET

        print(top)
        header = OVERLAY + "│ " + (OVERLAY + " │ ").join([
            cell("No", col_w[0], color=PEACH + BOLD),
            cell("Status", col_w[1], color=BLUE + BOLD),
            cell("Nama Layanan & Deskripsi", col_w[2], color=TEXT + BOLD)
        ]) + OVERLAY + " │" + RESET
        print(header)
        print(mid)

        for idx, s in enumerate(services, start=1):
            st_text = "[ON]  Aktif" if s["enabled"] else "[OFF] Mati"
            st_color = GREEN if s["enabled"] else RED
            row = OVERLAY + "│ " + (OVERLAY + " │ ").join([
                cell(f"[{idx:02d}]", col_w[0], color=PINK),
                cell(st_text, col_w[1], color=st_color),
                cell(s["name"], col_w[2], color=TEXT)
            ]) + OVERLAY + " │" + RESET
            print(row)

        print(bot)
        print("")

        for idx, s in enumerate(services, start=1):
            st_badge = f"{GREEN}[ON]{RESET}" if s["enabled"] else f"{RED}[OFF]{RESET}"
            print(f"  {PINK}[{idx:02d}]{RESET} {st_badge} {SUBTEXT}{s['desc']}{RESET}")

        print(f"\n  {BLUE}[E]{RESET} ✏️  Buka File ~/.config/bspwm/bspwmrc di Neovim")
        print(f"  {RED}[0]{RESET} ⬅️  Kembali ke Menu Utama")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}")

        pilihan = input(f"{YELLOW}Pilih nomor layanan untuk di-toggle [1-{len(services)} / E / 0]: {RESET}").strip()

        if pilihan == "0":
            break
        elif pilihan.lower() == "e":
            subprocess.run(["nvim", str(BSPWMRC_PATH)])
        elif pilihan.isdigit():
            val = int(pilihan)
            if 1 <= val <= len(services):
                toggle_bspwm_service(services[val - 1])

def main():
    while True:
        clear()
        print(BANNER)
        xdg_count = len(get_xdg_autostarts())
        xdg_on = sum(1 for a in get_xdg_autostarts() if a["enabled"])
        bspwm_srv = get_bspwm_services_status()
        bspwm_on = sum(1 for s in bspwm_srv if s["enabled"])

        print(f"  {OVERLAY}Ringkasan Autostart:{RESET}")
        print(f"  • Aplikasi Desktop (XDG) : {BOLD}{GREEN}{xdg_on}{RESET} Aktif / {xdg_count} Terdaftar")
        print(f"  • Layanan BSPWM (bspwmrc): {BOLD}{GREEN}{bspwm_on}{RESET} Aktif / {len(bspwm_srv)} Terdaftar")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}\n")

        print(f"  {PEACH}[1]{RESET}  🖥️  Kelola Aplikasi Autostart Desktop (XDG ~/.config/autostart)")
        print(f"  {BLUE}[2]{RESET}  ⚙️  Kelola Layanan Startup BSPWM (Picom, Polybar, Dunst, Wallpaper)")
        print(f"  {TEAL}[3]{RESET}  ➕ Tambah Aplikasi Baru ke Autostart Sistem")
        print(f"  {RED}[0]{RESET}  🚪 Keluar")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}")

        pilihan = input(f"{YELLOW}Pilih menu [0-3]: {RESET}").strip()

        if pilihan == "0" or pilihan.lower() == "q":
            print(f"{GREEN}Sampai jumpa! Pengaturan autostart tersimpan aman ⚙️{RESET}")
            break
        elif pilihan == "1":
            show_xdg_menu()
        elif pilihan == "2":
            show_bspwm_menu()
        elif pilihan == "3":
            add_custom_xdg_autostart()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{GREEN}Keluar.{RESET}")
