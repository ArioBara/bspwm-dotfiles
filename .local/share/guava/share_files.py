#!/usr/bin/env python3
"""
Instant LAN File Sharing Server & Upload Portal untuk Linux.
Menyediakan HTTP Server lokal, QR Code terminal untuk koneksi cepat smartphone,
serta dukungan unduh & unggah (upload) file langsung di browser.
"""

import http.server
import io
import os
import re
import socket
import sys
import urllib.parse
import shutil
import subprocess

import http.server
import io
import os
import re
import socket
import sys
import urllib.parse
import shutil
import subprocess
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
        prefix = f"  {label:<12}: "
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
        print(f"{Theme.BORDER}│{Theme.RESET}{Theme.GRAY}  {label:<12}: {Theme.RESET}{val_color}{val_str}{Theme.RESET}{pad}{Theme.BORDER}│{Theme.RESET}")
    dashes = "─" * (total_w - 2)
    print(f"{Theme.BORDER}╰{dashes}╯{Theme.RESET}\n")

def get_all_ip_addresses():
    """Mengambil seluruh alamat IP antarmuka jaringan yang aktif (Wi-Fi, LAN, VPN)."""
    ip_list = []
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        main_ip = s.getsockname()[0]
        s.close()
        if main_ip and main_ip != "127.0.0.1":
            ip_list.append(("Wi-Fi / LAN", main_ip))
    except Exception:
        pass

    try:
        out = subprocess.check_output("hostname -I 2>/dev/null", shell=True).decode().strip()
        for ip in out.split():
            if ip not in [item[1] for item in ip_list] and ":" not in ip:
                ip_list.append(("Secondary IP", ip))
    except Exception:
        pass

    if not ip_list:
        ip_list.append(("Localhost", "127.0.0.1"))

    return ip_list

def display_qr_code(url):
    """Menampilkan QR Code di terminal menggunakan qrencode."""
    if shutil.which("qrencode"):
        print(f" {Theme.BOLD}{Theme.PEACH}Scan QR Code via Smartphone untuk membuka berkas:{Theme.RESET}")
        os.system(f"qrencode -t ANSI256 '{url}' 2>/dev/null || qrencode -t UTF8 '{url}'")
    else:
        print(f" {Theme.GRAY}Tip: Pasang 'qrencode' (`sudo apt install qrencode`) untuk QR Code.{Theme.RESET}")

class UploadHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Handler dengan antarmuka web modern & dukungan upload file."""

    def do_POST(self):
        """Menangani unggah (upload) file dari browser."""
        content_type = self.headers.get('Content-Type', '')
        if not content_type.startswith('multipart/form-data'):
            self.send_error(400, "Bad Request: Hanya mendukung multipart/form-data")
            return

        boundary = content_type.split("boundary=")[1].encode()
        remain_bytes = int(self.headers.get('Content-Length', 0))
        
        line = self.rfile.readline()
        remain_bytes -= len(line)
        if boundary not in line:
            self.send_error(400, "Content NOT begin with boundary")
            return

        line = self.rfile.readline()
        remain_bytes -= len(line)
        fn_match = re.search(r'filename="(.+?)"', line.decode('utf-8', errors='ignore'))
        if not fn_match:
            self.send_error(400, "Tidak dapat menemukan nama file yang diunggah.")
            return

        fn = os.path.basename(fn_match.group(1))
        while remain_bytes > 0:
            line = self.rfile.readline()
            remain_bytes -= len(line)
            if line in (b'\r\n', b'\n'):
                break

        target_path = os.path.join(os.getcwd(), fn)
        with open(target_path, 'wb') as out_file:
            pre_line = self.rfile.readline()
            remain_bytes -= len(pre_line)
            while remain_bytes > 0:
                line = self.rfile.readline()
                remain_bytes -= len(line)
                if boundary in line:
                    out_file.write(pre_line.rstrip(b'\r\n'))
                    break
                else:
                    out_file.write(pre_line)
                    pre_line = line

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        response_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Upload Berhasil</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1e1e2e; color: #cdd6f4; text-align: center; padding: 40px 20px; }}
                .card {{ background: #181825; max-width: 480px; margin: 0 auto; padding: 30px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid #313244; }}
                h2 {{ color: #a6e3a1; }}
                a {{ display: inline-block; margin-top: 20px; background: #89b4fa; color: #1e1e2e; padding: 10px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>✓ File Berhasil Diunggah!</h2>
                <p>Nama File: <strong>{fn}</strong></p>
                <a href="/">Kembali ke Berkas</a>
            </div>
        </body>
        </html>
        """
        self.wfile.write(response_html.encode('utf-8'))

    def list_directory(self, path):
        try:
            list_dir = os.listdir(path)
        except os.error:
            self.send_error(404, "Tidak ada izin membaca folder.")
            return None

        list_dir.sort(key=lambda a: a.lower())
        r = []
        displaypath = urllib.parse.unquote(self.path)
        enc = sys.getfilesystemencoding()
        
        title = f"Berkas di {displaypath}"
        r.append('<!DOCTYPE html>')
        r.append('<html><head>')
        r.append('<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">')
        r.append(f'<title>{title}</title>')
        r.append('''<style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #1e1e2e; color: #cdd6f4; margin: 0; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            header { background: #181825; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #313244; }
            h1 { margin: 0 0 10px 0; font-size: 1.4rem; color: #89b4fa; }
            .upload-box { background: #181825; border: 2px dashed #45475a; border-radius: 12px; padding: 20px; margin-bottom: 20px; text-align: center; }
            input[type="file"] { margin-bottom: 10px; color: #cdd6f4; }
            input[type="submit"] { background: #a6e3a1; color: #1e1e2e; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; }
            input[type="submit"]:hover { background: #94e2d5; }
            table { width: 100%; border-collapse: collapse; background: #181825; border-radius: 12px; overflow: hidden; border: 1px solid #313244; }
            th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #313244; }
            th { background: #11111b; color: #a6adc8; }
            a { color: #89b4fa; text-decoration: none; word-break: break-all; }
            a:hover { text-decoration: underline; color: #b4befe; }
            .size { color: #a6adc8; font-size: 0.9rem; }
        </style></head><body><div class="container">''')
        
        r.append(f'<header><h1>📂 {title}</h1><p style="margin:0;color:#a6adc8;">Linux Local Share Server</p></header>')
        
        r.append('''<div class="upload-box">
            <form ENCTYPE="multipart/form-data" method="post">
                <h3 style="margin-top:0; color:#cdd6f4;">📤 Unggah File ke Folder Ini</h3>
                <input name="file" type="file"/> <br/>
                <input type="submit" value="Mulai Unggah"/>
            </form>
        </div>''')

        r.append('<table><thead><tr><th>Nama Berkas / Folder</th><th style="width:120px;">Ukuran</th></tr></thead><tbody>')
        
        if self.path != '/':
            r.append('<tr><td><a href="..">📁 .. (Kembali ke Folder Induk)</a></td><td>-</td></tr>')

        for name in list_dir:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            is_dir = os.path.isdir(fullname)
            if is_dir:
                displayname = f"📁 {name}/"
                linkname = f"{name}/"
                size_str = "Folder"
            else:
                displayname = f"📄 {name}"
                try:
                    size = os.path.getsize(fullname)
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024**2:
                        size_str = f"{size/1024:.1f} KB"
                    elif size < 1024**3:
                        size_str = f"{size/(1024**2):.1f} MB"
                    else:
                        size_str = f"{size/(1024**3):.1f} GB"
                except Exception:
                    size_str = "-"

            r.append(f'<tr><td><a href="{urllib.parse.quote(linkname)}">{displayname}</a></td><td class="size">{size_str}</td></tr>')

        r.append('</tbody></table></div></body></html>')
        encoded = '\n'.join(r).encode(enc, 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f

def start_server(share_dir=None, port=8080):
    clear_screen()
    if not share_dir:
        share_dir = os.getcwd()
    
    share_dir = os.path.abspath(os.path.expanduser(share_dir))
    if not os.path.exists(share_dir):
        print_status_card("❌ DIREKTORI TIDAK ADA", [
            ("Path", share_dir, Theme.RED),
        ])
        return

    os.chdir(share_dir)
    ip_list = get_all_ip_addresses()

    primary_url = ""
    card_items = [
        ("Direktori", share_dir, Theme.CYAN),
        ("Port", str(port), Theme.PEACH),
    ]

    for label, ip in ip_list:
        url = f"http://{ip}:{port}"
        if not primary_url and ip != "127.0.0.1":
            primary_url = url
        card_items.append((label, url, Theme.MINT))

    if not primary_url and ip_list:
        primary_url = f"http://{ip_list[0][1]}:{port}"

    print_status_card("🌐 INSTANT LAN FILE SHARING", card_items)
    display_qr_code(primary_url)

    print(f"\n {Theme.BOLD}{Theme.PEACH}◆ guava{Theme.RESET} › {Theme.CYAN}share-files{Theme.RESET} {Theme.MINT}● Server Aktif (Tekan CTRL+C untuk berhenti){Theme.RESET}\n")

    handler = UploadHTTPRequestHandler
    try:
        with http.server.ThreadingHTTPServer(("", port), handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n\n {Theme.PEACH}[*] Server dihentikan.{Theme.RESET}")
    except Exception as e:
        print(f"\n {Theme.RED}[!] Terjadi kesalahan pada server: {e}{Theme.RESET}")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    target_port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    start_server(target_dir, target_port)

