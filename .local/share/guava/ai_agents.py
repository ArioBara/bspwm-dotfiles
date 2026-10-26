#!/usr/bin/env python3
"""
Script Instalasi AI Agent CLI untuk Linux (Mint / Ubuntu / Debian).
Menggunakan skrip instalasi resmi standalone (curl/bash) langsung dari vendor resmi
sehingga tidak memerlukan dependensi runtime berat seperti Node.js global atau Python Pipx.
"""

import os
import shutil
import subprocess
import sys
import time

# Definisi Tema Catppuccin Mocha & ANSI Styling (Ricing Style)
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

def print_banner():
    """Banner minimal ricing untuk kompatibilitas."""
    print(make_box_top("🤖 AI AGENTS & CODING SUITE", badge="v2.5"))
    raw_sub = "  Claude Code, OpenCode, Aider, Open Interpreter, Ollama & Dev Tools"
    pad_sub = " " * max(0, 78 - get_display_width(raw_sub))
    print(f"{Theme.BORDER}│{Theme.RESET}{Theme.GRAY}{raw_sub}{Theme.RESET}{pad_sub}{Theme.BORDER}│{Theme.RESET}")

def is_root():
    """Mengecek apakah script dijalankan sebagai root/superuser."""
    return os.geteuid() == 0 if hasattr(os, "geteuid") else False

def get_sudo_prefix():
    """Mengembalikan prefix sudo jika bukan user root."""
    if is_root():
        return ""
    return "sudo "

def run_cmd(command, check=True, shell=True):
    """Menjalankan perintah terminal dengan penanganan error yang rapi."""
    try:
        return subprocess.run(command, shell=shell, check=check)
    except subprocess.CalledProcessError:
        print(f"\n{Colors.RED}[!] Perintah gagal dieksekusi: {command}{Colors.RESET}")
        return None

def check_linux_mint_env():
    """Memeriksa apakah sistem berbasis Linux (Mint / Ubuntu / Debian)."""
    if not sys.platform.startswith("linux"):
        print(f"{Colors.YELLOW}[!] Peringatan: Sistem terdeteksi bukan Linux ({sys.platform}).")
        print(f"    Script ini dirancang khusus untuk Linux / Ubuntu / Mint / Debian.{Colors.RESET}")
        confirm = input("Apakah Anda ingin tetap melanjutkan? (y/n): ").strip().lower()
        if confirm != "y":
            print("[*] Dibatalkan oleh pengguna.")
            sys.exit(0)
        return

    # Valid Linux environment check passes silently
    return

def configure_user_paths():
    """
    Memastikan direktori binary pengguna (~/.local/bin, ~/.opencode/bin)
    tersedia dan didaftarkan ke dalam PATH untuk semua shell: Fish, Bash, dan Zsh.
    """
    home = os.path.expanduser("~")
    local_bin = os.path.join(home, ".local", "bin")
    opencode_bin = os.path.join(home, ".opencode", "bin")

    os.makedirs(local_bin, exist_ok=True)

    # 1. Konfigurasi Bash (~/.bashrc)
    bashrc_path = os.path.join(home, ".bashrc")
    path_export = 'export PATH="$HOME/.local/bin:$HOME/.opencode/bin:$PATH"\n'
    if os.path.exists(bashrc_path):
        with open(bashrc_path, "r", encoding="utf-8") as f:
            content = f.read()
        if ".local/bin" not in content:
            with open(bashrc_path, "a", encoding="utf-8") as f:
                f.write(f"\n# AI Agents CLI PATH\n{path_export}")
            print(f"{Colors.CYAN}[*] PATH (~/.local/bin) ditambahkan ke ~/.bashrc.{Colors.RESET}")

    # 2. Konfigurasi Zsh (~/.zshrc)
    zshrc_path = os.path.join(home, ".zshrc")
    if os.path.exists(zshrc_path):
        with open(zshrc_path, "r", encoding="utf-8") as f:
            zcontent = f.read()
        if ".local/bin" not in zcontent:
            with open(zshrc_path, "a", encoding="utf-8") as f:
                f.write(f"\n# AI Agents CLI PATH\n{path_export}")
            print(f"{Colors.CYAN}[*] PATH (~/.local/bin) ditambahkan ke ~/.zshrc.{Colors.RESET}")

    # 3. Konfigurasi Fish Shell (~/.config/fish/config.fish & ~/.config/fish/conf.d/)
    fish_dir = os.path.join(home, ".config", "fish")
    fish_conf_d = os.path.join(fish_dir, "conf.d")
    fish_config = os.path.join(fish_dir, "config.fish")

    if shutil.which("fish") or os.path.exists(fish_dir):
        os.makedirs(fish_conf_d, exist_ok=True)
        fish_env_file = os.path.join(fish_conf_d, "ai_agents_path.fish")
        fish_code = (
            "# AI Agents CLI PATH - Auto Generated\n"
            'for p in "$HOME/.local/bin" "$HOME/.opencode/bin"\n'
            '    if test -d "$p"; and not contains "$p" $PATH\n'
            '        set -gx PATH "$p" $PATH\n'
            '    end\n'
            'end\n'
        )
        if not os.path.exists(fish_env_file):
            with open(fish_env_file, "w", encoding="utf-8") as f:
                f.write(fish_code)
            print(f"{Colors.CYAN}[*] PATH (~/.local/bin) dikonfigurasi untuk Fish Shell ({fish_env_file}).{Colors.RESET}")

        if os.path.exists(fish_config):
            with open(fish_config, "r", encoding="utf-8") as f:
                fish_content = f.read()
            if ".local/bin" not in fish_content and not os.path.exists(fish_env_file):
                with open(fish_config, "a", encoding="utf-8") as f:
                    f.write(f"\n# AI Agents CLI PATH\nfish_add_path $HOME/.local/bin\n")
                print(f"{Colors.CYAN}[*] PATH (~/.local/bin) ditambahkan ke ~/.config/fish/config.fish.{Colors.RESET}")

    # 4. Tambahkan ke os.environ subproses saat ini
    current_path = os.environ.get("PATH", "")
    for b in [opencode_bin, local_bin]:
        if b not in current_path:
            current_path = f"{b}:{current_path}"
    os.environ["PATH"] = current_path

def check_and_install_dependencies():
    """
    Memeriksa dan memasang dependensi esensial untuk installer curl
    (curl, wget, git, ca-certificates, tar, gzip, zstd, jq).
    Paket berat seperti nodejs/npm/pipx tidak lagi dibutuhkan.
    """
    print(f"\n{Colors.BOLD}=== [1/2] Memeriksa & Menyiapkan Utilitas Esensial (APT) ==={Colors.RESET}")
    sudo = get_sudo_prefix()

    # Periksa APT
    if not shutil.which("apt"):
        print(f"{Colors.RED}[!] Package manager 'apt' tidak ditemukan! Pastikan Anda menggunakan distro berbasis Debian/Ubuntu/Mint.{Colors.RESET}")
        return False

    print(f"{Colors.CYAN}[*] Memperbarui indeks paket APT...{Colors.RESET}")
    run_cmd(f"{sudo}apt update -y")

    # Paket esensial untuk mengunduh, mengekstrak, dan memverifikasi binary installer
    packages = [
        "curl",
        "wget",
        "git",
        "ca-certificates",
        "tar",
        "gzip",
        "zstd",
        "jq"
    ]
    pkg_str = " ".join(packages)
    print(f"{Colors.CYAN}[*] Memasang paket utilitas: {pkg_str}...{Colors.RESET}")
    run_cmd(f"{sudo}apt install -y {pkg_str}")

    # Konfigurasi direktori PATH pengguna
    configure_user_paths()

    print(f"{Colors.GREEN}[✓] Utilitas esensial siap!{Colors.RESET}")
    return True

def get_agent_list():
    """
    Daftar lengkap AI Agent CLI resmi beserta metode instalasi standalone (curl).
    """
    return {
        "1": {
            "name": "Claude Code CLI (@anthropic-ai/claude-code)",
            "desc": "Official AI Coding Agent CLI dari Anthropic (Sonnet 3.7 / Opus)",
            "cmd": "curl -fsSL https://claude.ai/install.sh | bash",
            "cmd_check": ["claude"]
        },
        "2": {
            "name": "OpenCode CLI (opencode-ai)",
            "desc": "Terminal AI Coding Agent berbasis TUI (multi-model & provider agnostic)",
            "cmd": "curl -fsSL https://opencode.ai/install | bash",
            "cmd_check": ["opencode"]
        },
        "3": {
            "name": "Open Interpreter (open-interpreter)",
            "desc": "Agen bahasa alami berbasis terminal untuk eksekusi kode & OS control",
            "cmd": "curl -fsSL https://www.openinterpreter.com/install | sh",
            "cmd_check": ["interpreter", "i"]
        },
        "4": {
            "name": "Aider AI Pair Programmer (aider-chat)",
            "desc": "CLI AI Pair Programming di Git repository (GPT-4o, Claude, DeepSeek)",
            "cmd": "curl -LsSf https://aider.chat/install.sh | sh",
            "cmd_check": ["aider"]
        },
        "5": {
            "name": "Antigravity CLI (google-antigravity)",
            "desc": "Tool dan CLI Agent resmi ekosistem Google Antigravity (agy)",
            "cmd": "curl -fsSL https://antigravity.google/cli/install.sh | bash",
            "cmd_check": ["agy", "antigravity"]
        },
        "6": {
            "name": "OpenAI Codex CLI (openai-codex)",
            "desc": "CLI resmi OpenAI untuk coding agent dan integrasi model Codex",
            "cmd": "curl -fsSL https://chatgpt.com/codex/install.sh | sh",
            "cmd_check": ["codex", "openai"]
        },
        "7": {
            "name": "Goose CLI (block/goose)",
            "desc": "Autonomous AI developer agent open-source dari Block (Square)",
            "cmd": "curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash",
            "cmd_check": ["goose"]
        },
        "8": {
            "name": "Ollama (Local LLM Engine & CLI)",
            "desc": "Mesin runtime & CLI untuk menjalankan model lokal (Llama 3, DeepSeek, Qwen)",
            "cmd": "curl -fsSL https://ollama.com/install.sh | sh",
            "cmd_check": ["ollama"]
        }
    }

def execute_agent_install(agent):
    """Mengeksekusi instalasi agen menggunakan curl script resmi."""
    clear_screen()
    print_status_card("📦 INSTALASI AI AGENT", [
        ("Agent", agent["name"], Theme.CYAN),
        ("Perintah", agent["cmd"], Theme.PEACH),
    ])

    configure_user_paths()
    res = run_cmd(agent["cmd"])
    success = res is not None and res.returncode == 0

    if success:
        print_status_card("✨ STATUS INSTALASI", [
            ("Status", "BERHASIL DIINSTAL", Theme.MINT),
            ("Agent", agent["name"], Theme.WHITE),
        ])
    else:
        print_status_card("❌ STATUS INSTALASI", [
            ("Status", "GAGAL DIEKSEKUSI", Theme.RED),
            ("Agent", agent["name"], Theme.WHITE),
        ])
    return success

def resolve_command_path(cmd_candidates):
    """Mencari lokasi binary dari daftar kandidat nama perintah."""
    if isinstance(cmd_candidates, str):
        cmd_candidates = [cmd_candidates]

    for cmd in cmd_candidates:
        path = shutil.which(cmd)
        if path:
            return cmd, path

        # Cek manual di ~/.local/bin jika PATH belum termuat di subproses
        home_bin = os.path.expanduser(f"~/.local/bin/{cmd}")
        if os.path.isfile(home_bin) and os.access(home_bin, os.X_OK):
            return cmd, home_bin

    return None, None

def check_installed_agents():
    """Mengecek status ketersediaan dan versi dari masing-masing AI Agent."""
    clear_screen()
    agents = get_agent_list()
    items = []
    for _, item in sorted(agents.items(), key=lambda x: int(x[0])):
        cmd_found, path = resolve_command_path(item.get("cmd_check", []))
        short_name = item['name'].split()[0]
        if path:
            version_str = "Terpasang"
            try:
                out = subprocess.check_output(f"{path} --version 2>/dev/null || {path} -v 2>/dev/null", shell=True, text=True).strip()
                if out:
                    version_str = out.splitlines()[0].strip()
            except Exception:
                pass
            items.append((short_name, f"● {version_str}", Theme.MINT))
        else:
            items.append((short_name, "○ Belum Terpasang", Theme.GRAY))
    print_status_card("🔍 STATUS AI AGENT TERPASANG", items)

def show_menu():
    """Menampilkan antarmuka menu utama interaktif 2-kolom rounded card."""
    agents = get_agent_list()
    agent_short_names = {
        "1": "Claude Code CLI",
        "2": "OpenCode CLI",
        "3": "Open Interpreter",
        "4": "Aider Pair Dev",
        "5": "Antigravity CLI",
        "6": "OpenAI Codex CLI",
        "7": "Goose AI Agent",
        "8": "Ollama Local LLM",
    }

    w1 = 37
    w2 = 40

    while True:
        clear_screen()
        top_box = make_box_top("🤖 AI AGENTS & CODING SUITE", badge="v2.5", total_w=80)
        print(top_box)

        # Cek status terpasang untuk 8 agent
        status_map = {}
        for k, v in agents.items():
            _, path = resolve_command_path(v.get("cmd_check", []))
            status_map[k] = (path is not None)

        left_keys = ["1", "2", "3", "4"]
        right_keys = ["5", "6", "7", "8"]

        for lk, rk in zip(left_keys, right_keys):
            c1 = format_app_col(lk, agent_short_names[lk], status_map[lk], w1)
            c2 = format_app_col(rk, agent_short_names[rk], status_map[rk], w2)
            print(f"{Theme.BORDER}│{Theme.RESET}{c1}{Theme.BORDER}│{Theme.RESET}{c2}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}├{'─'*w1}┼{'─'*w2}┤{Theme.RESET}")

        # Controls in 2 columns
        ctrl_l1 = format_menu_col("A", "Install Semua Agent", w1, Theme.PEACH, Theme.WHITE)
        ctrl_r1 = format_menu_col("S", "Periksa Status & Versi", w2, Theme.CYAN, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{ctrl_l1}{Theme.BORDER}│{Theme.RESET}{ctrl_r1}{Theme.BORDER}│{Theme.RESET}")

        ctrl_l2 = format_menu_col("P", "Konfigurasi Shell PATH", w1, Theme.BLUE, Theme.WHITE)
        ctrl_r2 = format_menu_col("D", "Setup Utilitas Esensial", w2, Theme.MINT, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{ctrl_l2}{Theme.BORDER}│{Theme.RESET}{ctrl_r2}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}├{'─'*w1}┴{'─'*w2}┤{Theme.RESET}")
        exit_str = format_menu_col("0", "Kembali ke Menu Utama", 78, Theme.RED, Theme.WHITE)
        print(f"{Theme.BORDER}│{Theme.RESET}{exit_str}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}╰{'─'*78}╯{Theme.RESET}")

        try:
            choice = input(f"\n {Theme.BOLD}{Theme.PEACH}◆ guava{Theme.RESET} › {Theme.CYAN}ai-agents{Theme.RESET} ❯ ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if choice == "0":
            break
        elif choice in agents:
            selected = agents[choice]
            execute_agent_install(selected)
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice.upper() == "A":
            clear_screen()
            for k in sorted(agents.keys(), key=lambda x: int(x)):
                execute_agent_install(agents[k])
            print_status_card("✨ STATUS BATCH", [
                ("Status", "SEMUA PROSES SELESAI", Theme.MINT),
            ])
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice.upper() == "S":
            check_installed_agents()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice.upper() == "P":
            clear_screen()
            print_status_card("🔧 KONFIGURASI PATH", [
                ("Action", "Menyesuaikan PATH Shell (Fish, Bash, Zsh)...", Theme.CYAN),
            ])
            configure_user_paths()
            print_status_card("✨ KONFIGURASI SELESAI", [
                ("Status", "PATH Berhasil Dikonfigurasi", Theme.MINT),
            ])
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")
        elif choice.upper() == "D":
            clear_screen()
            check_and_install_dependencies()
            input(f"\n{Theme.GRAY} Tekan ENTER untuk kembali ke menu...{Theme.RESET}")

def main():
    """Fungsi utama program."""
    check_linux_mint_env()
    show_menu()

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n{Theme.PEACH}[*] Program dihentikan.{Theme.RESET}")
        sys.exit(0)

