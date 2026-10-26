#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
quicknote: Minimalist Scratchpad & Markdown Quick Notes TUI
Author: ArioDev7
Theme: Catppuccin Mocha
"""

import os
import sys
import time
import datetime
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

NOTES_DIR = Path.home() / ".local" / "share" / "quicknote" / "notes"
SCRATCHPAD_FILE = NOTES_DIR / "scratchpad.md"

BANNER = rf"""{PEACH}{BOLD}
   ___  _   _ ___ ____ _  ___   _  ___ _____ _____ 
  / _ \| | | |_ _/ ___| |/ / \ | |/ _ \_   _| ____|
 | | | | | | || | |   | ' /|  \| | | | || | |  _|  
 | |_| | |_| || | |___| . \| |\  | |_| || | | |___ 
  \__\_\\___/|___\____|_|\_\_| \_|\___/ |_| |_____|
{RESET}{TEAL}  📝 Minimalist Scratchpad & Markdown Notes • by ArioDev7{RESET}
"""

def clear():
    os.system("clear")

def init_storage():
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    if not SCRATCHPAD_FILE.exists():
        with open(SCRATCHPAD_FILE, "w") as f:
            f.write("# 📝 Scratchpad Cepat\n\nCatatan sementara tanpa judul. Tambahkan apa saja di sini!\n\n")

def scratchpad_mode():
    init_storage()
    while True:
        clear()
        print(BANNER)
        print(f"{BOLD}{YELLOW}=== SCRATCHPAD CEPAT (AUTOSAVE) ==={RESET}\n")

        with open(SCRATCHPAD_FILE, "r") as f:
            lines = f.readlines()

        for line in lines[-20:]:
            sys.stdout.write(f"  {TEXT}{line}{RESET}")
        print(f"\n{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}")

        print(f"  {GREEN}[A]{RESET}  ➕ Tambah Catatan Singkat Baru")
        print(f"  {BLUE}[E]{RESET}  ✏️  Edit di Neovim")
        print(f"  {RED}[C]{RESET}  🗑️  Kosongkan Scratchpad")
        print(f"  {RED}[0]{RESET}  ⬅️  Kembali")

        pilihan = input(f"\n{YELLOW}Pilih opsi [A / E / C / 0]: {RESET}").strip().lower()

        if pilihan == "0":
            break
        elif pilihan == "a":
            note = input(f"{PEACH}Ketik catatan: {RESET}").strip()
            if note:
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                with open(SCRATCHPAD_FILE, "a") as f:
                    f.write(f"- [{now_str}] {note}\n")
                print(f"{GREEN}✓ Tersimpan!{RESET}")
                time.sleep(0.5)
        elif pilihan == "e":
            subprocess.run(["nvim", str(SCRATCHPAD_FILE)])
        elif pilihan == "c":
            confirm = input(f"{RED}Yakin ingin mengosongkan scratchpad? (y/n): {RESET}").strip().lower()
            if confirm == "y":
                with open(SCRATCHPAD_FILE, "w") as f:
                    f.write("# 📝 Scratchpad Cepat\n\n")
                print(f"{GREEN}✓ Dikosongkan.{RESET}")
                time.sleep(0.8)

def list_all_notes():
    init_storage()
    notes = [f for f in NOTES_DIR.glob("*.md") if f.name != "scratchpad.md"]
    notes.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return notes

def view_notes_menu():
    while True:
        clear()
        print(BANNER)
        notes = list_all_notes()
        print(f"{BOLD}{BLUE}=== DAFTAR CATATAN MARKDOWN ==={RESET}\n")

        if not notes:
            print(f"{YELLOW}Belum ada catatan bertopik. Buat catatan baru dengan memilih [N].{RESET}\n")
        else:
            for idx, n in enumerate(notes, start=1):
                mod_time = datetime.datetime.fromtimestamp(n.stat().st_mtime).strftime("%d %b %H:%M")
                lines_count = sum(1 for _ in open(n, "r", errors="ignore"))
                print(f"  {PINK}[{idx:02d}]{RESET} {BOLD}{TEXT}{n.stem:<28}{RESET} {SUBTEXT}• {lines_count:2d} baris • {mod_time}{RESET}")

        print(f"\n  {GREEN}[N]{RESET}  ➕ Buat Catatan Baru")
        print(f"  {RED}[D]{RESET}  ❌ Hapus Catatan")
        print(f"  {RED}[0]{RESET}  ⬅️  Kembali")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}")

        pilihan = input(f"{YELLOW}Pilih catatan [nomor / N / D / 0]: {RESET}").strip()

        if pilihan == "0":
            break
        elif pilihan.lower() == "n":
            title = input(f"{PEACH}Judul Catatan Baru (contoh: Ide Proyek, Cheatsheet): {RESET}").strip()
            if title:
                slug = title.replace(" ", "_") + ".md"
                new_path = NOTES_DIR / slug
                with open(new_path, "w") as f:
                    f.write(f"# {title}\n\nTanggal: {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n- [ ] Catatan pertama\n")
                subprocess.run(["nvim", str(new_path)])
        elif pilihan.lower() == "d":
            d_idx = input(f"{RED}Masukkan nomor catatan yang ingin dihapus: {RESET}").strip()
            if d_idx.isdigit() and 1 <= int(d_idx) <= len(notes):
                target = notes[int(d_idx) - 1]
                target.unlink(missing_ok=True)
                print(f"{GREEN}✓ Catatan '{target.stem}' dihapus.{RESET}")
                time.sleep(1)
        elif pilihan.isdigit():
            val = int(pilihan) - 1
            if 0 <= val < len(notes):
                manage_single_note(notes[val])

def manage_single_note(note_path):
    while True:
        clear()
        print(BANNER)
        print(f"{BOLD}{PEACH}=== MEMBACA: {note_path.stem} ==={RESET}")
        print(f"{OVERLAY}File: {note_path}{RESET}\n")

        with open(note_path, "r", errors="ignore") as f:
            content = f.read()

        for line in content.splitlines()[:25]:
            if line.startswith("# "):
                print(f"{BOLD}{MAUVE}{line}{RESET}")
            elif line.startswith("## "):
                print(f"{BOLD}{BLUE}{line}{RESET}")
            elif "- [x]" in line:
                print(f"{GREEN}{line}{RESET}")
            elif "- [ ]" in line:
                print(f"{YELLOW}{line}{RESET}")
            else:
                print(f"{TEXT}{line}{RESET}")

        print(f"\n{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}")
        print(f"  {BLUE}[E]{RESET} ✏️  Edit di Neovim")
        print(f"  {YELLOW}[T]{RESET} ☑️  Toggle Checklist Task (- [ ] <-> - [x])")
        print(f"  {RED}[0]{RESET} ⬅️  Kembali")

        pilihan = input(f"\n{YELLOW}Pilih aksi [E / T / 0]: {RESET}").strip().lower()

        if pilihan == "0":
            break
        elif pilihan == "e":
            subprocess.run(["nvim", str(note_path)])
        elif pilihan == "t":
            with open(note_path, "r") as f:
                lines = f.readlines()
            tasks = []
            for i, l in enumerate(lines):
                if "- [ ]" in l or "- [x]" in l:
                    tasks.append((i, l.strip()))
            if not tasks:
                print(f"{YELLOW}Tidak ada format checklist (- [ ] atau - [x]) di file ini.{RESET}")
                time.sleep(1.2)
                continue
            clear()
            print(f"{BOLD}{BLUE}Pilih nomor task untuk di-toggle:{RESET}\n")
            for t_idx, (line_no, text_line) in enumerate(tasks, start=1):
                print(f"  [{t_idx}] {text_line}")
            sel_t = input(f"\n{YELLOW}Nomor task: {RESET}").strip()
            if sel_t.isdigit() and 1 <= int(sel_t) <= len(tasks):
                target_l_no = tasks[int(sel_t) - 1][0]
                if "- [ ]" in lines[target_l_no]:
                    lines[target_l_no] = lines[target_l_no].replace("- [ ]", "- [x]")
                else:
                    lines[target_l_no] = lines[target_l_no].replace("- [x]", "- [ ]")
                with open(note_path, "w") as f:
                    f.writelines(lines)
                print(f"{GREEN}✓ Task diperbarui!{RESET}")
                time.sleep(0.8)

def search_notes():
    init_storage()
    clear()
    print(BANNER)
    print(f"{BOLD}{YELLOW}=== PENCARIAN CATATAN (FUZZY GREP) ==={RESET}\n")

    query = input(f"{PEACH}Ketik kata kunci yang dicari: {RESET}").strip()
    if not query:
        return

    matches = []
    for f in NOTES_DIR.glob("*.md"):
        with open(f, "r", errors="ignore") as file_obj:
            for l_idx, line in enumerate(file_obj, start=1):
                if query.lower() in line.lower():
                    matches.append((f.stem, l_idx, line.strip()))

    print(f"\n{SUBTEXT}Hasil pencarian untuk '{query}':{RESET}\n")
    if not matches:
        print(f"{YELLOW}Tidak ada catatan yang memuat kata '{query}'.{RESET}")
    else:
        for stem, l_no, line_text in matches:
            print(f"  {BLUE}[{stem}:{l_no}]{RESET} {TEXT}{line_text}{RESET}")

    input(f"\n{OVERLAY}[Tekan Enter untuk kembali]{RESET}")

def main():
    init_storage()
    while True:
        clear()
        print(BANNER)
        print(f"  {SUBTEXT}Pusat Catatan Cepat & Markdown Scratchpad{RESET}")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}\n")

        print(f"  {PEACH}[1]{RESET}  ⚡ Scratchpad Cepat (Catatan Harian Sekali Ketik)")
        print(f"  {BLUE}[2]{RESET}  📚 Daftar Catatan Lengkap (Markdown Topics)")
        print(f"  {TEAL}[3]{RESET}  🔍 Cari Kata Kunci di Semua Catatan")
        print(f"  {RED}[0]{RESET}  🚪 Keluar")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}")

        pilihan = input(f"{YELLOW}Pilih menu [0-3]: {RESET}").strip()

        if pilihan == "0" or pilihan.lower() == "q":
            print(f"{GREEN}Sampai jumpa! 📝{RESET}")
            break
        elif pilihan == "1":
            scratchpad_mode()
        elif pilihan == "2":
            view_notes_menu()
        elif pilihan == "3":
            search_notes()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{GREEN}Keluar.{RESET}")
