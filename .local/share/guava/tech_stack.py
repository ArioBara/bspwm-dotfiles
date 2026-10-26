#!/usr/bin/env python3
"""
Script Installer Tech Stack & Dev Environment untuk Linux (Mint / Ubuntu / Debian).
Katalog lengkap runtime bahasa pemrograman, database engine resmi (MongoDB, PostgreSQL, MariaDB),
Node.js (v24 LTS, v22 LTS), Docker CE resmi, .NET SDK, Cloud BaaS (Supabase, Firebase, PocketBase),
serta dev tools modern.
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
    """Memformat item aplikasi/tool dengan status bulatan ricing."""
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
    print(make_box_top("⚡ TECH STACK & DEV ENVIRONMENT", badge="v2.5"))
    raw_sub = "  Node.js 24/22, Docker CE, Database, Cloud BaaS & Compiler Suite"
    pad_sub = " " * (78 - get_display_width(raw_sub))
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

def get_ubuntu_codename():
    """Mendapatkan Ubuntu codename dasar (jammy/noble/focal) pada Linux."""
    codename = "jammy"
    if os.path.exists("/etc/os-release"):
        with open("/etc/os-release", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("UBUNTU_CODENAME="):
                    codename = line.strip().split("=")[1].strip('"')
                    return codename
                elif line.startswith("VERSION_CODENAME="):
                    codename = line.strip().split("=")[1].strip('"')
    return codename

def check_linux_env():
    """Memeriksa apakah sistem berjalan di Linux dengan package manager APT."""
    if not sys.platform.startswith("linux"):
        print(f"{Colors.YELLOW}[!] Peringatan: Sistem terdeteksi bukan Linux ({sys.platform}).")
        print(f"    Script ini dirancang khusus untuk Linux / Debian / Ubuntu / Mint.{Colors.RESET}")
        confirm = input("Apakah Anda ingin tetap melanjutkan? (y/n): ").strip().lower()
        if confirm != "y":
            print("[*] Dibatalkan oleh pengguna.")
            sys.exit(0)
        return

    if not shutil.which("apt"):
        print(f"{Colors.RED}[!] Package manager 'apt' tidak ditemukan! Pastikan Anda berada di distro berbasis Debian/Ubuntu/Mint.{Colors.RESET}")
        sys.exit(1)
    check_and_repair_apt_sources()

def check_and_repair_apt_sources():
    """Memperbaiki list repositori corrupt di /etc/apt/sources.list.d/ jika terdeteksi."""
    legacy_docker = "/etc/apt/sources.list.d/docker.list"
    if os.path.exists(legacy_docker):
        try:
            with open(legacy_docker, "r") as f:
                content = f.read()
            if "$(dpkg" in content or "LINUX UBUNTU BASED" in content:
                sudo = get_sudo_prefix()
                run_cmd(f"{sudo}rm -f '{legacy_docker}'", check=False)
        except Exception:
            pass

def configure_shell_paths():
    """
    Memastikan direktori runtime developer (Bun, Cargo, Deno, .NET, Flutter, Go, pnpm)
    tersedia dan didaftarkan ke dalam PATH untuk semua shell: Fish, Bash, dan Zsh.
    """
    home = os.path.expanduser("~")
    dirs_to_add = [
        os.path.join(home, ".local", "bin"),
        os.path.join(home, ".cargo", "bin"),
        os.path.join(home, ".bun", "bin"),
        os.path.join(home, ".deno", "bin"),
        os.path.join(home, ".dotnet"),
        os.path.join(home, ".dotnet", "tools"),
        os.path.join(home, ".flutter", "bin"),
        os.path.join(home, "go", "bin"),
        os.path.join(home, ".local", "share", "pnpm"),
    ]

    for d in dirs_to_add:
        os.makedirs(d, exist_ok=True)

    # 1. Fish Shell (~/.config/fish/conf.d/tech_stack_paths.fish & config.fish)
    fish_dir = os.path.join(home, ".config", "fish")
    fish_conf_d = os.path.join(fish_dir, "conf.d")
    fish_config = os.path.join(fish_dir, "config.fish")

    if shutil.which("fish") or os.path.exists(fish_dir):
        os.makedirs(fish_conf_d, exist_ok=True)
        fish_env_file = os.path.join(fish_conf_d, "tech_stack_paths.fish")
        fish_lines = [
            "# Tech Stack & Dev Environment PATHs - Auto Generated",
            "set -gx BUN_INSTALL \"$HOME/.bun\"",
            "set -gx DENO_INSTALL \"$HOME/.deno\"",
            "set -gx PNPM_HOME \"$HOME/.local/share/pnpm\"",
            "set -gx DOTNET_ROOT \"$HOME/.dotnet\"",
            "",
            "for p in \"$HOME/.local/bin\" \"$HOME/.cargo/bin\" \"$HOME/.bun/bin\" \"$HOME/.deno/bin\" \"$HOME/.dotnet\" \"$HOME/.dotnet/tools\" \"$HOME/.flutter/bin\" \"$HOME/go/bin\" \"$HOME/.local/share/pnpm\"",
            "    if test -d \"$p\"; and not contains \"$p\" $PATH",
            "        set -gx PATH \"$p\" $PATH",
            "    end",
            "end",
            ""
        ]
        with open(fish_env_file, "w", encoding="utf-8") as f:
            f.write("\n".join(fish_lines))
        print(f"{Colors.CYAN}[*] PATH Developer Tools dikonfigurasi untuk Fish Shell ({fish_env_file}).{Colors.RESET}")

        # Dukungan NVM di Fish Shell
        nvm_dir = os.path.join(home, ".nvm")
        if os.path.isdir(nvm_dir):
            fish_functions_dir = os.path.join(fish_dir, "functions")
            os.makedirs(fish_functions_dir, exist_ok=True)
            nvm_fish_file = os.path.join(fish_functions_dir, "nvm.fish")
            if not os.path.exists(nvm_fish_file):
                fish_nvm_wrapper = (
                    "function nvm --description 'NVM wrapper for Fish shell'\n"
                    '    set -l nvm_cmd (string escape -- $argv)\n'
                    '    bash -c "source ~/.nvm/nvm.sh && nvm $nvm_cmd"\n'
                    "end\n"
                )
                with open(nvm_fish_file, "w", encoding="utf-8") as f:
                    f.write(fish_nvm_wrapper)
                print(f"{Colors.CYAN}[*] Dukungan NVM ditambahkan ke Fish Shell ({nvm_fish_file}).{Colors.RESET}")

    # 2. Bash (~/.bashrc)
    bashrc_path = os.path.join(home, ".bashrc")
    bash_export = (
        '\n# Tech Stack & Dev Environment PATHs\n'
        'export BUN_INSTALL="$HOME/.bun"\n'
        'export DENO_INSTALL="$HOME/.deno"\n'
        'export PNPM_HOME="$HOME/.local/share/pnpm"\n'
        'export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$BUN_INSTALL/bin:$DENO_INSTALL/bin:$HOME/.dotnet:$HOME/.dotnet/tools:$HOME/.flutter/bin:$HOME/go/bin:$PNPM_HOME:$PATH"\n'
    )
    if os.path.exists(bashrc_path):
        with open(bashrc_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "BUN_INSTALL" not in content and ".cargo/bin" not in content:
            with open(bashrc_path, "a", encoding="utf-8") as f:
                f.write(bash_export)
            print(f"{Colors.CYAN}[*] PATH Developer Tools ditambahkan ke ~/.bashrc.{Colors.RESET}")

    # 3. Zsh (~/.zshrc)
    zshrc_path = os.path.join(home, ".zshrc")
    if os.path.exists(zshrc_path):
        with open(zshrc_path, "r", encoding="utf-8") as f:
            zcontent = f.read()
        if "BUN_INSTALL" not in zcontent and ".cargo/bin" not in zcontent:
            with open(zshrc_path, "a", encoding="utf-8") as f:
                f.write(bash_export)
            print(f"{Colors.CYAN}[*] PATH Developer Tools ditambahkan ke ~/.zshrc.{Colors.RESET}")

    # 4. Tambahkan ke os.environ saat ini
    cur_path = os.environ.get("PATH", "")
    for d in dirs_to_add:
        if d not in cur_path:
            cur_path = f"{d}:{cur_path}"
    os.environ["PATH"] = cur_path

def is_item_installed(cmd_or_pkg):
    """Mengecek apakah paket atau binary sudah terpasang di sistem."""
    if not cmd_or_pkg:
        return False
    first_cmd = cmd_or_pkg.split()[0]
    if shutil.which(first_cmd):
        return True
    
    # Cek di PATH lokal pengguna (~/.local/bin atau ~/.cargo/bin atau ~/.bun/bin atau ~/.dotnet)
    home = os.path.expanduser("~")
    for extra_dir in [".local/bin", ".cargo/bin", ".bun/bin", ".nvm", ".dotnet"]:
        candidate = os.path.join(home, extra_dir, first_cmd)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return True

    # Cek di nvm versions jika node atau npm
    if first_cmd in ["node", "npm", "npx"]:
        nvm_node = os.path.join(home, ".nvm", "versions", "node")
        if os.path.isdir(nvm_node):
            for v_dir in os.listdir(nvm_node):
                cand = os.path.join(nvm_node, v_dir, "bin", first_cmd)
                if os.path.isfile(cand) and os.access(cand, os.X_OK):
                    return True


    # Cek via dpkg-query jika berupa paket APT
    try:
        res = subprocess.run(
            f"dpkg -s {first_cmd} 2>/dev/null | grep -q 'Status: install ok installed'",
            shell=True
        )
        return res.returncode == 0
    except Exception:
        return False

def get_tech_categories():
    """Daftar lengkap kategori bahasa pemrograman, database, server, container, dan tooling."""
    codename = get_ubuntu_codename()

    return {
        "1": {
            "name": "JavaScript & TypeScript Runtimes (Node.js, Bun, Deno)",
            "desc": "Node.js 24 LTS, Node.js 22 LTS, Bun, Deno & NVM",
            "items": [
                {
                    "name": "Node.js 24.20.0 LTS (Official Website / NVM)",
                    "desc": "Instalasi Node.js 24 via installer resmi website nodejs.org & NVM v0.40.7",
                    "type": "custom",
                    "installer": "nodejs-24.txt",
                    "cmd_install": 'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.7/install.sh | bash && export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \\. "$NVM_DIR/nvm.sh" && nvm install 24 && nvm alias default 24 && nvm use 24 && mkdir -p "$HOME/.local/bin" && ln -sf "$(which node)" "$HOME/.local/bin/node" && ln -sf "$(which npm)" "$HOME/.local/bin/npm"',
                    "cmd": "node"
                },
                {
                    "name": "Node.js 22.23.2 LTS & NPM (Official Website / NVM)",
                    "desc": "Instalasi Node.js 22 LTS via installer resmi website nodejs.org",
                    "type": "custom",
                    "installer": "nodejs-22.txt",
                    "cmd_install": "curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && sudo apt install -y nodejs",
                    "cmd": "node"
                },
                {
                    "name": "Bun (Ultra-fast JavaScript/TypeScript Runtime & Bundler)",
                    "desc": "Runtime modern berbasis JavaScriptCore & Zig yang sangat kencang",
                    "type": "custom",
                    "cmd_install": "curl -fsSL https://bun.sh/install | bash",
                    "cmd": "bun"
                },
                {
                    "name": "Deno (Secure JS/TS Runtime modern berbasis Rust & V8)",
                    "desc": "Runtime aman dengan dukungan standar web dan TypeScript out-of-the-box",
                    "type": "custom",
                    "cmd_install": "curl -fsSL https://deno.land/install.sh | sh",
                    "cmd": "deno"
                },
                {
                    "name": "NVM (Node Version Manager)",
                    "desc": "Tool untuk install dan switch berbagai versi Node.js secara instan",
                    "type": "custom",
                    "cmd_install": "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash",
                    "cmd": "nvm"
                },
                {
                    "name": "pnpm & Yarn Package Managers",
                    "desc": "Manajer paket alternatif yang cepat dan efisien",
                    "type": "custom",
                    "cmd_install": "curl -fsSL https://get.pnpm.io/install.sh | sh - && sudo npm install -g yarn 2>/dev/null || npm install -g yarn",
                    "cmd": "pnpm"
                }
            ]
        },
        "2": {
            "name": "Bahasa Pemrograman, Compiler & SDK (Python, Go, Rust, .NET, Java, PHP)",
            "desc": "Python 3, Go, Rustup, .NET SDK, Java OpenJDK, PHP & C/C++",
            "items": [
                {
                    "name": "Python 3 + Pip + Venv + Pipx + uv (Ekosistem Python Lengkap)",
                    "desc": "Python 3 lengkap dengan package manager, venv, pipx dan uv resolver",
                    "type": "custom",
                    "cmd_install": "sudo apt update && sudo apt install -y python3 python3-pip python3-venv python3-dev pipx build-essential && curl -LsSf https://astral.sh/uv/install.sh | sh",
                    "cmd": "python3"
                },
                {
                    "name": ".NET SDK 8.0 LTS (Microsoft .NET SDK)",
                    "desc": "Software Development Kit resmi Microsoft untuk C#, F# & ASP.NET Core",
                    "type": "custom",
                    "cmd_install": "sudo apt update && (sudo apt install -y dotnet-sdk-8.0 || (curl -sSL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 8.0))",
                    "cmd": "dotnet"
                },
                {
                    "name": ".NET SDK 9.0 (Microsoft .NET SDK Terbaru)",
                    "desc": "Software Development Kit resmi Microsoft .NET 9.0",
                    "type": "custom",
                    "cmd_install": "curl -sSL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 9.0",
                    "cmd": "dotnet"
                },
                {
                    "name": "Go / Golang (Backend & Cloud-Native Language)",
                    "desc": "Kompilator Go resmi dari Google untuk performa tinggi & concurrency",
                    "type": "apt",
                    "apt_package": "golang-go",
                    "cmd": "go"
                },
                {
                    "name": "Rust & Cargo (Toolchain Resmi via Rustup)",
                    "desc": "Kompilator Rust, Cargo package manager & Clippy via Rustup",
                    "type": "custom",
                    "cmd_install": "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y",
                    "cmd": "rustc"
                },
                {
                    "name": "C / C++ Toolchain (GCC, G++, Clang, CMake, Make, GDB, Ninja)",
                    "desc": "Build essential dan compiler C/C++ standar industri",
                    "type": "apt",
                    "apt_package": "build-essential gdb clang cmake make ninja-build",
                    "cmd": "gcc"
                },
                {
                    "name": "PHP 8.x + Ekstensi Lengkap (CLI, FPM, MySQL, GD, Zip, cURL)",
                    "desc": "Interpreter PHP untuk backend web & Laravel/WordPress",
                    "type": "apt",
                    "apt_package": "php php-cli php-fpm php-mysql php-xml php-mbstring php-curl php-zip php-gd php-intl php-sqlite3 composer",
                    "cmd": "php"
                },
                {
                    "name": "Java OpenJDK 21 LTS (Java LTS Terbaru untuk Spring Boot 3 & Modern Enterprise)",
                    "desc": "Java Development Kit (JDK 21) & Runtime LTS generasi terbaru",
                    "type": "apt",
                    "apt_package": "openjdk-21-jdk openjdk-21-jre",
                    "cmd": "java"
                },
                {
                    "name": "Java OpenJDK 17 LTS (Java LTS Enterprise Standar)",
                    "desc": "Java Development Kit (JDK 17) & Runtime LTS standar industri",
                    "type": "apt",
                    "apt_package": "openjdk-17-jdk openjdk-17-jre",
                    "cmd": "java"
                },
                {
                    "name": "Ruby & RubyGems (Ruby on Rails Stack)",
                    "desc": "Interpreter Ruby & Ruby Development Packages",
                    "type": "apt",
                    "apt_package": "ruby-full ruby-dev",
                    "cmd": "ruby"
                }
            ]
        },
        "3": {
            "name": "Database Engines & Storage (MongoDB, PostgreSQL, MariaDB, Redis, SurrealDB)",
            "desc": "Server basis data relasional, NoSQL, in-memory & multi-model",
            "items": [
                {
                    "name": "MongoDB 8.0 Community Edition & Mongosh (Official Latest Release)",
                    "desc": "Server NoSQL Document Database resmi MongoDB 8.0 (Latest) & Mongosh Shell",
                    "type": "custom",
                    "installer": "mongodb.txt",
                    "cmd_install": f"sudo apt update && sudo apt install -y gnupg curl && curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg --dearmor --yes && echo 'deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu {codename}/mongodb-org/8.0 multiverse' | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list && sudo apt update && sudo apt install -y mongodb-org mongodb-mongosh",
                    "cmd": "mongod"
                },
                {
                    "name": "MongoDB 7.0 Community Edition & Mongosh (Official Previous LTS)",
                    "desc": "Server NoSQL Document Database resmi MongoDB 7.0 LTS & Mongosh Shell",
                    "type": "custom",
                    "cmd_install": f"sudo apt update && sudo apt install -y gnupg curl && curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor --yes && echo 'deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu {codename}/mongodb-org/7.0 multiverse' | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list && sudo apt update && sudo apt install -y mongodb-org mongodb-mongosh",
                    "cmd": "mongod"
                },
                {
                    "name": "PostgreSQL Server & Client (Enterprise Relational DB)",
                    "desc": "Database open-source paling canggih dengan dukungan ekstensi lengkap",
                    "type": "apt",
                    "apt_package": "postgresql postgresql-contrib postgresql-client",
                    "cmd": "psql"
                },
                {
                    "name": "MariaDB Server & Client (MySQL Drop-in Replacement)",
                    "desc": "Database relasional cepat dan andal untuk web aplikasi",
                    "type": "apt",
                    "apt_package": "mariadb-server mariadb-client",
                    "cmd": "mariadb"
                },
                {
                    "name": "Redis Server & Redis-Tools (In-Memory Data Store & Cache)",
                    "desc": "Database in-memory untuk caching cepat, session storage & queue",
                    "type": "apt",
                    "apt_package": "redis-server redis-tools",
                    "cmd": "redis-server"
                },
                {
                    "name": "SQLite 3 Engine & Dev Libraries",
                    "desc": "Database berkas tanpa server yang ringan dan embedded",
                    "type": "apt",
                    "apt_package": "sqlite3 libsqlite3-dev",
                    "cmd": "sqlite3"
                },
                {
                    "name": "SurrealDB (Modern Multi-model Cloud-Native Database)",
                    "desc": "Database revolusioner yang mendukung relational, document & graph",
                    "type": "custom",
                    "cmd_install": "curl -sSf https://install.surrealdb.com | sh",
                    "cmd": "surreal"
                }
            ]
        },
        "4": {
            "name": "Cloud BaaS, Backend CLI & Serverless (Firebase, Supabase, PocketBase)",
            "desc": "Firebase CLI, Supabase CLI, PocketBase, Vercel, Netlify & Stripe",
            "items": [
                {
                    "name": "Firebase CLI (Official Google Firebase Standalone / NPM)",
                    "desc": "CLI resmi Google Firebase untuk hosting, functions, Firestore rules & emulators",
                    "type": "custom",
                    "cmd_install": "curl -sL https://firebase.tools | bash || sudo npm install -g firebase-tools",
                    "cmd": "firebase"
                },
                {
                    "name": "Supabase CLI (Official Supabase Binary & NPM)",
                    "desc": "CLI resmi Supabase untuk local development, migrations & edge functions",
                    "type": "custom",
                    "cmd_install": "curl -fsSL https://github.com/supabase/cli/releases/latest/download/supabase_linux_amd64.tar.gz | tar -xz && sudo install supabase /usr/local/bin && rm -f supabase || sudo npm install -g supabase",
                    "cmd": "supabase"
                },
                {
                    "name": "PocketBase (Open-Source Backend in 1 File)",
                    "desc": "Backend all-in-one super cepat dengan embedded SQLite, Auth, Realtime DB & Admin UI",
                    "type": "custom",
                    "cmd_install": "PB_URL=$(curl -s https://api.github.com/repos/pocketbase/pocketbase/releases/latest | grep 'browser_download_url.*linux_amd64.zip' | cut -d '\"' -f 4) && curl -fsSL \"$PB_URL\" -o pocketbase.zip && unzip -o pocketbase.zip pocketbase && sudo install pocketbase /usr/local/bin && rm -f pocketbase.zip pocketbase",
                    "cmd": "pocketbase"
                },
                {
                    "name": "Vercel CLI & Netlify CLI",
                    "desc": "CLI deployment cloud platform untuk frontend & serverless functions",
                    "type": "custom",
                    "cmd_install": "sudo npm install -g vercel netlify-cli 2>/dev/null || npm install -g vercel netlify-cli",
                    "cmd": "vercel"
                },
                {
                    "name": "Stripe CLI (Official Payment Testing CLI)",
                    "desc": "CLI resmi Stripe untuk listen webhook dan test pembayaran lokal",
                    "type": "custom",
                    "cmd_install": "curl -s https://packages.stripe.dev/api/security/keypair/stripe-cli-gpg/public | gpg --dearmor | sudo tee /usr/share/keyrings/stripe.gpg > /dev/null && echo 'deb [signed-by=/usr/share/keyrings/stripe.gpg] https://packages.stripe.dev/stripe-cli-debian-local stable main' | sudo tee /etc/apt/sources.list.d/stripe.list && sudo apt update && sudo apt install -y stripe",
                    "cmd": "stripe"
                },
                {
                    "name": "Prisma ORM & Drizzle Kit CLI",
                    "desc": "TypeScript ORM toolkit & migration manager terpopuler",
                    "type": "custom",
                    "cmd_install": "sudo npm install -g prisma drizzle-kit 2>/dev/null || npm install -g prisma drizzle-kit",
                    "cmd": "prisma"
                }
            ]
        },
        "5": {
            "name": "Containerization & Cloud Infrastructure (Docker CE Resmi, Podman, Kube)",
            "desc": "Docker Engine CE Resmi, Docker Compose v2, Podman & Kubectl",
            "items": [
                {
                    "name": "Docker CE Resmi (Docker Engine, CLI, Buildx & Compose v2 dari download.docker.com)",
                    "desc": "Instalasi Docker Community Edition versi website resmi lengkap dengan keyring docker.asc",
                    "type": "custom",
                    "installer": "docker.txt",
                    "cmd_install": f"sudo rm -f /etc/apt/sources.list.d/docker.list && sudo apt update && sudo apt install -y ca-certificates curl gnupg && sudo install -m 0755 -d /etc/apt/keyrings && sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc && sudo chmod a+r /etc/apt/keyrings/docker.asc && sudo tee /etc/apt/sources.list.d/docker.sources << 'EOF_DOCKER'\nTypes: deb\nURIs: https://download.docker.com/linux/ubuntu\nSuites: {codename}\nComponents: stable\nArchitectures: amd64\nSigned-By: /etc/apt/keyrings/docker.asc\nEOF_DOCKER\n && sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin && sudo usermod -aG docker $USER",
                    "cmd": "docker"
                },
                {
                    "name": "Podman & Podman Docker (Rootless Container Platform)",
                    "desc": "Engine container tanpa daemon (daemonless) yang kompatibel dengan Docker",
                    "type": "apt",
                    "apt_package": "podman podman-docker",
                    "cmd": "podman"
                },
                {
                    "name": "Kubectl (Kubernetes Cluster CLI Controller)",
                    "desc": "CLI resmi untuk manajemen dan orkestrasi container Kubernetes",
                    "type": "custom",
                    "cmd_install": "curl -LO 'https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl' && chmod +x kubectl && sudo install kubectl /usr/local/bin/ && rm -f kubectl",
                    "cmd": "kubectl"
                },
                {
                    "name": "Terraform / OpenTofu (Infrastructure as Code)",
                    "desc": "Penyedia otomatisasi infrastruktur cloud (AWS, GCP, DigitalOcean)",
                    "type": "custom",
                    "cmd_install": "curl -fsSL https://get.opentofu.org/install-opentofu.sh -o install-opentofu.sh && chmod +x install-opentofu.sh && ./install-opentofu.sh --install-method deb && rm -f install-opentofu.sh",
                    "cmd": "tofu"
                }
            ]
        },
        "6": {
            "name": "Web Server & Reverse Proxy (Nginx, Apache2, Caddy, LAMP/LEMP)",
            "desc": "Server HTTP/HTTPS, SSL otomatis, load balancer & local server stacks",
            "items": [
                {
                    "name": "Nginx (High Performance Web Server & Reverse Proxy)",
                    "desc": "Server web andal dengan konsumsi memori rendah dan kecepatan tinggi",
                    "type": "apt",
                    "apt_package": "nginx",
                    "cmd": "nginx"
                },
                {
                    "name": "Apache2 HTTP Web Server",
                    "desc": "Web server modular klasik dengan dukungan .htaccess fleksibel",
                    "type": "apt",
                    "apt_package": "apache2 apache2-utils",
                    "cmd": "apache2"
                },
                {
                    "name": "Caddy Server (Modern Web Server dengan Auto-HTTPS SSL)",
                    "desc": "Web server modern yang otomatis mengurus sertifikat SSL/TLS Let's Encrypt",
                    "type": "custom",
                    "cmd_install": "sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg --yes && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list && sudo apt update && sudo apt install -y caddy",
                    "cmd": "caddy"
                },
                {
                    "name": "LAMP Stack Lengkap (Apache2 + MariaDB + PHP + phpMyAdmin)",
                    "desc": "Paket web server lengkap untuk pengembangan aplikasi PHP & MySQL",
                    "type": "apt",
                    "apt_package": "apache2 mariadb-server php libapache2-mod-php php-mysql php-xml php-mbstring php-curl phpmyadmin",
                    "cmd": "apache2"
                },
                {
                    "name": "LEMP Stack Lengkap (Nginx + MariaDB + PHP-FPM)",
                    "desc": "Paket web server Nginx dengan PHP FastCGI Process Manager",
                    "type": "apt",
                    "apt_package": "nginx mariadb-server php-fpm php-mysql php-xml php-mbstring php-curl php-zip",
                    "cmd": "nginx"
                }
            ]
        },
        "7": {
            "name": "Database GUI Clients, API Testers & Git Tools",
            "desc": "DBeaver, SQLite Browser, Postman/Bruno, GitHub CLI, Lazygit",
            "items": [
                {
                    "name": "DBeaver Community Edition (Universal Multi-database GUI)",
                    "desc": "GUI canggih untuk PostgreSQL, MySQL, MariaDB, SQLite, Oracle, MongoDB",
                    "type": "custom",
                    "cmd_install": "wget -O - https://dbeaver.io/debs/dbeaver.gpg.key | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/dbeaver.gpg --yes && echo 'deb https://dbeaver.io/debs/dbeaver-ce /' | sudo tee /etc/apt/sources.list.d/dbeaver.list && sudo apt update && sudo apt install -y dbeaver-ce",
                    "cmd": "dbeaver"
                },
                {
                    "name": "SQLite Browser (DB Browser for SQLite GUI)",
                    "desc": "Antarmuka visual untuk membuat, mendesain, dan mengedit file database SQLite",
                    "type": "apt",
                    "apt_package": "sqlitebrowser",
                    "cmd": "sqlitebrowser"
                },
                {
                    "name": "GitHub CLI (gh) & Lazygit",
                    "desc": "Tool resmi GitHub dan Terminal UI untuk navigasi Git yang sangat produktif",
                    "type": "custom",
                    "cmd_install": "sudo apt update && sudo apt install -y gh git-delta && LAZYGIT_VERSION=$(curl -s 'https://api.github.com/repos/jesseduffield/lazygit/releases/latest' | grep -Po '\"tag_name\": \"v\\K[^\"]*') && curl -Lo lazygit.tar.gz \"https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LAZYGIT_VERSION}_Linux_x86_64.tar.gz\" && tar xf lazygit.tar.gz lazygit && sudo install lazygit /usr/local/bin && rm -f lazygit.tar.gz lazygit",
                    "cmd": "gh"
                },
                {
                    "name": "HTTPie & cURL & Wget & Jq (API Testing Suite)",
                    "desc": "Alat pengujian API terminal dengan formatting warna dan JSON parser",
                    "type": "apt",
                    "apt_package": "httpie curl wget jq",
                    "cmd": "http"
                },
                {
                    "name": "Meld & Gitg (Visual Diff & Git Branch Graph)",
                    "desc": "Alat komparasi kode file/folder visual dan penampil cabang git",
                    "type": "apt",
                    "apt_package": "meld gitg",
                    "cmd": "meld"
                }
            ]
        },
        "8": {
            "name": "Mobile & Cross-Platform App Development (Flutter, Dart, Android SDK, React Native)",
            "desc": "Flutter SDK Stable, Dart SDK, Android Platform Tools (ADB/Fastboot), Expo, React Native CLI, Scrcpy",
            "items": [
                {
                    "name": "Flutter SDK Stable (Google Flutter Framework Resmi)",
                    "desc": "SDK lengkap untuk build aplikasi Android, iOS, Web & Desktop dari 1 codebase",
                    "type": "custom",
                    "cmd_install": "sudo apt update && sudo apt install -y git curl unzip xz-utils zip libglu1-mesa clang cmake ninja-build pkg-config libgtk-3-dev && [ ! -d $HOME/.flutter ] && git clone https://github.com/flutter/flutter.git -b stable $HOME/.flutter; sudo ln -sf $HOME/.flutter/bin/flutter /usr/local/bin/flutter && sudo ln -sf $HOME/.flutter/bin/dart /usr/local/bin/dart && flutter --version",
                    "cmd": "flutter"
                },
                {
                    "name": "Dart SDK Standalone (Google Dart Language SDK)",
                    "desc": "Kompilator dan runtime mandiri bahasa pemrograman Dart",
                    "type": "custom",
                    "cmd_install": "sudo apt update && sudo apt install -y apt-transport-https && wget -qO- https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/dart.gpg --yes && echo 'deb [signed-by=/usr/share/keyrings/dart.gpg arch=amd64] https://storage.googleapis.com/download.dartlang.org/linux/debian stable main' | sudo tee /etc/apt/sources.list.d/dart_stable.list && sudo apt update && sudo apt install -y dart",
                    "cmd": "dart"
                },
                {
                    "name": "Android Platform Tools (ADB, Fastboot & Android Udev Rules)",
                    "desc": "Alat komunikasi debugging USB, flashing & shell perangkat Android",
                    "type": "apt",
                    "apt_package": "adb fastboot android-sdk-platform-tools-common",
                    "cmd": "adb"
                },
                {
                    "name": "React Native CLI & Expo CLI (EAS)",
                    "desc": "Framework mobile apps berbasis JavaScript & React",
                    "type": "custom",
                    "cmd_install": "sudo npm install -g expo-cli eas-cli react-native-cli 2>/dev/null || npm install -g expo-cli eas-cli react-native-cli",
                    "cmd": "expo"
                },
                {
                    "name": "Scrcpy (Display & Control Android Devices over USB/WiFi)",
                    "desc": "Penampil layar dan pengontrol HP Android berkecepatan tinggi & low-latency",
                    "type": "apt",
                    "apt_package": "scrcpy adb",
                    "cmd": "scrcpy"
                }
            ]
        }
    }

def install_item(item):
    """Mengeksekusi instalasi satu item tech stack dengan pembersihan layar ricing."""
    clear_screen()
    sudo = get_sudo_prefix()
    
    print_status_card("📦 PROSES INSTALASI", [
        ("Target", item["name"], Theme.BOLD + Theme.WHITE),
        ("Tipe", item.get("type", "apt").upper(), Theme.CYAN),
        ("Status", "Menyiapkan dependensi & memasang stack...", Theme.PEACH)
    ])

    item_type = item.get("type", "apt")
    success = False

    installer_name = item.get("installer")
    installer_path = None
    if installer_name:
        candidate = os.path.join(os.path.dirname(os.path.abspath(__file__)), "installer", installer_name)
        if os.path.exists(candidate):
            installer_path = candidate
        else:
            candidate_parent = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "installer", installer_name)
            if os.path.exists(candidate_parent):
                installer_path = candidate_parent

    if installer_path:
        res = run_cmd(f"bash '{installer_path}'")
        success = res is not None and res.returncode == 0
    elif item_type == "apt":
        pkgs = item["apt_package"]
        res = run_cmd(f"{sudo}apt update -y && {sudo}apt install -y {pkgs}")
        success = res is not None and res.returncode == 0
    elif item_type == "custom":
        cmd_str = item["cmd_install"]
        res = run_cmd(cmd_str)
        success = res is not None and res.returncode == 0

    print()
    if success:
        configure_shell_paths()
        print_status_card("✨ INSTALASI BERHASIL", [
            ("Target", item["name"], Theme.BOLD + Theme.WHITE),
            ("Status", "● Komponen berhasil terpasang di sistem", Theme.MINT)
        ])
        input(f" {Theme.PEACH}◆ Tekan [ENTER] untuk kembali ke menu...{Theme.RESET}")
    else:
        print_status_card("⚠️ INSTALASI TERKENDALA", [
            ("Target", item["name"], Theme.BOLD + Theme.WHITE),
            ("Status", "● Terjadi kendala saat instalasi (Cek log di atas)", Theme.RED)
        ])
        input(f" {Theme.PEACH}◆ Tekan [ENTER] untuk kembali ke menu...{Theme.RESET}")
    return success

def show_subcategory_menu(cat_key, cat_data):
    """Menampilkan submenu item tech stack dalam format 2 kolom rounded box ricing."""
    items = cat_data["items"]
    w1, w2 = 37, 40
    d1 = "─" * w1
    d2 = "─" * w2
    
    cat_slug = cat_data["name"].split("(")[0].strip().lower().replace(" ", "-")

    while True:
        clear_screen()
        top_title = f"⚡ {cat_data['name'].upper()}"
        if get_display_width(top_title) > 65:
            top_title = top_title[:62] + "..."
        print(make_box_top(top_title, badge=f"Kat {cat_key}"))

        stat_text = f"  Status: {Theme.MINT}● Terpasang{Theme.RESET}   {Theme.GRAY}○ Belum Terpasang{Theme.RESET}"
        raw_stat = "  Status: ● Terpasang   ○ Belum Terpasang"
        pad_stat = " " * max(0, 78 - get_display_width(raw_stat))
        print(f"{Theme.BORDER}│{Theme.RESET}{stat_text}{pad_stat}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}├{d1}┬{d2}┤{Theme.RESET}")

        for i in range(0, len(items), 2):
            idx1 = i + 1
            it1 = items[i]
            short1 = it1["name"].split(" (")[0].strip()
            inst1 = is_item_installed(it1.get("cmd", ""))
            col1 = format_app_col(idx1, short1, inst1, w1)

            if i + 1 < len(items):
                idx2 = i + 2
                it2 = items[i + 1]
                short2 = it2["name"].split(" (")[0].strip()
                inst2 = is_item_installed(it2.get("cmd", ""))
                col2 = format_app_col(idx2, short2, inst2, w2)
            else:
                col2 = " " * w2
            print(f"{Theme.BORDER}│{Theme.RESET}{col1}{Theme.BORDER}│{Theme.RESET}{col2}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}├{d1}┼{d2}┤{Theme.RESET}")
        colA = format_menu_col("A", "Pasang Semua di Kategori", width=w1, num_color=Theme.CYAN)
        col0 = format_menu_col("0", "Kembali ke Menu Utama", width=w2, num_color=Theme.RED)
        print(f"{Theme.BORDER}│{Theme.RESET}{colA}{Theme.BORDER}│{Theme.RESET}{col0}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}╰{d1}┴{d2}╯{Theme.RESET}")

        choice = input(f"\n {Theme.MINT}◆{Theme.RESET} {Theme.CYAN}guava{Theme.RESET} {Theme.GRAY}›{Theme.RESET} {Theme.PEACH}{cat_slug}{Theme.RESET} {Theme.CYAN}❯{Theme.RESET} ").strip()

        if choice == "0":
            break
        elif choice.upper() == "A":
            for it in items:
                install_item(it)
            break
        elif choice.isdigit():
            val = int(choice)
            if 1 <= val <= len(items):
                selected = items[val - 1]
                install_item(selected)
            else:
                print(f" {Theme.RED}[!] Nomor di luar jangkauan (1-{len(items)}).{Theme.RESET}")
                time.sleep(1)
        else:
            print(f" {Theme.RED}[!] Pilihan '{choice}' tidak valid.{Theme.RESET}")
            time.sleep(1)

def install_preset(preset_type):
    """Menginstal paket bundel rekomendasi developer stack siap pakai."""
    clear_screen()
    sudo = get_sudo_prefix()
    codename = get_ubuntu_codename()

    presets = {
        "1": {
            "name": "Full-Stack Web (Node 24 LTS, Bun, pnpm, Python 3, Postgres)",
            "action": lambda: run_cmd(
                "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.7/install.sh | bash && "
                'export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \\. "$NVM_DIR/nvm.sh" && '
                "nvm install 24 && nvm alias default 24 && nvm use 24 && "
                'mkdir -p "$HOME/.local/bin" && ln -sf "$(which node)" "$HOME/.local/bin/node" && ln -sf "$(which npm)" "$HOME/.local/bin/npm" && '
                "sudo apt install -y postgresql postgresql-contrib python3 python3-pip python3-venv git git-delta httpie jq build-essential && "
                "curl -fsSL https://bun.sh/install | bash && "
                "curl -fsSL https://get.pnpm.io/install.sh | sh - && "
                "npm install -g prisma drizzle-kit"
            )
        },
        "2": {
            "name": "Cloud BaaS & Serverless (Firebase, Supabase, PocketBase, Vercel)",
            "action": lambda: run_cmd(
                "curl -sL https://firebase.tools | bash && "
                "curl -fsSL https://github.com/supabase/cli/releases/latest/download/supabase_linux_amd64.tar.gz | tar -xz && sudo install supabase /usr/local/bin && rm -f supabase && "
                "sudo npm install -g vercel netlify-cli 2>/dev/null || npm install -g vercel netlify-cli"
            )
        },
        "3": {
            "name": "Database & NoSQL Suite (MongoDB 8.0 Resmi + Postgres + Redis)",
            "action": lambda: run_cmd(
                "sudo apt update && sudo apt install -y postgresql postgresql-contrib redis-server sqlite3 libsqlite3-dev"
            ) and (
                run_cmd(f"bash '{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'installer', 'mongodb.txt')}'")
                if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "installer", "mongodb.txt"))
                else run_cmd(
                    f"sudo apt update && sudo apt install -y gnupg curl && "
                    f"curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg --dearmor --yes && "
                    f"echo 'deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu {codename}/mongodb-org/8.0 multiverse' | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list && "
                    f"sudo apt update && sudo apt install -y mongodb-org mongodb-mongosh"
                )
            )
        },
        "4": {
            "name": "Docker CE Resmi & Cloud DevOps (Docker CE, Buildx, Compose, Kube)",
            "action": lambda: (
                run_cmd(f"bash '{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'installer', 'docker.txt')}'")
                if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "installer", "docker.txt"))
                else run_cmd(
                    f"sudo rm -f /etc/apt/sources.list.d/docker.list && "
                    f"sudo apt update && sudo apt install -y ca-certificates curl gnupg && "
                    f"sudo install -m 0755 -d /etc/apt/keyrings && "
                    f"curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc && sudo chmod a+r /etc/apt/keyrings/docker.asc && "
                    f"sudo tee /etc/apt/sources.list.d/docker.sources << 'EOF_DOCKER'\nTypes: deb\nURIs: https://download.docker.com/linux/ubuntu\nSuites: {codename}\nComponents: stable\nArchitectures: amd64\nSigned-By: /etc/apt/keyrings/docker.asc\nEOF_DOCKER\n && "
                    f"sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin && "
                    f"sudo usermod -aG docker $USER"
                )
            ) and run_cmd(
                "curl -LO 'https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl' && chmod +x kubectl && sudo install kubectl /usr/local/bin/ && rm -f kubectl"
            )
        },
        "5": {
            "name": "Microsoft .NET & C# Stack (.NET 8 LTS & .NET 9 SDK)",
            "action": lambda: run_cmd(
                "sudo apt update && (sudo apt install -y dotnet-sdk-8.0 || (curl -sSL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 8.0)) && "
                "curl -sSL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 9.0"
            )
        },
        "6": {
            "name": "Mobile App Dev (Flutter SDK, Dart, Android Tools, Scrcpy)",
            "action": lambda: run_cmd(
                "sudo apt update && sudo apt install -y git curl unzip xz-utils zip libglu1-mesa clang cmake ninja-build pkg-config libgtk-3-dev adb fastboot scrcpy openjdk-17-jdk && "
                "[ ! -d $HOME/.flutter ] && git clone https://github.com/flutter/flutter.git -b stable $HOME/.flutter; sudo ln -sf $HOME/.flutter/bin/flutter /usr/local/bin/flutter && sudo ln -sf $HOME/.flutter/bin/dart /usr/local/bin/dart && flutter --version"
            )
        }
    }

    if preset_type in presets:
        selected = presets[preset_type]
        print_status_card("⚡ BUNDEL PRESET TECH STACK", [
            ("Preset", selected["name"][:50], Theme.BOLD + Theme.WHITE),
            ("Status", "Memasang seluruh komponen preset...", Theme.PEACH)
        ])
        selected["action"]()
        configure_shell_paths()
        print()
        print_status_card("✨ PRESET SELESAI", [
            ("Preset", selected["name"][:50], Theme.BOLD + Theme.WHITE),
            ("Status", "● Komponen preset berhasil diproses", Theme.MINT)
        ])
        input(f" {Theme.PEACH}◆ Tekan [ENTER] untuk kembali ke menu...{Theme.RESET}")

def show_preset_menu():
    """Menampilkan menu paket rekomendasi / bundel instan dalam rounded box."""
    preset_items = [
        ("1", "Modern Full-Stack Web Dev"),
        ("2", "Cloud BaaS & Serverless"),
        ("3", "Database & NoSQL Suite"),
        ("4", "Docker CE & Cloud DevOps"),
        ("5", "Microsoft .NET & C# Stack"),
        ("6", "Mobile & Flutter App Dev")
    ]
    w1, w2 = 37, 40
    d1 = "─" * w1
    d2 = "─" * w2

    while True:
        clear_screen()
        print(make_box_top("⚡ BUNDEL TECH STACK REKOMENDASI", badge="v2.5"))
        raw_sub = "  Paket Siap Pakai untuk Web, Cloud, Database, DevOps & Mobile"
        pad_sub = " " * max(0, 78 - get_display_width(raw_sub))
        print(f"{Theme.BORDER}│{Theme.RESET}{Theme.GRAY}{raw_sub}{Theme.RESET}{pad_sub}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}├{d1}┬{d2}┤{Theme.RESET}")

        for i in range(0, len(preset_items), 2):
            n1, t1 = preset_items[i]
            col1 = format_menu_col(n1, t1, width=w1, num_color=Theme.MINT, title_color=Theme.BOLD)
            n2, t2 = preset_items[i + 1]
            col2 = format_menu_col(n2, t2, width=w2, num_color=Theme.MINT, title_color=Theme.BOLD)
            print(f"{Theme.BORDER}│{Theme.RESET}{col1}{Theme.BORDER}│{Theme.RESET}{col2}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}├{d1}┼{d2}┤{Theme.RESET}")
        col0 = format_menu_col("0", "Kembali ke Menu Utama", width=w1, num_color=Theme.RED)
        col_empty = " " * w2
        print(f"{Theme.BORDER}│{Theme.RESET}{col0}{Theme.BORDER}│{Theme.RESET}{col_empty}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}╰{d1}┴{d2}╯{Theme.RESET}")

        choice = input(f"\n {Theme.MINT}◆{Theme.RESET} {Theme.CYAN}guava{Theme.RESET} {Theme.GRAY}›{Theme.RESET} {Theme.PEACH}presets{Theme.RESET} {Theme.CYAN}❯{Theme.RESET} ").strip()
        if choice == "0":
            break
        elif choice in ["1", "2", "3", "4", "5", "6"]:
            install_preset(choice)
            break
        else:
            print(f" {Theme.RED}[!] Pilihan tidak valid.{Theme.RESET}")
            time.sleep(1)

def manage_services_menu():
    """Menu untuk mengelola status layanan database & web server di Linux."""
    sudo = get_sudo_prefix()
    services = [
        {"name": "Docker Daemon", "service": "docker"},
        {"name": "MongoDB (mongod)", "service": "mongod"},
        {"name": "PostgreSQL Database", "service": "postgresql"},
        {"name": "MariaDB / MySQL", "service": "mariadb"},
        {"name": "Redis In-Memory", "service": "redis-server"},
        {"name": "Nginx Web Server", "service": "nginx"},
        {"name": "Apache2 Web Server", "service": "apache2"}
    ]
    w1, w2 = 37, 40
    d1 = "─" * w1
    d2 = "─" * w2

    while True:
        clear_screen()
        print(make_box_top("⚙️ KONTROL SERVICE & SERVER", badge="systemctl"))
        raw_sub = "  Status Service Database, Web Server & Container Daemon"
        pad_sub = " " * max(0, 78 - get_display_width(raw_sub))
        print(f"{Theme.BORDER}│{Theme.RESET}{Theme.GRAY}{raw_sub}{Theme.RESET}{pad_sub}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}├{d1}┬{d2}┤{Theme.RESET}")

        for i in range(0, len(services), 2):
            s1 = services[i]
            out1 = subprocess.run(f"systemctl is-active {s1['service']} 2>/dev/null", shell=True, capture_output=True, text=True).stdout.strip()
            inst1 = (out1 == "active")
            col1 = format_app_col(i + 1, s1["name"], inst1, w1)

            if i + 1 < len(services):
                s2 = services[i + 1]
                out2 = subprocess.run(f"systemctl is-active {s2['service']} 2>/dev/null", shell=True, capture_output=True, text=True).stdout.strip()
                inst2 = (out2 == "active")
                col2 = format_app_col(i + 2, s2["name"], inst2, w2)
            else:
                col2 = " " * w2
            print(f"{Theme.BORDER}│{Theme.RESET}{col1}{Theme.BORDER}│{Theme.RESET}{col2}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}├{d1}┼{d2}┤{Theme.RESET}")
        col0 = format_menu_col("0", "Kembali ke Menu Utama", width=w1, num_color=Theme.RED)
        print(f"{Theme.BORDER}│{Theme.RESET}{col0}{Theme.BORDER}│{Theme.RESET}{' '*w2}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}╰{d1}┴{d2}╯{Theme.RESET}")
        print(f" {Theme.GRAY}Format: ketik nomor untuk Toggle (Start/Stop), atau misal: 1start, 1stop{Theme.RESET}")

        user_in = input(f"\n {Theme.MINT}◆{Theme.RESET} {Theme.CYAN}guava{Theme.RESET} {Theme.GRAY}›{Theme.RESET} {Theme.PEACH}services{Theme.RESET} {Theme.CYAN}❯{Theme.RESET} ").strip().lower()

        if user_in == "0":
            break

        action = "toggle"
        num_str = ""
        for act in ["start", "stop", "restart", "status"]:
            if user_in.endswith(act):
                action = act
                num_str = user_in[:-len(act)]
                break

        if not num_str and user_in.isdigit():
            num_str = user_in

        if num_str.isdigit() and 1 <= int(num_str) <= len(services):
            target_svc = services[int(num_str) - 1]
            svc_name = target_svc["service"]

            if action == "toggle":
                curr_status = subprocess.run(f"systemctl is-active {svc_name} 2>/dev/null", shell=True, capture_output=True, text=True).stdout.strip()
                action = "stop" if curr_status == "active" else "start"

            clear_screen()
            print_status_card("⚙️ KONTROL SERVICE", [
                ("Service", svc_name, Theme.BOLD + Theme.WHITE),
                ("Aksi", f"systemctl {action}", Theme.CYAN)
            ])
            run_cmd(f"{sudo}systemctl {action} {svc_name}")
            print()
            input(f" {Theme.PEACH}◆ Tekan [ENTER] untuk kembali ke kontrol service...{Theme.RESET}")
        else:
            print(f" {Theme.RED}[!] Input tidak valid.{Theme.RESET}")
            time.sleep(1)

def show_main_menu():
    """Menampilkan antarmuka pemilihan menu utama dalam format 2 kolom rounded box ricing."""
    categories = [
        ("1", "JS / TS Runtimes (Node, Bun)"),
        ("2", "Bahasa, Compiler & SDKs"),
        ("3", "Database Engines & Storage"),
        ("4", "Cloud BaaS & Serverless"),
        ("5", "Container & Infrastructure"),
        ("6", "Web Server & Reverse Proxy"),
        ("7", "DB Client GUI & API Tools"),
        ("8", "Mobile & App Development")
    ]
    cat_data_map = get_tech_categories()
    w1, w2 = 37, 40
    d1 = "─" * w1
    d2 = "─" * w2

    while True:
        clear_screen()
        print(make_box_top("⚡ TECH STACK & DEV ENVIRONMENT", badge="v2.5"))
        raw_sub = "  Node.js 24/22, Docker CE, Database, Cloud BaaS & Compiler Suite"
        pad_sub = " " * max(0, 78 - get_display_width(raw_sub))
        print(f"{Theme.BORDER}│{Theme.RESET}{Theme.GRAY}{raw_sub}{Theme.RESET}{pad_sub}{Theme.BORDER}│{Theme.RESET}")
        print(f"{Theme.BORDER}├{d1}┬{d2}┤{Theme.RESET}")

        for i in range(0, len(categories), 2):
            num1, title1 = categories[i]
            col1 = format_menu_col(num1, title1, width=w1, num_color=Theme.MINT, title_color=Theme.BOLD)
            if i + 1 < len(categories):
                num2, title2 = categories[i + 1]
                col2 = format_menu_col(num2, title2, width=w2, num_color=Theme.MINT, title_color=Theme.BOLD)
            else:
                col2 = " " * w2
            print(f"{Theme.BORDER}│{Theme.RESET}{col1}{Theme.BORDER}│{Theme.RESET}{col2}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}├{d1}┼{d2}┤{Theme.RESET}")

        ctrls = [
            ("P", "Bundel Preset Stack Cepat"),
            ("K", "Kontrol Layanan / Service"),
            ("S", "Konfigurasi PATH Shell"),
            ("U", "Perbarui Repositori APT"),
            ("0", "Keluar dari Tech Stack")
        ]

        for i in range(0, len(ctrls), 2):
            k1, label1 = ctrls[i]
            col1 = format_menu_col(k1, label1, width=w1, num_color=Theme.CYAN if k1 != "0" else Theme.RED)
            if i + 1 < len(ctrls):
                k2, label2 = ctrls[i + 1]
                col2 = format_menu_col(k2, label2, width=w2, num_color=Theme.CYAN if k2 != "0" else Theme.RED)
            else:
                col2 = " " * w2
            print(f"{Theme.BORDER}│{Theme.RESET}{col1}{Theme.BORDER}│{Theme.RESET}{col2}{Theme.BORDER}│{Theme.RESET}")

        print(f"{Theme.BORDER}╰{d1}┴{d2}╯{Theme.RESET}")

        choice = input(f"\n {Theme.MINT}◆{Theme.RESET} {Theme.CYAN}guava{Theme.RESET} {Theme.GRAY}›{Theme.RESET} {Theme.PEACH}tech-stack{Theme.RESET} {Theme.CYAN}❯{Theme.RESET} ").strip()

        if choice == "0":
            print(f"\n {Theme.MINT}[*] Terima kasih! Selamat mengembangkan aplikasi di Linux.{Theme.RESET}\n")
            break
        elif choice in cat_data_map:
            show_subcategory_menu(choice, cat_data_map[choice])
        elif choice.upper() == "P":
            show_preset_menu()
        elif choice.upper() == "K":
            manage_services_menu()
        elif choice.upper() == "S":
            clear_screen()
            print_status_card("⚙️ KONFIGURASI PATH", [
                ("Aksi", "Setup PATH Environment Shell", Theme.BOLD + Theme.WHITE),
                ("Shell", "Fish, Bash, dan Zsh", Theme.CYAN)
            ])
            configure_shell_paths()
            print()
            print_status_card("✨ SETUP PATH SELESAI", [
                ("Status", "● PATH environment berhasil diperbarui", Theme.MINT)
            ])
            input(f" {Theme.PEACH}◆ Tekan [ENTER] untuk kembali ke menu...{Theme.RESET}")
        elif choice.upper() == "U":
            sudo = get_sudo_prefix()
            clear_screen()
            print_status_card("🔄 PEMBARUAN SISTEM", [
                ("Tindakan", "APT Update & Upgrade", Theme.BOLD + Theme.WHITE),
                ("Status", "Memperbarui repositori dan paket Linux...", Theme.PEACH)
            ])
            run_cmd(f"{sudo}apt update -y && {sudo}apt upgrade -y")
            print()
            print_status_card("✨ PEMBARUAN SELESAI", [
                ("Status", "● Repositori & paket sistem berhasil diperbarui", Theme.MINT)
            ])
            input(f" {Theme.PEACH}◆ Tekan [ENTER] untuk kembali ke menu utama...{Theme.RESET}")
        else:
            print(f" {Theme.RED}[!] Pilihan '{choice}' tidak valid.{Theme.RESET}")
            time.sleep(1)

def main():
    """Fungsi utama program."""
    check_linux_env()
    show_main_menu()

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n{Colors.YELLOW}[*] Program dihentikan oleh pengguna.{Colors.RESET}")
        sys.exit(0)
