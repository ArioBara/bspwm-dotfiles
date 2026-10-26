#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lanshare: Local WiFi File Transfer via QR Code & Web Portal
Author: ArioDev7
Theme: Catppuccin Mocha
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import cgi
import time
import socket
import qrcode
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Catppuccin Colors
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

DOWNLOAD_DIR = Path.home() / "Downloads" / "lanshare"

BANNER = rf"""{TEAL}{BOLD}
  _        _    _   _ ____  _   _    _    ____  _____ 
 | |      / \  | \ | / ___|| | | |  / \  |  _ \| ____|
 | |     / _ \ |  \| \___ \| |_| | / _ \ | |_) |  _|  
 | |___ / ___ \| |\  |___) |  _  |/ ___ \|  _ <| |___ 
 |_____/_/   \_\_| \_|____/|_| |_/_/   \_\_| \_\_____|
{RESET}{PINK}  📲 Transfer File WiFi Laptop ⇄ HP via QR Code • by ArioDev7{RESET}
"""

def clear():
    os.system("clear")

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't actually send data, just identifies outgoing interface
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def print_qr(url):
    qr = qrcode.QRCode(box_size=1, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    qr.print_ascii(invert=True)

class SingleFileSendHandler(BaseHTTPRequestHandler):
    filepath = None
    filename = None

    def log_message(self, format, *args):
        # Clean terminal logging
        pass

    def do_GET(self):
        if not self.filepath or not os.path.exists(self.filepath):
            self.send_error(404, "File not found")
            return

        stat = os.stat(self.filepath)
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Disposition", f'attachment; filename="{self.filename}"')
        self.send_header("Content-Length", str(stat.st_size))
        self.end_headers()

        print(f"\n{GREEN}⚡ [DOWNLOAD DIMULAI] Perangkat HP mulai mengunduh {self.filename}...{RESET}")
        try:
            with open(self.filepath, "rb") as f:
                while chunk := f.read(64 * 1024):
                    self.wfile.write(chunk)
            print(f"{GREEN}✓ [SELESAI] File {self.filename} sukses terkirim ke HP!{RESET}")
        except Exception as e:
            print(f"{RED}Koneksi terputus: {e}{RESET}")

UPLOAD_HTML = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LANShare • Kirim ke Laptop</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #1e1e2e;
      color: #cdd6f4;
      margin: 0;
      padding: 24px 16px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .card {
      background: #181825;
      border: 1px solid #313244;
      border-radius: 16px;
      padding: 24px;
      max-width: 440px;
      width: 100%;
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
      text-align: center;
    }
    h1 { color: #cba6f7; margin-top: 0; font-size: 22px; }
    p { color: #a6adc8; font-size: 14px; margin-bottom: 24px; }
    .dropzone {
      border: 2px dashed #89b4fa;
      border-radius: 12px;
      padding: 30px 16px;
      background: #11111b;
      cursor: pointer;
      margin-bottom: 20px;
      transition: all 0.2s;
    }
    .dropzone:hover { border-color: #a6e3a1; }
    input[type="file"] { display: none; }
    .btn {
      background: #cba6f7;
      color: #11111b;
      border: none;
      padding: 14px 28px;
      border-radius: 10px;
      font-weight: bold;
      font-size: 16px;
      cursor: pointer;
      width: 100%;
    }
    .btn:active { transform: scale(0.98); }
    .footer { margin-top: 20px; font-size: 12px; color: #6c7086; }
    #selected-file { margin-top: 10px; font-weight: bold; color: #a6e3a1; word-break: break-all; }
  </style>
</head>
<body>
  <div class="card">
    <h1>📲 LANShare Portal</h1>
    <p>Pilih foto, video, atau dokumen dari HP Anda untuk langsung dikirim ke folder Downloads di laptop.</p>
    <form method="POST" enctype="multipart/form-data" id="upload-form">
      <label class="dropzone" for="file-input">
        <div style="font-size: 40px; margin-bottom: 10px;">📁</div>
        <div>Ketuk untuk Memilih File</div>
        <div id="selected-file"></div>
      </label>
      <input type="file" id="file-input" name="file" required onchange="showFile(this)">
      <button type="submit" class="btn" id="upload-btn">Kirim ke Laptop 🚀</button>
    </form>
    <div class="footer">Koneksi WiFi Lokal • Aman & Cepat • by ArioDev7</div>
  </div>
  <script>
    function showFile(input) {
      if (input.files && input.files[0]) {
        document.getElementById('selected-file').innerText = '✓ ' + input.files[0].name + ' (' + (input.files[0].size / (1024*1024)).toFixed(2) + ' MB)';
      }
    }
  </script>
</body>
</html>
"""

UPLOAD_SUCCESS_HTML = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sukses Terkirim!</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #1e1e2e;
      color: #cdd6f4;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 90vh;
      margin: 0;
    }
    .card {
      background: #181825;
      border: 1px solid #a6e3a1;
      border-radius: 16px;
      padding: 32px 24px;
      max-width: 400px;
      text-align: center;
    }
    h1 { color: #a6e3a1; font-size: 24px; margin-top: 10px; }
    a { display: inline-block; margin-top: 20px; color: #89b4fa; text-decoration: none; font-weight: bold; }
  </style>
</head>
<body>
  <div class="card">
    <div style="font-size: 50px;">🎉</div>
    <h1>File Berhasil Terkirim!</h1>
    <p>File telah tersimpan di laptop pada folder <b>~/Downloads/lanshare/</b>.</p>
    <a href="/">Kirim File Lainnya ➔</a>
  </div>
</body>
</html>
"""

class UploadServerHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(UPLOAD_HTML.encode("utf-8"))

    def do_POST(self):
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']}
        )
        if "file" in form:
            file_item = form["file"]
            filename = os.path.basename(file_item.filename)
            if filename:
                out_path = DOWNLOAD_DIR / filename
                with open(out_path, "wb") as f:
                    f.write(file_item.file.read())

                print(f"\n{GREEN}🎉 [FILE DITERIMA] Sukses menerima '{filename}' dari HP!{RESET}")
                print(f"{SUBTEXT}Disimpan di: {out_path}{RESET}")

                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(UPLOAD_SUCCESS_HTML.encode("utf-8"))
                return

        self.send_response(400)
        self.end_headers()
        self.wfile.write(b"Upload gagal.")

def send_file_mode():
    clear()
    print(BANNER)
    print(f"{BOLD}{BLUE}=== MODE KIRIM FILE KE HP ==={RESET}\n")

    file_input = input(f"{PEACH}Ketik / seret (drag & drop) path file yang ingin dikirim: {RESET}").strip().strip("'\"")
    if not file_input:
        return
    p = Path(file_input).expanduser().resolve()
    if not p.is_file():
        print(f"{RED}File tidak ditemukan: {p}{RESET}")
        time.sleep(1.5)
        return

    local_ip = get_local_ip()
    port = 8484
    url = f"http://{local_ip}:{port}/{urllib.parse.quote(p.name)}"

    SingleFileSendHandler.filepath = str(p)
    SingleFileSendHandler.filename = p.name

    clear()
    print(BANNER)
    print(f"{BOLD}{GREEN}✓ SERVER SIAP MENGIRIM FILE!{RESET}")
    print(f"  {SUBTEXT}File:{RESET} {BOLD}{TEXT}{p.name}{RESET} ({p.stat().st_size / (1024*1024):.2f} MB)")
    print(f"  {SUBTEXT}Link Download:{RESET} {BOLD}{BLUE}{url}{RESET}\n")
    print(f"{YELLOW}Arahkan kamera HP Anda ke QR Code di bawah untuk langsung mengunduh:{RESET}\n")

    print_qr(url)

    print(f"\n{OVERLAY}Tekan [Ctrl+C] di terminal ini jika sudah selesai mengunduh.{RESET}\n")

    try:
        httpd = HTTPServer((local_ip, port), SingleFileSendHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Server pengiriman dihentikan.{RESET}")
        time.sleep(1)

def receive_file_mode():
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    local_ip = get_local_ip()
    port = 8585
    url = f"http://{local_ip}:{port}/"

    clear()
    print(BANNER)
    print(f"{BOLD}{GREEN}✓ PORTAL UPLOAD DARI HP SIAP!{RESET}")
    print(f"  {SUBTEXT}Folder Penyimpanan Laptop:{RESET} {BOLD}{TEXT}{DOWNLOAD_DIR}{RESET}")
    print(f"  {SUBTEXT}Buka di Browser HP:{RESET} {BOLD}{BLUE}{url}{RESET}\n")
    print(f"{YELLOW}Scan QR Code di bawah untuk membuka halaman upload di HP Anda:{RESET}\n")

    print_qr(url)

    print(f"\n{OVERLAY}Server aktif di latar belakang. Tekan [Ctrl+C] untuk mengakhiri.{RESET}\n")

    try:
        httpd = HTTPServer((local_ip, port), UploadServerHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Portal penerimaan dihentikan.{RESET}")
        time.sleep(1)

def main():
    while True:
        clear()
        print(BANNER)
        local_ip = get_local_ip()
        print(f"  {OVERLAY}Alamat IP WiFi Laptop Anda:{RESET} {BOLD}{BLUE}{local_ip}{RESET}")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}\n")

        print(f"  {PEACH}[1]{RESET}  📤 Kirim File dari Laptop ke HP (Tampilkan QR Code Download)")
        print(f"  {BLUE}[2]{RESET}  📥 Terima File dari HP ke Laptop (Buka Web Upload Portal)")
        print(f"  {TEAL}[3]{RESET}  📂 Buka Folder Berkas Diterima (~/Downloads/lanshare)")
        print(f"  {RED}[0]{RESET}  🚪 Keluar")
        print(f"{OVERLAY}───────────────────────────────────────────────────────────────────────{RESET}")

        pilihan = input(f"{YELLOW}Pilih menu [0-3]: {RESET}").strip()

        if pilihan == "0" or pilihan.lower() == "q":
            print(f"{GREEN}Sampai jumpa! 📲{RESET}")
            break
        elif pilihan == "1":
            send_file_mode()
        elif pilihan == "2":
            receive_file_mode()
        elif pilihan == "3":
            DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
            subprocess.Popen(["nemo", str(DOWNLOAD_DIR)])
            print(f"{GREEN}Membuka folder {DOWNLOAD_DIR}...{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{GREEN}Keluar.{RESET}")
