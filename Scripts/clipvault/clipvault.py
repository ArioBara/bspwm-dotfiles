#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clipvault: Smart Clipboard History & Snippet Vault TUI
Author: ArioDev7
Theme: Catppuccin Mocha
"""

import os
import sys
import time
import json
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
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

CACHE_DIR = Path.home() / ".cache" / "clipvault"
CONFIG_DIR = Path.home() / ".config" / "clipvault"
HISTORY_FILE = CACHE_DIR / "history.json"
SNIPPETS_FILE = CONFIG_DIR / "snippets.json"

BANNER = rf"""{PINK}{BOLD}
   ____ _     ___ ______     ___   _   _ _   _____ 
  / ___| |   |_ _|  _ \ \   / / \ | | | | | |_   _|
 | |   | |    | || |_) \ \ / / _ \| | | | |   | |  
 | |___| |___ | ||  __/ \ V / ___ \ |_| | |___| |  
  \____|_____|___|_|     \_/_/   \_\___/|_____|_|  
{RESET}{TEAL}  📋 Smart Clipboard History & Snippet Vault • Catppuccin Mocha{RESET}
"""

DEFAULT_SNIPPETS = [
    {
        "category": "Docker",
        "title": "Cek log container terbaru",
        "content": "docker logs --tail 50 -f <container_name>"
    },
    {
        "category": "Git",
        "title": "Batalkan commit terakhir (simpan perubahan file)",
        "content": "git reset --soft HEAD~1"
    },
    {
        "category": "System",
        "title": "Cek port yang sedang didengarkan (LISTEN)",
        "content": "sudo ss -tulpn | grep LISTEN"
    },
    {
        "category": "SSH",
        "title": "Generate kunci SSH Ed25519 baru",
        "content": 'ssh-keygen -t ed25519 -C "ario@dev"'
    },
    {
        "category": "Network",
        "title": "Cek IP lokal dan IP publik instan",
        "content": "ip -br a && echo -n 'Public IP: ' && curl -s ifconfig.me && echo ''"
    }
]

def clear():
    os.system("clear")

def get_x11_clipboard():
    try:
        res = subprocess.run(["xclip", "-selection", "clipboard", "-o"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=1)
        return res.stdout
    except Exception:
        try:
            res = subprocess.run(["xsel", "-b", "-o"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=1)
            return res.stdout
        except Exception:
            return ""

def set_x11_clipboard(text):
    try:
        p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
        p.communicate(input=text.encode("utf-8"))
        # Also copy to primary selection
        p2 = subprocess.Popen(["xclip", "-selection", "primary"], stdin=subprocess.PIPE)
        p2.communicate(input=text.encode("utf-8"))
        return True
    except Exception:
        try:
            p = subprocess.Popen(["xsel", "-b", "-i"], stdin=subprocess.PIPE)
            p.communicate(input=text.encode("utf-8"))
            return True
        except Exception:
            return False

def load_history():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        cur = get_x11_clipboard().strip()
        hist = [cur] if cur else []
        with open(HISTORY_FILE, "w") as f:
            json.dump(hist, f, indent=2)
        return hist
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(hist):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(hist[:100], f, indent=2)

def update_clipboard_history():
    current = get_x11_clipboard()
    if not current or not current.strip():
        return
    current = current.strip()
    hist = load_history()
    if current in hist:
        hist.remove(current)
    hist.insert(0, current)
    save_history(hist)

def load_snippets():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not SNIPPETS_FILE.exists():
        with open(SNIPPETS_FILE, "w") as f:
            json.dump(DEFAULT_SNIPPETS, f, indent=2)
        return DEFAULT_SNIPPETS
    try:
        with open(SNIPPETS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_SNIPPETS

def save_snippets(snippets):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(SNIPPETS_FILE, "w") as f:
        json.dump(snippets, f, indent=2)

def view_clipboard_history():
    update_clipboard_history()
    while True:
        clear()
        print(BANNER)
        hist = load_history()
        print(f"{BOLD}{PEACH}=== RIWAYAT CLIPBOARD TERBARU ==={RESET}")
        print(f"{SUBTEXT}Pilih nomor untuk menyalin kembali teks ke clipboard Anda.{RESET}\n")

        if not hist:
            print(f"{YELLOW}Riwayat clipboard kosong.{RESET}")
        else:
            for idx, item in enumerate(hist[:15], start=1):
                clean_item = item.replace("\n", " ↵ ")
                if len(clean_item) > 60:
                    clean_item = clean_item[:57] + "..."
                print(f"  {PINK}[{idx:02d}]{RESET} {TEXT}{clean_item}{RESET}")

        print(f"\n  {RED}[C]{RESET}  🗑️  Bersihkan Seluruh Riwayat")
        print(f"  {RED}[0]{RESET}  ⬅️  Kembali ke Menu Utama")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}")

        pilihan = input(f"{YELLOW}Pilih nomor [1-{min(15, len(hist))}] atau [C/0]: {RESET}").strip()

        if pilihan == "0":
            break
        elif pilihan.lower() == "c":
            save_history([])
            print(f"{GREEN}✓ Riwayat clipboard berhasil dikosongkan.{RESET}")
            time.sleep(1)
        elif pilihan.isdigit():
            val = int(pilihan) - 1
            if 0 <= val < len(hist):
                sel = hist[val]
                set_x11_clipboard(sel)
                print(f"{GREEN}✓ Berhasil disalin ke clipboard!{RESET}")
                time.sleep(0.8)
                break

def view_snippets():
    while True:
        clear()
        print(BANNER)
        snippets = load_snippets()
        print(f"{BOLD}{BLUE}=== DAFTAR SNIPPET VAULT ==={RESET}")
        print(f"{SUBTEXT}Pilih snippet untuk menyalin langsung perintah ke clipboard.{RESET}\n")

        for idx, s in enumerate(snippets, start=1):
            cat_badge = f"{MAUVE}[{s.get('category', 'General')}]{RESET}"
            print(f"  {PINK}[{idx:02d}]{RESET} {cat_badge} {BOLD}{TEXT}{s['title']}{RESET}")
            content_preview = s['content'].replace('\n', ' ↵ ')
            if len(content_preview) > 65:
                content_preview = content_preview[:62] + "..."
            print(f"       {SUBTEXT}↳ {content_preview}{RESET}")

        print(f"\n  {GREEN}[A]{RESET}  ➕ Tambah Snippet Baru")
        print(f"  {RED}[D]{RESET}  ❌ Hapus Snippet")
        print(f"  {RED}[0]{RESET}  ⬅️  Kembali ke Menu Utama")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}")

        pilihan = input(f"{YELLOW}Pilih aksi [nomor / A / D / 0]: {RESET}").strip()

        if pilihan == "0":
            break
        elif pilihan.lower() == "a":
            clear()
            print(BANNER)
            print(f"{BOLD}{GREEN}=== TAMBAH SNIPPET BARU ==={RESET}\n")
            cat = input(f"{PEACH}Kategori (misal Docker, Git, Linux): {RESET}").strip() or "General"
            title = input(f"{PEACH}Judul Snippet: {RESET}").strip()
            if not title:
                print(f"{RED}Judul tidak boleh kosong!{RESET}")
                time.sleep(1)
                continue
            content = input(f"{PEACH}Isi Perintah / Teks: {RESET}").strip()
            if not content:
                print(f"{RED}Konten tidak boleh kosong!{RESET}")
                time.sleep(1)
                continue
            snippets.append({"category": cat, "title": title, "content": content})
            save_snippets(snippets)
            print(f"\n{GREEN}✓ Snippet '{title}' berhasil disimpan!{RESET}")
            time.sleep(1)
        elif pilihan.lower() == "d":
            del_idx = input(f"{RED}Masukkan nomor snippet yang ingin dihapus: {RESET}").strip()
            if del_idx.isdigit() and 1 <= int(del_idx) <= len(snippets):
                removed = snippets.pop(int(del_idx) - 1)
                save_snippets(snippets)
                print(f"{GREEN}✓ Snippet '{removed['title']}' berhasil dihapus.{RESET}")
                time.sleep(1)
        elif pilihan.isdigit():
            val = int(pilihan) - 1
            if 0 <= val < len(snippets):
                sel = snippets[val]
                set_x11_clipboard(sel['content'])
                print(f"{GREEN}✓ Perintah '{sel['title']}' berhasil disalin ke clipboard!{RESET}")
                time.sleep(1)
                break

def daemon_mode():
    print(f"{TEAL}Menjalankan daemon pemantau clipboard ClipVault di latar belakang...{RESET}")
    last_clip = get_x11_clipboard()
    while True:
        try:
            time.sleep(1)
            cur = get_x11_clipboard()
            if cur and cur != last_clip:
                last_clip = cur
                update_clipboard_history()
        except KeyboardInterrupt:
            break
        except Exception:
            pass

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        daemon_mode()
        return

    update_clipboard_history()

    while True:
        clear()
        print(BANNER)
        current = get_x11_clipboard().strip().replace("\n", " ↵ ")
        if len(current) > 55:
            current = current[:52] + "..."
        if not current:
            current = "(Kosong)"

        print(f"  {OVERLAY}Clipboard Saat Ini:{RESET} {BOLD}{GREEN}{current}{RESET}")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}\n")

        print(f"  {PEACH}[1]{RESET}  📋 Riwayat Clipboard (Lihat & Salin Cepat)")
        print(f"  {BLUE}[2]{RESET}  ⚡ Snippet Vault (Perintah & Template Tersimpan)")
        print(f"  {TEAL}[3]{RESET}  ➕ Simpan Clipboard Saat Ini ke Snippet Vault")
        print(f"  {YELLOW}[4]{RESET}  🔄 Mulai Background Daemon Listener")
        print(f"  {RED}[0]{RESET}  🚪 Keluar")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}")

        pilihan = input(f"{YELLOW}Pilih menu [0-4]: {RESET}").strip()

        if pilihan == "0" or pilihan.lower() == "q":
            print(f"{GREEN}Sampai jumpa! 📋{RESET}")
            break
        elif pilihan == "1":
            view_clipboard_history()
        elif pilihan == "2":
            view_snippets()
        elif pilihan == "3":
            raw_clip = get_x11_clipboard().strip()
            if not raw_clip:
                print(f"{RED}Clipboard kosong, tidak ada yang bisa disimpan.{RESET}")
                time.sleep(1)
                continue
            cat = input(f"{PEACH}Kategori: {RESET}").strip() or "General"
            title = input(f"{PEACH}Judul Snippet: {RESET}").strip() or "Snippet Cepat"
            snips = load_snippets()
            snips.append({"category": cat, "title": title, "content": raw_clip})
            save_snippets(snips)
            print(f"{GREEN}✓ Berhasil disimpan ke Snippet Vault!{RESET}")
            time.sleep(1)
        elif pilihan == "4":
            subprocess.Popen(["python3", str(Path(__file__).resolve()), "--daemon"])
            print(f"{GREEN}✓ Daemon berhasil dijalankan di background!{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{GREEN}Keluar.{RESET}")
