#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gitman: Git Project & Repository Dashboard TUI
Author: ArioDev7
Theme: Catppuccin Mocha
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

# Catppuccin Mocha ANSI Escape Colors
MAUVE = "\033[38;2;203;166;247m"
PINK = "\033[38;2;245;194;231m"
BLUE = "\033[38;2;137;180;250m"
TEAL = "\033[38;2;148;226;213m"
GREEN = "\033[38;2;166;227;161m"
PEACH = "\033[38;2;250;179;135m"
YELLOW = "\033[38;2;249;226;175m"
RED = "\033[38;2;243;139;168m"
LAVENDER = "\033[38;2;180;190;254m"
TEXT = "\033[38;2;205;214;244m"
SUBTEXT = "\033[38;2;166;173;200m"
OVERLAY = "\033[38;2;108;112;134m"
SURFACE = "\033[38;2;49;50;68m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

CACHE_DIR = Path.home() / ".cache" / "gitman"
CACHE_FILE = CACHE_DIR / "repos.json"

BANNER = rf"""{MAUVE}{BOLD}
   ____ ___ _____ __  __    _    _   _ 
  / ___|_ _|_   _|  \/  |  / \  | \ | |
 | |  _ | |  | | | |\/| | / _ \ |  \| |
 | |_| || |  | | | |  | |/ ___ \| |\  |
  \____|___| |_| |_|  |_/_/   \_\_| \_|
{RESET}{TEAL}  󰊢  Git Project & Repository Dashboard • Catppuccin Edition{RESET}
"""

IGNORE_DIRS = {
    ".cache", ".cargo", ".bun", ".npm", ".nvm", ".deno", ".rustup",
    ".vscode", ".vscode-shared", "node_modules", ".git", "venv", ".venv",
    ".gemini", ".local", ".claude", ".codex", ".opencode", ".themes", ".icons"
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

def run_cmd(cmd, cwd=None):
    try:
        res = subprocess.run(
            cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, shell=isinstance(cmd, str)
        )
        return res.returncode == 0, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def find_git_repos():
    repos = []
    search_roots = [
        Path.home() / "Scripts",
        Path.home() / "Documents",
        Path.home() / "Desktop",
        Path.home() / "bspwm-catppuccin-rice",
        Path.home() / "docker-monitoring",
        Path.home(),
    ]
    # Check external drives if they have project folders
    for ext in ["/media/ario/Data", "/media/ario/SSD KYO"]:
        if os.path.exists(ext):
            for sub in ["Projects", "Code", "Repos", "Repositories", "Workspace"]:
                sp = Path(ext) / sub
                if sp.exists():
                    search_roots.append(sp)

    for root in search_roots:
        if not root.exists():
            continue
        try:
            cmd = ["find", str(root), "-maxdepth", "3", "-name", ".git", "-type", "d"]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=2)
            for line in res.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                if not any(x in line for x in [".cache", ".cargo", ".local", ".npm", ".nvm", ".bun", "node_modules"]):
                    repo_dir = str(Path(line).parent.resolve())
                    repos.append(repo_dir)
        except Exception:
            pass

    repos = sorted(list(set(repos)))
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(repos, f, indent=2)
    return repos

def load_cached_repos():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r") as f:
                data = json.load(f)
                return [r for r in data if Path(r).exists() and (Path(r) / ".git").is_dir()]
        except Exception:
            pass
    return find_git_repos()

def get_repo_status(repo_path):
    ok, branch, _ = run_cmd("git branch --show-current", cwd=repo_path)
    if not branch:
        branch = "HEAD (detached)"

    ok, status_out, _ = run_cmd("git status --porcelain", cwd=repo_path)
    dirty_count = len(status_out.splitlines()) if status_out else 0

    ok, ahead_behind, _ = run_cmd("git rev-list --left-right --count origin/HEAD...HEAD", cwd=repo_path)
    if not ok:
        ok, ahead_behind, _ = run_cmd(f"git rev-list --left-right --count origin/{branch}...{branch}", cwd=repo_path)
    
    ahead, behind = 0, 0
    if ok and ahead_behind:
        parts = ahead_behind.split()
        if len(parts) == 2:
            try:
                behind = int(parts[0])
                ahead = int(parts[1])
            except ValueError:
                pass

    return {
        "path": repo_path,
        "name": Path(repo_path).name,
        "branch": branch,
        "dirty": dirty_count,
        "ahead": ahead,
        "behind": behind
    }

def print_table(repo_data):
    col_w = [4, 22, 13, 14, 13]
    top = OVERLAY + "┌" + "┬".join("─" * (w + 2) for w in col_w) + "┐" + RESET
    mid = OVERLAY + "├" + "┼".join("─" * (w + 2) for w in col_w) + "┤" + RESET
    bot = OVERLAY + "└" + "┴".join("─" * (w + 2) for w in col_w) + "┘" + RESET

    print(top)
    header = OVERLAY + "│ " + (OVERLAY + " │ ").join([
        cell("No", col_w[0], color=PEACH + BOLD),
        cell("Nama Repository", col_w[1], color=BLUE + BOLD),
        cell("Branch", col_w[2], color=LAVENDER + BOLD),
        cell("Status Kerja", col_w[3], color=YELLOW + BOLD),
        cell("Sync Remote", col_w[4], color=TEAL + BOLD)
    ]) + OVERLAY + " │" + RESET
    print(header)
    print(mid)

    for idx, r in enumerate(repo_data, start=1):
        num_str = f"[{idx}]"
        name_str = r['name']
        branch_str = r['branch']

        if r['dirty'] == 0:
            st_text = "✓ Bersih"
            st_color = GREEN
        else:
            st_text = f"● {r['dirty']} Berubah"
            st_color = RED

        sync_parts = []
        if r['ahead'] > 0:
            sync_parts.append(f"↑{r['ahead']}")
        if r['behind'] > 0:
            sync_parts.append(f"↓{r['behind']}")
        if not sync_parts:
            sync_text = "≡ Terkini"
            sync_color = GREEN
        else:
            sync_text = " ".join(sync_parts)
            sync_color = YELLOW

        row = OVERLAY + "│ " + (OVERLAY + " │ ").join([
            cell(num_str, col_w[0], color=PINK),
            cell(name_str, col_w[1], color=TEXT),
            cell(branch_str, col_w[2], color=LAVENDER),
            cell(st_text, col_w[3], color=st_color),
            cell(sync_text, col_w[4], color=sync_color)
        ]) + OVERLAY + " │" + RESET
        print(row)

    print(bot)

def manage_repo(repo_info):
    repo_path = repo_info["path"]
    while True:
        clear()
        print(BANNER)
        print(f"{TEAL}📁 Repository Terpilih: {BOLD}{TEXT}{repo_info['name']}{RESET}")
        print(f"{OVERLAY}📍 Path: {SUBTEXT}{repo_path}{RESET}")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}\n")

        print(f"  {PEACH}[1]{RESET}  📋 Status Lengkap (git status)")
        print(f"  {PEACH}[2]{RESET}  🔄 Pull Perubahan Terbaru (git pull)")
        print(f"  {PEACH}[3]{RESET}  📦 Commit & Push Wizard (Add all, Commit pesan, Push)")
        print(f"  {PEACH}[4]{RESET}  🚀 Quick Push (git push)")
        print(f"  {PEACH}[5]{RESET}  📜 Riwayat Commit Graph (10 commit terakhir)")
        print(f"  {PEACH}[6]{RESET}  🌿 Ganti / Buat Branch Baru")
        print(f"  {PEACH}[7]{RESET}  📥 Simpan Sementara (Git Stash / Pop)")
        print(f"  {PEACH}[8]{RESET}  💻 Buka Neovim di Folder Ini")
        print(f"  {PEACH}[9]{RESET}  📂 Buka File Manager (Nemo)")
        print(f"  {PEACH}[10]{RESET} 🐚 Buka Terminal Baru di Folder Ini")
        print(f"\n  {RED}[0]{RESET}  ⬅️  Kembali ke Daftar Repository")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}")

        pilihan = input(f"{YELLOW}Pilih aksi [0-10]: {RESET}").strip()

        if pilihan == "0":
            break
        elif pilihan == "1":
            clear()
            print(f"{BLUE}--- GIT STATUS [{repo_info['name']}] ---{RESET}\n")
            subprocess.run(["git", "status"], cwd=repo_path)
            input(f"\n{OVERLAY}[Tekan Enter untuk kembali]{RESET}")
        elif pilihan == "2":
            clear()
            print(f"{BLUE}--- MENJALANKAN GIT PULL ---{RESET}\n")
            subprocess.run(["git", "pull"], cwd=repo_path)
            input(f"\n{OVERLAY}[Tekan Enter untuk kembali]{RESET}")
        elif pilihan == "3":
            clear()
            print(f"{BLUE}--- COMMIT & PUSH WIZARD ---{RESET}\n")
            subprocess.run(["git", "status", "-s"], cwd=repo_path)
            print("")
            msg = input(f"{YELLOW}Ketik pesan commit: {RESET}").strip()
            if msg:
                subprocess.run(["git", "add", "-A"], cwd=repo_path)
                res = subprocess.run(["git", "commit", "-m", msg], cwd=repo_path)
                if res.returncode == 0:
                    do_push = input(f"{GREEN}Commit berhasil! Lanjut push ke remote? (y/n): {RESET}").strip().lower()
                    if do_push == "y":
                        subprocess.run(["git", "push"], cwd=repo_path)
            else:
                print(f"{RED}Commit dibatalkan: pesan commit kosong.{RESET}")
            input(f"\n{OVERLAY}[Tekan Enter untuk kembali]{RESET}")
        elif pilihan == "4":
            clear()
            print(f"{BLUE}--- MENJALANKAN GIT PUSH ---{RESET}\n")
            subprocess.run(["git", "push"], cwd=repo_path)
            input(f"\n{OVERLAY}[Tekan Enter untuk kembali]{RESET}")
        elif pilihan == "5":
            clear()
            print(f"{BLUE}--- RIWAYAT COMMIT GRAPH ---{RESET}\n")
            subprocess.run(["git", "log", "--graph", "--oneline", "--decorate", "--color=always", "-n", "15"], cwd=repo_path)
            input(f"\n{OVERLAY}[Tekan Enter untuk kembali]{RESET}")
        elif pilihan == "6":
            clear()
            print(f"{BLUE}--- CABANG / BRANCH ---{RESET}\n")
            subprocess.run(["git", "branch", "-a"], cwd=repo_path)
            print("")
            sub_opt = input(f"{YELLOW}[1] Checkout ke Branch Lain | [2] Buat Branch Baru: {RESET}").strip()
            if sub_opt == "1":
                target_br = input(f"{YELLOW}Nama branch tujuan: {RESET}").strip()
                if target_br:
                    subprocess.run(["git", "checkout", target_br], cwd=repo_path)
            elif sub_opt == "2":
                new_br = input(f"{YELLOW}Nama branch baru: {RESET}").strip()
                if new_br:
                    subprocess.run(["git", "checkout", "-b", new_br], cwd=repo_path)
            input(f"\n{OVERLAY}[Tekan Enter untuk kembali]{RESET}")
        elif pilihan == "7":
            clear()
            print(f"{BLUE}--- GIT STASH ---{RESET}\n")
            stash_opt = input(f"{YELLOW}[1] Stash Perubahan Saat Ini | [2] Pop Stash Terakhir: {RESET}").strip()
            if stash_opt == "1":
                s_msg = input(f"{YELLOW}Keterangan stash (opsional): {RESET}").strip()
                cmd = ["git", "stash"] + (["push", "-m", s_msg] if s_msg else [])
                subprocess.run(cmd, cwd=repo_path)
            elif stash_opt == "2":
                subprocess.run(["git", "stash", "pop"], cwd=repo_path)
            input(f"\n{OVERLAY}[Tekan Enter untuk kembali]{RESET}")
        elif pilihan == "8":
            subprocess.Popen(["kitty", "-e", "nvim"], cwd=repo_path)
            print(f"{GREEN}Membuka Neovim di {repo_path}...{RESET}")
            time.sleep(1)
        elif pilihan == "9":
            subprocess.Popen(["nemo", repo_path])
            print(f"{GREEN}Membuka Nemo...{RESET}")
            time.sleep(1)
        elif pilihan == "10":
            subprocess.Popen(["kitty"], cwd=repo_path)
            print(f"{GREEN}Membuka terminal Kitty...{RESET}")
            time.sleep(1)

def main():
    repos = load_cached_repos()

    while True:
        clear()
        print(BANNER)
        print(f"  {SUBTEXT}Ditemukan {BOLD}{len(repos)}{RESET}{SUBTEXT} repository Git lokal.{RESET}")
        print(f"  {OVERLAY}Pilih nomor repository untuk mengelola, atau opsi kontrol di bawah.{RESET}\n")

        # Gather fast status
        repo_data = [get_repo_status(r) for r in repos]
        print_table(repo_data)

        print(f"\n  {YELLOW}[R]{RESET} 🔄 Pindai Ulang Seluruh Folder (Rescan Repos)")
        print(f"  {RED}[0]{RESET} 🚪 Keluar")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}")

        pilihan = input(f"{YELLOW}Pilih nomor repo [1-{len(repos)}] atau [R/0]: {RESET}").strip()

        if pilihan == "0" or pilihan.lower() == "q":
            print(f"{GREEN}Sampai jumpa! 󰊢{RESET}")
            break
        elif pilihan.lower() == "r":
            repos = find_git_repos()
        elif pilihan.isdigit():
            idx = int(pilihan) - 1
            if 0 <= idx < len(repo_data):
                manage_repo(repo_data[idx])
                # refresh status after managing
                repo_data = [get_repo_status(r) for r in repos]

if __name__ == "__main__":
    try:
        import time
        main()
    except KeyboardInterrupt:
        print(f"\n{GREEN}Keluar.{RESET}")
