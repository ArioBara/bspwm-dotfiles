# 󰒍 Tailscale & Honcho Network Monitor (Ricing Edition)
> **Aesthetic, ultra-responsive, real-time WireGuard Mesh & Honcho AI Memory monitor.**  
> Crafted with ❤️ by **ArioDev7** | Themed with **Catppuccin Mocha**

---

## 🌟 Sekilas Tentang Proyek (Overview)

**Tailscale & Honcho Monitor (`netmon`)** adalah aplikasi pemantauan jaringan dan backend AI berbasis TUI (*Terminal User Interface*) yang dirancang khusus untuk menyatu dengan setup **Linux Ricing** (BSPWM, Kitty, Polybar, dan skema warna Catppuccin Mocha).

Aplikasi ini memantau koneksi mesh **Tailscale WireGuard** serta server memori agen **Honcho** di Cloud VPS (`vmi3356393:8001` / `100.125.78.92:8001`) secara real-time dan asinkron tanpa membebani CPU/RAM.

---

## ✨ Fitur Utama (Features)

- 🎨 **Palet Catppuccin Mocha**: Selaras sempurna dengan Kitty terminal, rounded box (`╭─╮`), font Nerd Fonts, dan transparansi latar belakang.
- 󰛳 **ASCII Network Topology**: Visualisasi grafis ASCII interaktif yang menggambarkan alur mesh antara PC lokal (`ario-bzx`), Cloud VPS (`vmi3356393:8001`), dan PC kantor (`hermes`).
- ⚡ **Asynchronous Live Data**: Pembaruan otomatis setiap 4 detik di latar belakang (background thread) sehingga navigasi antarmuka tetap instan dan lancar.
- 󰒍 **Tailscale Mesh Inspector**:
  - Menampilkan perangkat lokal sendiri (`ario-bzx` • `100.87.102.16`) di posisi teratas dengan badge `● (Saya)`
  - Deteksi status node peer (● Online / ○ Offline)
  - Pengukuran latensi ping langsung (ms) & deteksi jalur DERP relay vs Direct
  - Aksi ping langsung (`p`) ke node yang sedang dipilih (loopback untuk perangkat sendiri)
- 󰌘 **Honcho AI Health & Memory Status**:
  - Health check endpoint (`/health`) & response latency
  - Informasi workspace aktif (`Autopreneur` / `hermes`) & peran agen (`fixer`, `oracle`, `orchestrator`, dll.)
  - Daftar 16 peers AI yang terdaftar di workspace
  - Progress bar status antrean deriver background task
- 󰋖 **Layar Bantuan Keybindings Interaktif (`?` / `h`)**: Akses cepat ke daftar pintasan keyboard.

---

## 🎮 Pintasan Keyboard (Keybindings)

| Tombol | Fungsi |
|---|---|
| **`Tab`** | Beralih antar tab secara siklis (*Overview* ➔ *Peers* ➔ *Honcho*) |
| **`1`, `2`, `3`** | Langsung lompat ke Tab 1 (Overview), Tab 2 (Peers), atau Tab 3 (Honcho) |
| **`k` / `↑`, `j` / `↓`** | Navigasi baris pada daftar Node atau Peers |
| **`p`** | Kirim ping langsung ke node Tailscale yang dipilih (Tab Peers) |
| **`r`** | Paksa pembaruan data secara instan (*Manual Refresh*) |
| **`?` / `h` / `F1`** | Buka / Tutup panduan keybindings interaktif |
| **`q` / `Esc`** | Keluar dari aplikasi |

---

## 🚀 Cara Menjalankan

Aplikasi ini tidak memerlukan virtual environment atau package pip pihak ketiga (menggunakan modul bawaan Python 3 murni).

### 1. Eksekusi Langsung dari Terminal
Symlink telah dibuat di `~/.local/bin/netmon`. Cukup ketik:
```bash
netmon
```
Atau jalankan file skripnya:
```bash
~/Scripts/tailscale-honcho-monitor/monitor.py
```

### 2. Kustomisasi Parameter (Environment Variables)
Secara default aplikasi mengarah ke `http://vmi3356393:8001` dengan workspace `hermes`. Anda dapat mengubahnya sewaktu-waktu:
```bash
HONCHO_API_URL="http://100.125.78.92:8001" HONCHO_WORKSPACE_ID="hermes" netmon
```

---

## 🖥️ Integrasi Linux Ricing (BSPWM & SXHKD)

### 1. Floating Window Rule (BSPWM)
Tambahkan baris berikut ke `~/.config/bspwm/bspwmrc` agar terbuka dalam floating window rapi di tengah layar:
```bash
bspc rule -a Kitty:netmon-term state=floating center=on rectangle=980x600+0+0
```

### 2. Global Hotkey (SXHKD)
Tambahkan ke `~/.config/sxhkd/sxhkdrc`:
```bash
# Tailscale & Honcho Monitor Floating Window
super + ctrl + m
	kitty --class netmon-term -T "Mesh & Honcho Monitor • by ArioDev7" -e netmon
```
Lalu muat ulang sxhkd:
```bash
pkill -USR1 -x sxhkd
```

### 3. Application Launcher (Rofi / Desktop Entry)
Simpan file desktop di `~/.local/share/applications/netmon.desktop`:
```ini
[Desktop Entry]
Name=Netmon (Tailscale & Honcho)
Comment=Catppuccin Mocha Network & AI Memory Monitor
Exec=kitty --class netmon-term -T "Mesh & Honcho Monitor • by ArioDev7" -e /home/ario/.local/bin/netmon
Icon=network-wired
Terminal=false
Type=Application
Categories=Network;System;Monitor;
```

---
*Dibuat oleh **ArioDev7** untuk workflow Linux Ricing.*
