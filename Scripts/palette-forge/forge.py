#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
palette-forge: Wallpaper Color Extractor & Theme Forge TUI
Author: ArioDev7
Theme: Catppuccin Mocha & Dynamic Palettes
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from PIL import Image

# Catppuccin Base UI Colors
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

CACHE_DIR = Path.home() / ".cache" / "palette-forge"

BANNER = rf"""{YELLOW}{BOLD}
  ____   _    _     _____ _____ _____ _____ 
 |  _ \ / \  | |   | ____|_   _|_   _| ____|
 | |_) / _ \ | |   |  _|   | |   | | |  _|  
 |  __/ ___ \| |___| |___  | |   | | | |___ 
 |_| /_/   \_\_____|_____| |_|   |_| |_____|
{RESET}{TEAL}  🎨 Wallpaper Color Extractor & Dynamic Theme Forge • Catppuccin{RESET}
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

def get_current_wallpaper():
    cw = Path.home() / ".current_wallpaper"
    if cw.exists():
        try:
            with open(cw, "r") as f:
                p = f.read().strip()
                if Path(p).exists():
                    return Path(p)
        except Exception:
            pass

    feh = Path.home() / ".fehbg"
    if feh.exists():
        try:
            with open(feh, "r") as f:
                content = f.read()
                for part in content.split("'"):
                    if Path(part).is_file() and any(part.lower().endswith(ext) for ext in [".jpg", ".png", ".jpeg"]):
                        return Path(part)
        except Exception:
            pass

    wp_dir = Path.home() / ".config" / "bspwm" / "wallpapers"
    if wp_dir.exists():
        imgs = list(wp_dir.glob("*.jpg")) + list(wp_dir.glob("*.png"))
        if imgs:
            return imgs[0]

    return None

def extract_palette(image_path, num_colors=16):
    try:
        img = Image.open(image_path).convert("RGB")
        # Resize small for fast analysis
        img = img.resize((150, 150))
        # Quantize to target color count
        quant = img.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)
        palette = quant.getpalette()[:num_colors * 3]

        colors = []
        for i in range(0, len(palette), 3):
            r, g, b = palette[i], palette[i+1], palette[i+2]
            hex_code = f"#{r:02x}{g:02x}{b:02x}"
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            colors.append({
                "r": r, "g": g, "b": b,
                "hex": hex_code,
                "lum": luminance
            })
        # Sort by brightness
        colors.sort(key=lambda c: c["lum"])
        return colors
    except Exception as e:
        print(f"{RED}Gagal mengekstrak warna: {e}{RESET}")
        return []

def draw_palette(colors, wallpaper_path):
    print(f"  {SUBTEXT}Wallpaper Teranalisis: {BOLD}{TEXT}{Path(wallpaper_path).name}{RESET}")
    print(f"  {OVERLAY}Lokasi: {wallpaper_path}{RESET}\n")

    col_w = [4, 12, 10, 18, 25]
    top = OVERLAY + "┌" + "┬".join("─" * (w + 2) for w in col_w) + "┐" + RESET
    mid = OVERLAY + "├" + "┼".join("─" * (w + 2) for w in col_w) + "┤" + RESET
    bot = OVERLAY + "└" + "┴".join("─" * (w + 2) for w in col_w) + "┘" + RESET

    print(top)
    header = OVERLAY + "│ " + (OVERLAY + " │ ").join([
        cell("No", col_w[0], color=PEACH + BOLD),
        cell("Warna Swatch", col_w[1], color=BLUE + BOLD),
        cell("Hex Code", col_w[2], color=TEAL + BOLD),
        cell("RGB Format", col_w[3], color=YELLOW + BOLD),
        cell("Uji Kontras Teks", col_w[4], color=GREEN + BOLD)
    ]) + OVERLAY + " │" + RESET
    print(header)
    print(mid)

    for idx, c in enumerate(colors, start=1):
        r, g, b = c["r"], c["g"], c["b"]
        hex_c = c["hex"]
        bg = f"\033[48;2;{r};{g};{b}m"
        fg = "\033[38;2;0;0;0m" if c["lum"] > 128 else "\033[38;2;255;255;255m"
        swatch_color = f"\033[38;2;{r};{g};{b}m"

        swatch = f"{swatch_color}████████{RESET}    "
        contrast = f"{bg}{fg} Contoh Teks ABC {RESET}" + " " * 8
        rgb_str = f"({r:3d},{g:3d},{b:3d})"

        row = OVERLAY + "│ " + (OVERLAY + " │ ").join([
            cell(f"[{idx:02d}]", col_w[0], color=PINK),
            swatch,
            cell(hex_c, col_w[2], color=TEXT),
            cell(rgb_str, col_w[3], color=SUBTEXT),
            contrast
        ]) + OVERLAY + " │" + RESET
        print(row)

    print(bot)
    print("")

def apply_bspwm_border(color_hex):
    try:
        subprocess.run(["bspc", "config", "active_border_color", color_hex])
        print(f"{GREEN}✓ Aksen border aktif BSPWM berhasil diganti menjadi {color_hex}!{RESET}")
    except Exception as e:
        print(f"{RED}Gagal mengubah border BSPWM: {e}{RESET}")

def export_palette(colors, wallpaper_path):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    json_path = CACHE_DIR / "current_palette.json"
    sh_path = CACHE_DIR / "palette.sh"

    data = {
        "wallpaper": str(wallpaper_path),
        "colors": colors
    }
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)

    with open(sh_path, "w") as f:
        f.write("#!/usr/bin/env bash\n# Generated by palette-forge\n")
        f.write(f'export WALLPAPER="{wallpaper_path}"\n')
        for i, c in enumerate(colors):
            f.write(f'export COLOR{i}="{c["hex"]}"\n')

    print(f"{GREEN}✓ Berhasil diekspor ke:{RESET}")
    print(f"  {SUBTEXT}• JSON : {json_path}{RESET}")
    print(f"  {SUBTEXT}• Bash : {sh_path}{RESET}")

def choose_wallpaper():
    wp_dir = Path.home() / ".config" / "bspwm" / "wallpapers"
    wps = []
    if wp_dir.exists():
        wps = list(wp_dir.glob("*.jpg")) + list(wp_dir.glob("*.png")) + list(wp_dir.glob("*.jpeg"))

    clear()
    print(BANNER)
    print(f"{BOLD}{BLUE}=== PILIH WALLPAPER UNTUK DIEKSTRAK ==={RESET}\n")

    for i, w in enumerate(wps, start=1):
        print(f"  {PINK}[{i:02d}]{RESET} {TEXT}{w.name}{RESET}")

    print(f"\n  {RED}[0]{RESET} Batal")
    print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}")

    choice = input(f"{YELLOW}Pilih nomor [1-{len(wps)}] atau ketik path gambar kustom: {RESET}").strip()
    if choice == "0":
        return None
    if choice.isdigit() and 1 <= int(choice) <= len(wps):
        return wps[int(choice) - 1]
    elif Path(choice).is_file():
        return Path(choice)
    return None

def main():
    cur_wp = get_current_wallpaper()
    if not cur_wp or not cur_wp.exists():
        cur_wp = Path.home() / ".config" / "bspwm" / "wallpapers" / "naruto.jpg"

    colors = extract_palette(cur_wp)

    while True:
        clear()
        print(BANNER)
        draw_palette(colors, cur_wp)

        print(f"  {PEACH}[1]{RESET}  ✨ Terapkan Warna ke Border Aktif BSPWM")
        print(f"  {BLUE}[2]{RESET}  💾 Simpan & Ekspor Skema Warna (JSON & Bash Script)")
        print(f"  {TEAL}[3]{RESET}  🖼️  Ganti Wallpaper untuk Diekstrak")
        print(f"  {RED}[0]{RESET}  🚪 Keluar")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}")

        pilihan = input(f"{YELLOW}Pilih menu [0-3]: {RESET}").strip()

        if pilihan == "0" or pilihan.lower() == "q":
            print(f"{GREEN}Sampai jumpa! 🎨{RESET}")
            break
        elif pilihan == "1":
            color_num = input(f"{PEACH}Pilih nomor warna [1-{len(colors)}] untuk border BSPWM: {RESET}").strip()
            if color_num.isdigit() and 1 <= int(color_num) <= len(colors):
                sel_hex = colors[int(color_num) - 1]["hex"]
                apply_bspwm_border(sel_hex)
                time.sleep(1.2)
        elif pilihan == "2":
            export_palette(colors, cur_wp)
            input(f"\n{OVERLAY}[Tekan Enter untuk kembali]{RESET}")
        elif pilihan == "3":
            new_wp = choose_wallpaper()
            if new_wp:
                cur_wp = new_wp
                colors = extract_palette(cur_wp)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{GREEN}Keluar.{RESET}")
