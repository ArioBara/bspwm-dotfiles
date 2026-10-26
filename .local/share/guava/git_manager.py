#!/usr/bin/env python3
"""
Git Repository Manager & Batch Synchronizer untuk Linux.
Memindai seluruh repositori Git di direktori kerja / Home, menampilkan status cabang,
perubahan belum di-commit, dan melakukan sinkronisasi batch (pull, fetch, push, garbage collection).
"""

import os
import subprocess
import sys
import shutil
import time

import os
import subprocess
import sys
import shutil
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

def run_git_cmd(args, cwd):
    """Menjalankan perintah git pada repositori tertentu."""
    try:
        res = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        return res.stdout.strip(), res.stderr.strip(), res.returncode
    except Exception as e:
        return "", str(e), 1

def find_git_repos(base_dir, max_depth=3):
    """Memindai direktori untuk mencari seluruh repositori git."""
    base_dir = os.path.abspath(os.path.expanduser(base_dir))
    repos = []

    for root, dirs, _ in os.walk(base_dir):
        rel_path = os.path.relpath(root, base_dir)
        depth = 0 if rel_path == "." else rel_path.count(os.sep) + 1

        if depth > max_depth:
            dirs.clear()
            continue

        dirs[:] = [d for d in dirs if d not in [".cache", ".local", "node_modules", ".cargo", ".rustup", "vendor", ".venv", "venv"]]

        if ".git" in dirs:
            repos.append(root)
            dirs.remove(".git")

    return sorted(repos)

def get_repo_info(repo_path):
    """Mengambil status detail sebuah repositori Git."""
    branch, _, _ = run_git_cmd(["branch", "--show-current"], repo_path)
    if not branch:
        branch, _, _ = run_git_cmd(["rev-parse", "--short", "HEAD"], repo_path)
        branch = f"HEAD ({branch})" if branch else "Unknown"

    status_out, _, _ = run_git_cmd(["status", "--porcelain"], repo_path)
    has_changes = len(status_out.splitlines()) if status_out else 0

    ahead, behind = 0, 0
    tracking_out, _, code = run_git_cmd(["rev-list", "--left-right", "--count", "@{upstream}...HEAD"], repo_path)
    if code == 0 and tracking_out:
        parts = tracking_out.split()
        if len(parts) == 2:
            behind = int(parts[0])
            ahead = int(parts[1])

    remote_url, _, _ = run_git_cmd(["config", "--get", "remote.origin.url"], repo_path)

    return {
        "path": repo_path,
        "name": os.path.basename(repo_path),
        "branch": branch,
        "changes": has_changes,
        "ahead": ahead,
        "behind": behind,
        "remote": remote_url or "No remote"
    }

def print_repo_table_rows(repo_list):
    """Menampilkan baris-baris repositori di dalam kartu ricing."""
    if not repo_list:
        msg = "  (Tidak ditemukan repositori Git pada direktori ini)"
        pad = " " * max(0, 78 - get_display_width(msg))
        print(f"{Theme.BORDER}│{Theme.RESET}{Theme.GRAY}{msg}{Theme.RESET}{pad}{Theme.BORDER}│{Theme.RESET}")
        return

    # Header kolom
    hdr = f"  {'No':<4} {'Repository':<23} {'Branch':<16} {'Status':<16} {'Sync':<15}"
    pad_h = " " * max(0, 78 - get_display_width(hdr))
    print(f"{Theme.BORDER}│{Theme.RESET}{Theme.PEACH}{hdr}{Theme.RESET}{pad_h}{Theme.BORDER}│{Theme.RESET}")
    print(f"{Theme.BORDER}├{'─'*78}┤{Theme.RESET}")

    for idx, r in enumerate(repo_list, start=1):
        if r['changes'] > 0:
            change_str = f"{Theme.PEACH}● {r['changes']} dirty{Theme.RESET}"
            raw_change = f"● {r['changes']} dirty"
        else:
            change_str = f"{Theme.MINT}● Clean{Theme.RESET}"
            raw_change = "● Clean"

        sync_parts = []
        if r['ahead'] > 0:
            sync_parts.append(f"↑{r['ahead']}")
        if r['behind'] > 0:
            sync_parts.append(f"↓{r['behind']}")
        raw_sync = " ".join(sync_parts) if sync_parts else "Up-to-date"
        sync_str = f"{Theme.CYAN}{raw_sync}{Theme.RESET}" if sync_parts else f"{Theme.MINT}{raw_sync}{Theme.RESET}"

        name_d = r['name'][:22]
        branch_d = r['branch'][:15]

        # Buat padding presisi
        c_no = f" [{idx:>2}]"
        c_name = f" {name_d:<22}"
        c_branch = f" {branch_d:<15}"
        pad_change = " " * max(0, 16 - get_display_width(raw_change))
        pad_sync = " " * max(0, 15 - get_display_width(raw_sync))

        line_left = f"{Theme.NUM}{c_no}{Theme.RESET}{Theme.WHITE}{c_name}{Theme.RESET}{Theme.CYAN}{c_branch}{Theme.RESET} {change_str}{pad_change}{sync_str}{pad_sync}"
        raw_full = f"{c_no}{c_name}{c_branch} {raw_change}{pad_change}{raw_sync}{pad_sync}"
        pad_end = " " * max(0, 78 - get_display_width(raw_full))

        print(f"{Theme.BORDER}│{Theme.RESET}{line_left}{pad_end}{Theme.BORDER}│{Theme.RESET}")

def batch_git_pull(repos):
    """Melakukan git pull di seluruh repositori secara otomatis."""
    clear_screen()
    print_status_card("🚀 BATCH GIT PULL", [
        ("Total Repo", f"{len(repos)} repositori", Theme.CYAN),
        ("Status", "Memulai pull...", Theme.YELLOW),
    ])
    success, failed = 0, 0

    for idx, r in enumerate(repos, start=1):
        print(f" {Theme.GRAY}[{idx}/{len(repos)}]{Theme.RESET} {Theme.BOLD}{r['name']}{Theme.RESET} ({Theme.CYAN}{r['branch']}{Theme.RESET})...", end=" ", flush=True)
        out, err, code = run_git_cmd(["pull", "--ff-only"], r['path'])
        if code == 0:
            print(f"{Theme.MINT}[✓ OK]{Theme.RESET}")
            success += 1
        else:
            print(f"{Theme.RED}[✗ GAGAL]{Theme.RESET}")
            failed += 1

    print()
    print_status_card("✨ HASIL BATCH PULL", [
        ("Berhasil", f"{success} repo", Theme.MINT),
        ("Gagal", f"{failed} repo", Theme.RED if failed > 0 else Theme.GRAY),
    ])

def batch_git_fetch(repos):
    """Melakukan git fetch --all --prune di seluruh repositori."""
    clear_screen()
    print_status_card("📡 BATCH GIT FETCH", [
        ("Total Repo", f"{len(repos)} repositori", Theme.CYAN),
        ("Status", "Sinkronisasi remote...", Theme.YELLOW),
    ])

    for idx, r in enumerate(repos, start=1):
        print(f" {Theme.GRAY}[{idx}/{len(repos)}]{Theme.RESET} Fetching: {Theme.BOLD}{r['name']}{Theme.RESET}...", end=" ", flush=True)
        _, _, code = run_git_cmd(["fetch", "--all", "--prune"], r['path'])
        if code == 0:
            print(f"{Theme.MINT}[✓ OK]{Theme.RESET}")
        else:
            print(f"{Theme.RED}[✗ Error]{Theme.RESET}")

    print()
    print_status_card("✨ HASIL BATCH FETCH", [
        ("Status", "Sinkronisasi Selesai", Theme.MINT),
    ])

def batch_git_gc(repos):
    """Mengoptimalkan penyimpanan repositori dengan git gc & prune."""
    clear_screen()
    print_status_card("🧹 BATCH GIT GC", [
        ("Total Repo", f"{len(repos)} repositori", Theme.CYAN),
        ("Status", "Mengoptimalkan dan membersihkan database repo...", Theme.YELLOW),
    ])

    for idx, r in enumerate(repos, start=1):
        print(f" {Theme.GRAY}[{idx}/{len(repos)}]{Theme.RESET} Cleaning: {Theme.BOLD}{r['name']}{Theme.RESET}...", end=" ", flush=True)
        run_git_cmd(["gc", "--auto", "--prune=now"], r['path'])
        print(f"{Theme.MINT}[✓ Selesai]{Theme.RESET}")

    print()
    print_status_card("✨ HASIL BATCH GC", [
        ("Status", "Optimasi Selesai", Theme.MINT),
    ])

def manage_single_repo(repo):
    """Menu aksi untuk satu repositori terpilih."""
    w1 = 37
    w2 = 40

    while True:
        clear_screen()
        print(make_box_top(f"🐙 REPO: {repo['name'].upper()}", badge="v2.5", total_w=80))

        # Detail repo
        p_raw = f"  Lokasi : {repo['path']}"
        if get_display_width(p_raw) > 76:
            p_raw = p_raw[:73] + "..."
        pad_p = " " * max(0, 78 - get_display_width(p_raw))
        print(f"{Theme.BORDER}│{Theme.RESET}{Theme.GRAY}  Lokasi : {Theme.RESET}{Theme.WHITE}{p_raw[11:]}{Theme.RESET}{pad_p}{Theme.BORDER}│{Theme.RESET}")

        r_raw = f"  Remote : {repo['remote']}"
        if get_display_width(r_raw) > 76:
            r_raw = r_raw[:73] + "..."
        pad_r = " " * max(0, 78 - get_display_width(r_raw))
        print(f"{Theme.BORDER}│{Theme.RESET}{Theme.GRAY}  Remote : {Theme.RESET}{Theme.PEACH}{r_raw[11:]}{Theme.RESET}{pad_r}{Theme.BORDER}│{Theme.RESET}")

        b_raw = f"  Branch : {repo['branch']}"
        pad_b = " " * max(0, 78 - get_display_width(b_raw))
        print(f"{Theme.BORDER}│{Theme.RESET}{Theme.GRAY}  Branch : {Theme.RESET}{Theme.CYAN}{repo['branch']}{Theme.RESET}{pad_b}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}├{'─'*w1}┬{'─'*w2}┤{Theme.RESET}")

        m1 = format_menu_col("1", "Git Status", w1, Theme.CYAN, Theme.WHITE)
        m2 = format_menu_col("2", "Git Pull", w2, Theme.MINT, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{m1}{Theme.BORDER}│{Theme.RESET}{m2}{Theme.BORDER}│{Theme.RESET}")

        m3 = format_menu_col("3", "Git Push", w1, Theme.PEACH, Theme.WHITE)
        m4 = format_menu_col("4", "Git Log (5 Commit)", w2, Theme.BLUE, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{m3}{Theme.BORDER}│{Theme.RESET}{m4}{Theme.BORDER}│{Theme.RESET}")

        m5 = format_menu_col("5", "Buka di Lazygit (TUI)", w1, Theme.YELLOW, Theme.WHITE)
        m0 = format_menu_col("0", "Kembali ke Daftar", w2, Theme.RED, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{m5}{Theme.BORDER}│{Theme.RESET}{m0}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}╰{'─'*w1}┴{'─'*w2}╯{Theme.RESET}")

        try:
            choice = input(f"\n {Theme.BOLD}{Theme.PEACH}◆ guava{Theme.RESET} › {Theme.CYAN}repo-action{Theme.RESET} ❯ ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "0":
            break
        elif choice == "1":
            clear_screen()
            out, _, _ = run_git_cmd(["status"], repo['path'])
            print_status_card("📋 GIT STATUS", [
                ("Repo", repo['name'], Theme.CYAN),
                ("Branch", repo['branch'], Theme.PEACH),
            ])
            print(out)
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali...{Theme.RESET}")
        elif choice == "2":
            clear_screen()
            print_status_card("🚀 GIT PULL", [
                ("Repo", repo['name'], Theme.CYAN),
                ("Status", "Menjalankan git pull...", Theme.YELLOW),
            ])
            out, err, _ = run_git_cmd(["pull"], repo['path'])
            print(out or err)
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali...{Theme.RESET}")
        elif choice == "3":
            clear_screen()
            print_status_card("🚀 GIT PUSH", [
                ("Repo", repo['name'], Theme.CYAN),
                ("Status", "Menjalankan git push...", Theme.YELLOW),
            ])
            out, err, _ = run_git_cmd(["push"], repo['path'])
            print(out or err)
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali...{Theme.RESET}")
        elif choice == "4":
            clear_screen()
            print_status_card("📜 GIT LOG (5 COMMIT)", [
                ("Repo", repo['name'], Theme.CYAN),
            ])
            out, _, _ = run_git_cmd(["log", "--oneline", "-n", "5", "--graph", "--decorate"], repo['path'])
            print(out)
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali...{Theme.RESET}")
        elif choice == "5":
            if shutil.which("lazygit"):
                clear_screen()
                subprocess.run(["lazygit"], cwd=repo['path'])
            else:
                clear_screen()
                print_status_card("❌ LAZYGIT TIDAK DITEMUKAN", [
                    ("Keterangan", "Lazygit belum terpasang di sistem", Theme.RED),
                    ("Solusi", "Pasang via tech_stack.py [Dev Tools]", Theme.PEACH),
                ])
                input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali...{Theme.RESET}")

def main():
    current_search_dir = os.getcwd()
    w1 = 37
    w2 = 40

    while True:
        clear_screen()
        print(make_box_top("🐙 GIT REPOSITORY MANAGER", badge="v2.5", total_w=80))

        raw_paths = find_git_repos(current_search_dir, max_depth=3)
        repo_data = [get_repo_info(p) for p in raw_paths]
        print_repo_table_rows(repo_data)

        print(f"{Theme.BORDER}├{'─'*78}┤{Theme.RESET}")

        # Path info
        p_info = f" Lokasi: {current_search_dir}"
        if get_display_width(p_info) > 76:
            p_info = p_info[:73] + "..."
        pad_pi = " " * max(0, 78 - get_display_width(p_info))
        print(f"{Theme.BORDER}│{Theme.RESET}{Theme.YELLOW}{p_info}{Theme.RESET}{pad_pi}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}├{'─'*w1}┬{'─'*w2}┤{Theme.RESET}")

        # Controls in 2 columns
        c1 = format_menu_col("P", "Batch Git Pull", w1, Theme.MINT, Theme.WHITE)
        c2 = format_menu_col("F", "Batch Git Fetch", w2, Theme.CYAN, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{c1}{Theme.BORDER}│{Theme.RESET}{c2}{Theme.BORDER}│{Theme.RESET}")

        c3 = format_menu_col("G", "Batch Git GC", w1, Theme.PEACH, Theme.WHITE)
        c4 = format_menu_col("C", "Ganti Direktori", w2, Theme.BLUE, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{c3}{Theme.BORDER}│{Theme.RESET}{c4}{Theme.BORDER}│{Theme.RESET}")

        c5 = format_menu_col("R", "Refresh / Scan", w1, Theme.YELLOW, Theme.WHITE)
        c0 = format_menu_col("0", "Kembali ke Menu Utama", w2, Theme.RED, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{c5}{Theme.BORDER}│{Theme.RESET}{c0}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}╰{'─'*w1}┴{'─'*w2}╯{Theme.RESET}")

        try:
            cmd = input(f"\n {Theme.BOLD}{Theme.PEACH}◆ guava{Theme.RESET} › {Theme.CYAN}git-manager{Theme.RESET} ❯ ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if cmd == "0":
            break
        elif cmd.upper() == "P":
            if repo_data:
                batch_git_pull(repo_data)
                input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali...{Theme.RESET}")
        elif cmd.upper() == "F":
            if repo_data:
                batch_git_fetch(repo_data)
                input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali...{Theme.RESET}")
        elif cmd.upper() == "G":
            if repo_data:
                batch_git_gc(repo_data)
                input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali...{Theme.RESET}")
        elif cmd.upper() == "R":
            continue
        elif cmd.upper() == "C":
            clear_screen()
            print_status_card("📁 GANTI DIREKTORI PEMINDAIAN", [
                ("Saat ini", current_search_dir, Theme.CYAN),
                ("Panduan", "Masukkan path direktori baru (contoh: ~/Projects)", Theme.PEACH),
            ])
            new_dir = input(f" {Theme.BOLD}Path direktori: {Theme.RESET}").strip()
            if new_dir:
                new_dir = os.path.expanduser(new_dir)
                if os.path.isdir(new_dir):
                    current_search_dir = new_dir
                else:
                    print(f"\n {Theme.RED}[!] Direktori tidak ditemukan.{Theme.RESET}")
                    time.sleep(1.2)
        elif cmd.isdigit():
            val = int(cmd)
            if 1 <= val <= len(repo_data):
                manage_single_repo(repo_data[val - 1])
            else:
                print(f"\n {Theme.RED}[!] Nomor di luar jangkauan.{Theme.RESET}")
                time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n{Theme.PEACH}[*] Program dihentikan.{Theme.RESET}")
        sys.exit(0)

