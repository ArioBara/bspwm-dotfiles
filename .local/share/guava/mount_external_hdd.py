#!/usr/bin/env python3
"""
Script Mount & Automount HDD / SSD Eksternal untuk Linux (Mint / Ubuntu / Debian).
Mendukung deteksi UUID, konfigurasi /etc/fstab permanen (dengan opsi nofail & x-systemd.automount),
manajemen driver NTFS/exFAT/ext4/Btrfs, serta pembuatan shortcut ke direktori Home.
"""

import os
import json
import subprocess
import sys
import time

import os
import json
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

def is_root():
    return os.geteuid() == 0 if hasattr(os, "geteuid") else False

def get_sudo_prefix():
    if is_root():
        return ""
    return "sudo "

def run_cmd(command, check=True, shell=True, capture=False):
    try:
        if capture:
            res = subprocess.run(command, shell=shell, check=check, capture_output=True, text=True)
            return res.stdout.strip()
        else:
            return subprocess.run(command, shell=shell, check=check)
    except subprocess.CalledProcessError:
        return None

def check_linux_env():
    if not sys.platform.startswith("linux"):
        sys.exit(0)

def check_and_install_fs_drivers():
    clear_screen()
    print_status_card("📦 DRIVER FILESYSTEM", [
        ("Status", "Memeriksa paket driver NTFS, exFAT, Btrfs...", Theme.CYAN),
    ])
    sudo = get_sudo_prefix()
    drivers = ["ntfs-3g", "exfatprogs", "e2fsprogs", "dosfstools", "btrfs-progs", "util-linux"]
    needed = []
    
    for d in drivers:
        res = subprocess.run(f"dpkg -s {d} 2>/dev/null | grep -q 'Status: install ok installed'", shell=True)
        if res.returncode != 0:
            needed.append(d)

    if needed:
        pkg_str = " ".join(needed)
        run_cmd(f"{sudo}apt update -y && {sudo}apt install -y {pkg_str}")
        print_status_card("✨ DRIVER SELESAI", [
            ("Dipasang", pkg_str, Theme.MINT),
            ("Status", "Driver siap digunakan", Theme.MINT),
        ])
    else:
        print_status_card("✨ DRIVER SUDAH LENGKAP", [
            ("Status", "Seluruh driver (NTFS-3G, exFAT, ext4, Btrfs) sudah terpasang", Theme.MINT),
        ])

def get_disk_list():
    raw_json = run_cmd("lsblk -J -o NAME,FSTYPE,LABEL,UUID,SIZE,MOUNTPOINT,TYPE,TRAN,MODEL", capture=True)
    if not raw_json:
        return []

    try:
        data = json.loads(raw_json)
    except Exception:
        return []

    disks = []

    def parse_devices(devices):
        for dev in devices:
            dev_type = dev.get("type", "")
            fstype = dev.get("fstype", "")
            name = dev.get("name", "")
            
            if dev_type in ["part", "disk"] and fstype and dev.get("uuid"):
                dev_path = f"/dev/{name}"
                disks.append({
                    "path": dev_path,
                    "name": name,
                    "fstype": fstype,
                    "label": dev.get("label") or "NO_LABEL",
                    "uuid": dev.get("uuid", ""),
                    "size": dev.get("size", "N/A"),
                    "mountpoint": dev.get("mountpoint") or "",
                    "tran": dev.get("tran") or "",
                    "model": dev.get("model") or ""
                })

            if "children" in dev:
                parse_devices(dev["children"])

    if "blockdevices" in data:
        parse_devices(data["blockdevices"])

    return disks

def print_disk_table(disks):
    """Menampilkan card tabel disk dengan border rounded ricing."""
    top = make_box_top("💾 PARTISI DISK TERDETEKSI", badge="v2.5", total_w=80)
    print(top)

    if not disks:
        msg = "  (Tidak ditemukan partisi eksternal dengan filesystem valid)"
        pad = " " * max(0, 78 - get_display_width(msg))
        print(f"{Theme.BORDER}│{Theme.RESET}{Theme.PEACH}{msg}{Theme.RESET}{pad}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}╰{'─'*78}╯{Theme.RESET}")
        return

    hdr = f"  {'No':<4} {'Device':<12} {'Label':<16} {'FSType':<8} {'Size':<7} {'Mountpoint / Status':<25}"
    pad_h = " " * max(0, 78 - get_display_width(hdr))
    print(f"{Theme.BORDER}│{Theme.RESET}{Theme.PEACH}{hdr}{Theme.RESET}{pad_h}{Theme.BORDER}│{Theme.RESET}")
    print(f"{Theme.BORDER}├{'─'*78}┤{Theme.RESET}")

    for idx, d in enumerate(disks, start=1):
        if d['mountpoint']:
            st_color = Theme.MINT
            st_text = f"● {d['mountpoint']}"
        else:
            st_color = Theme.GRAY
            st_text = "○ [Belum di-mount]"

        c_no = f" [{idx:>2}]"
        c_dev = f" {d['path'][:11]:<11}"
        c_lbl = f" {d['label'][:15]:<15}"
        c_fs = f" {d['fstype'][:7]:<7}"
        c_sz = f" {d['size'][:6]:<6}"

        raw_left = f"{c_no}{c_dev}{c_lbl}{c_fs}{c_sz} "
        dw_left = get_display_width(raw_left)
        max_st_w = 78 - dw_left - 1
        if get_display_width(st_text) > max_st_w:
            st_text = st_text[:max_st_w-3] + "..."
        pad_end = " " * max(0, 78 - dw_left - get_display_width(st_text))

        line = f"{Theme.NUM}{c_no}{Theme.RESET}{Theme.WHITE}{c_dev}{Theme.PEACH}{c_lbl}{Theme.CYAN}{c_fs}{Theme.WHITE}{c_sz}{Theme.RESET} {st_color}{st_text}{Theme.RESET}{pad_end}"
        print(f"{Theme.BORDER}│{Theme.RESET}{line}{Theme.BORDER}│{Theme.RESET}")

    print(f"{Theme.BORDER}╰{'─'*78}╯{Theme.RESET}")

def get_mount_options_for_fstab(fstype, uid=1000, gid=1000):
    fstype_lower = fstype.lower()
    if fstype_lower in ["ntfs", "ntfs-3g"]:
        return "ntfs-3g", f"defaults,auto,users,rw,nofail,uid={uid},gid={gid},dmask=022,fmask=133,windows_names,x-systemd.device-timeout=5,x-systemd.automount", "0 0"
    elif fstype_lower == "exfat":
        return "exfat", f"defaults,auto,users,rw,nofail,uid={uid},gid={gid},dmask=022,fmask=133,x-systemd.device-timeout=5,x-systemd.automount", "0 0"
    elif fstype_lower in ["vfat", "fat32", "fat"]:
        return "vfat", f"defaults,auto,users,rw,nofail,uid={uid},gid={gid},dmask=022,fmask=133,x-systemd.device-timeout=5,x-systemd.automount", "0 0"
    elif fstype_lower == "ext4":
        return "ext4", "defaults,auto,nofail,x-systemd.device-timeout=5,x-systemd.automount", "0 2"
    elif fstype_lower == "btrfs":
        return "btrfs", "defaults,auto,nofail,compress=zstd,x-systemd.device-timeout=5,x-systemd.automount", "0 0"
    else:
        return fstype, "defaults,auto,nofail,x-systemd.device-timeout=5,x-systemd.automount", "0 0"

def create_home_symlink(mountpoint, name="HDD_External"):
    home = os.path.expanduser("~")
    shortcut_path = os.path.join(home, name)
    if os.path.islink(shortcut_path) or os.path.exists(shortcut_path):
        try:
            os.remove(shortcut_path)
        except Exception:
            pass
    try:
        os.symlink(mountpoint, shortcut_path)
    except Exception:
        pass

def mount_selected_disk():
    clear_screen()
    disks = get_disk_list()
    print_disk_table(disks)
    if not disks:
        return

    try:
        choice = input(f"\n {Theme.BOLD}Pilih nomor partisi [1-{len(disks)} / 0 batal]: {Theme.RESET}").strip()
    except (KeyboardInterrupt, EOFError):
        return

    if choice == "0" or not choice.isdigit():
        return

    val = int(choice)
    if val < 1 or val > len(disks):
        return

    target_disk = disks[val - 1]
    if target_disk["mountpoint"]:
        clear_screen()
        print_status_card("ℹ️ INFO MOUNT", [
            ("Status", "Partisi sudah ter-mount", Theme.YELLOW),
            ("Device", target_disk['path'], Theme.WHITE),
            ("Lokasi", target_disk['mountpoint'], Theme.MINT),
        ])
        return

    default_name = target_disk['label'] if target_disk['label'] != "NO_LABEL" else f"external_{target_disk['name']}"
    default_mountpoint = f"/media/{os.getenv('USER', 'mint')}/{default_name}"

    try:
        user_mp = input(f" Mount point [{default_mountpoint}]: ").strip()
    except (KeyboardInterrupt, EOFError):
        return
    mountpoint = user_mp if user_mp else default_mountpoint

    clear_screen()
    print_status_card("⏳ MEMPROSES MOUNT", [
        ("Device", target_disk['path'], Theme.CYAN),
        ("FSType", target_disk['fstype'], Theme.PEACH),
        ("Target", mountpoint, Theme.MINT),
    ])

    sudo = get_sudo_prefix()
    run_cmd(f"{sudo}mkdir -p '{mountpoint}'")

    fstype = target_disk["fstype"].lower()
    uid = os.getuid() if hasattr(os, "getuid") else 1000
    gid = os.getgid() if hasattr(os, "getgid") else 1000

    if fstype in ["ntfs", "ntfs-3g"]:
        cmd = f"{sudo}mount -t ntfs-3g -o rw,uid={uid},gid={gid},dmask=022,fmask=133 '{target_disk['path']}' '{mountpoint}'"
    elif fstype == "exfat":
        cmd = f"{sudo}mount -t exfat -o rw,uid={uid},gid={gid},dmask=022,fmask=133 '{target_disk['path']}' '{mountpoint}'"
    elif fstype in ["vfat", "fat32", "fat"]:
        cmd = f"{sudo}mount -t vfat -o rw,uid={uid},gid={gid},dmask=022,fmask=133 '{target_disk['path']}' '{mountpoint}'"
    else:
        cmd = f"{sudo}mount '{target_disk['path']}' '{mountpoint}' && {sudo}chown -R {uid}:{gid} '{mountpoint}'"

    res = run_cmd(cmd)
    if res is not None and res.returncode == 0:
        create_home_symlink(mountpoint, default_name)
        print_status_card("✨ MOUNT BERHASIL", [
            ("Status", "Partisi Berhasil Di-mount", Theme.MINT),
            ("Device", target_disk['path'], Theme.WHITE),
            ("Lokasi", mountpoint, Theme.CYAN),
        ])
    else:
        print_status_card("❌ MOUNT GAGAL", [
            ("Status", "Gagal me-mount partisi", Theme.RED),
            ("Device", target_disk['path'], Theme.WHITE),
        ])

def configure_automount():
    clear_screen()
    disks = get_disk_list()
    print_disk_table(disks)
    if not disks:
        return

    try:
        choice = input(f"\n {Theme.BOLD}Pilih partisi untuk AUTOMOUNT permanen [1-{len(disks)} / 0 batal]: {Theme.RESET}").strip()
    except (KeyboardInterrupt, EOFError):
        return

    if choice == "0" or not choice.isdigit():
        return

    val = int(choice)
    if val < 1 or val > len(disks):
        return

    target_disk = disks[val - 1]
    uuid = target_disk["uuid"]
    if not uuid:
        print_status_card("❌ UUID TIDAK DITEMUKAN", [("Device", target_disk['path'], Theme.RED)])
        return

    default_name = target_disk['label'] if target_disk['label'] != "NO_LABEL" else f"external_{target_disk['name']}"
    default_mountpoint = f"/media/{os.getenv('USER', 'mint')}/{default_name}"

    try:
        user_mp = input(f" Mount point permanen [{default_mountpoint}]: ").strip()
    except (KeyboardInterrupt, EOFError):
        return
    mountpoint = user_mp if user_mp else default_mountpoint

    clear_screen()
    print_status_card("⏳ MENGONFIGURASI AUTOMOUNT", [
        ("UUID", uuid, Theme.CYAN),
        ("Target", mountpoint, Theme.MINT),
    ])

    sudo = get_sudo_prefix()
    run_cmd(f"{sudo}mkdir -p '{mountpoint}'")

    uid = os.getuid() if hasattr(os, "getuid") else 1000
    gid = os.getgid() if hasattr(os, "getgid") else 1000
    fs_driver, mount_opts, dump_pass = get_mount_options_for_fstab(target_disk["fstype"], uid, gid)

    fstab_line = f"UUID={uuid}  {mountpoint}  {fs_driver}  {mount_opts}  {dump_pass}\n"

    backup_file = f"/etc/fstab.bak.{int(time.time())}"
    run_cmd(f"{sudo}cp /etc/fstab {backup_file}")

    current_fstab = run_cmd("cat /etc/fstab", capture=True)
    if uuid in current_fstab:
        run_cmd(f"{sudo}sed -i '/{uuid}/d' /etc/fstab")

    cmd_append = f"echo '{fstab_line.strip()}' | {sudo}tee -a /etc/fstab > /dev/null"
    run_cmd(cmd_append)

    run_cmd(f"{sudo}systemctl daemon-reload")
    res = run_cmd(f"{sudo}mount -a")

    if res is not None and res.returncode == 0:
        create_home_symlink(mountpoint, default_name)
        print_status_card("✨ AUTOMOUNT AKTIF", [
            ("Status", "Berhasil Ditambahkan ke /etc/fstab", Theme.MINT),
            ("Device", target_disk['path'], Theme.WHITE),
            ("Driver", fs_driver, Theme.PEACH),
            ("Safety", "Flag 'nofail' aktif (booting aman)", Theme.MINT),
        ])
    else:
        run_cmd(f"{sudo}cp {backup_file} /etc/fstab")
        print_status_card("❌ CONFIG ERROR", [
            ("Status", "Error saat mount -a, fstab dikembalikan", Theme.RED),
        ])

def unmount_disk():
    clear_screen()
    disks = [d for d in get_disk_list() if d["mountpoint"]]
    if not disks:
        print_status_card("ℹ️ UNMOUNT DISK", [
            ("Status", "Tidak ada partisi eksternal yang sedang ter-mount", Theme.YELLOW),
        ])
        return

    print_disk_table(disks)
    try:
        choice = input(f"\n {Theme.BOLD}Pilih nomor partisi yang ingin di-UNMOUNT [1-{len(disks)} / 0 batal]: {Theme.RESET}").strip()
    except (KeyboardInterrupt, EOFError):
        return

    if choice == "0" or not choice.isdigit():
        return

    val = int(choice)
    if val < 1 or val > len(disks):
        return

    target = disks[val - 1]
    sudo = get_sudo_prefix()
    clear_screen()
    print_status_card("⏳ UNMOUNT DISK", [
        ("Device", target['path'], Theme.CYAN),
        ("Mountpoint", target['mountpoint'], Theme.PEACH),
    ])
    
    res = run_cmd(f"{sudo}umount '{target['mountpoint']}' || udisksctl unmount -b '{target['path']}'")
    if res is not None and res.returncode == 0:
        print_status_card("✨ UNMOUNT BERHASIL", [
            ("Status", "Partisi Berhasil Dilepaskan. Aman dicabut.", Theme.MINT),
        ])
    else:
        print_status_card("❌ UNMOUNT GAGAL", [
            ("Status", "Pastikan tidak ada aplikasi atau terminal yang mengakses partisi.", Theme.RED),
        ])

def remove_automount_entry():
    clear_screen()
    fstab_content = run_cmd("grep -E 'UUID=|/dev/' /etc/fstab | grep -v '^#'", capture=True)
    if not fstab_content:
        print_status_card("ℹ️ FSTAB", [
            ("Status", "Tidak ada entri mount kustom yang aktif di /etc/fstab", Theme.YELLOW),
        ])
        return

    lines = fstab_content.splitlines()
    card_items = []
    for idx, l in enumerate(lines, start=1):
        tok = l.split()[0][:25]
        tgt = l.split()[1] if len(l.split()) > 1 else ""
        card_items.append((f"[{idx}] {tok}", tgt[:30], Theme.WHITE))

    print_status_card("📋 DAFTAR ENTRI /ETC/FSTAB", card_items)

    try:
        choice = input(f" {Theme.BOLD}Pilih nomor entri yang ingin DIHAPUS [1-{len(lines)} / 0 batal]: {Theme.RESET}").strip()
    except (KeyboardInterrupt, EOFError):
        return

    if choice == "0" or not choice.isdigit():
        return

    val = int(choice)
    if val < 1 or val > len(lines):
        return

    selected_line = lines[val - 1]
    first_token = selected_line.split()[0]

    sudo = get_sudo_prefix()
    backup_file = f"/etc/fstab.bak.{int(time.time())}"
    run_cmd(f"{sudo}cp /etc/fstab {backup_file}")

    run_cmd(f"{sudo}sed -i '\\|{first_token}|d' /etc/fstab")
    run_cmd(f"{sudo}systemctl daemon-reload")

    clear_screen()
    print_status_card("✨ ENTRI DIHAPUS", [
        ("Token", first_token, Theme.PEACH),
        ("Status", "Berhasil dihapus dari /etc/fstab", Theme.MINT),
    ])

def show_main_menu():
    w1 = 37
    w2 = 40

    while True:
        clear_screen()
        print(make_box_top("🍃 EXTERNAL HDD & AUTOMOUNT TOOL", badge="v2.5", total_w=80))

        m1 = format_menu_col("1", "Scan Partisi Disk", w1, Theme.CYAN, Theme.WHITE)
        m4 = format_menu_col("4", "Unmount / Eject Disk", w2, Theme.PEACH, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{m1}{Theme.BORDER}│{Theme.RESET}{m4}{Theme.BORDER}│{Theme.RESET}")

        m2 = format_menu_col("2", "Mount Partisi Instan", w1, Theme.MINT, Theme.WHITE)
        m5 = format_menu_col("5", "Hapus Entri /etc/fstab", w2, Theme.YELLOW, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{m2}{Theme.BORDER}│{Theme.RESET}{m5}{Theme.BORDER}│{Theme.RESET}")

        m3 = format_menu_col("3", "Setup Automount Boot", w1, Theme.BLUE, Theme.WHITE)
        m6 = format_menu_col("6", "Pasang Driver Filesystem", w2, Theme.CYAN, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{m3}{Theme.BORDER}│{Theme.RESET}{m6}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}├{'─'*w1}┴{'─'*w2}┤{Theme.RESET}")
        m0 = format_menu_col("0", "Kembali ke Menu Utama", 78, Theme.RED, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{m0}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}╰{'─'*78}╯{Theme.RESET}")

        try:
            choice = input(f"\n {Theme.BOLD}{Theme.PEACH}◆ guava{Theme.RESET} › {Theme.CYAN}hdd-mount{Theme.RESET} ❯ ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if choice == "0":
            break
        elif choice == "1":
            clear_screen()
            disks = get_disk_list()
            print_disk_table(disks)
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "2":
            mount_selected_disk()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "3":
            configure_automount()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "4":
            unmount_disk()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "5":
            remove_automount_entry()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice == "6":
            check_and_install_fs_drivers()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")

def main():
    check_linux_env()
    show_main_menu()

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n{Theme.PEACH}[*] Program dihentikan.{Theme.RESET}")
        sys.exit(0)

