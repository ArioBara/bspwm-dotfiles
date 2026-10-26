# 󰎆 YouTube Music TUI • Linux Ricing Edition
> **Aesthetic, ultra-lightweight, and lightning-fast YouTube Music player in your terminal.**  
> Crafted with ❤️ by **ArioDev7** | Themed with **Catppuccin Mocha**

---

## 🌟 Sekilas Tentang Proyek (Overview)

**YouTube Music TUI** adalah aplikasi pemutar musik berbasis terminal (*Terminal User Interface*) yang dirancang khusus agar menyatu secara harmonis dengan setup **Linux Ricing** (BSPWM, Kitty, Polybar, Rofi, dan skema warna Catppuccin Mocha).

Aplikasi ini menggunakan backend pemutar audio **MPV** dengan arsitektur **Event-Driven IPC Socket** dan parser **`yt-dlp`** modern. Anda dapat mencari jutaan lagu, memutar streaming langsung beresolusi tinggi tanpa mengunduh file ke disk, melihat animasi visualizer equalizer, dan mengendalikan pemutaran via pintasan keyboard atau panel Polybar.

---

## ✨ Fitur Utama (Features)

- 🎨 **Palet Catppuccin Mocha**: Selaras sempurna dengan tema Kitty, font Nerd Fonts, dan mendukung transparansi latar belakang terminal (*translucent*).
- ⚡ **Pencarian Kilat (Vim-Style Inline Search)**: Cukup tekan `/` atau `s` untuk mencari lagu secara asinkron tanpa membebani pemutaran musik yang sedang berjalan.
- 🎵 **Streaming Langsung Instan via MPV**: Menggunakan MPV IPC Unix Socket (`--idle=yes`). Memutar stream dalam ~1 detik dengan konsumsi RAM dan CPU yang sangat minim.
- 📊 **Animated Waveform Equalizer**: Visualizer equalizer dinamis (` ▂▃▅▆▇▆▅▃ `) yang berdenyut secara otomatis saat musik diputar.
- 📑 **Antrean & Riwayat Lagu (Queue & History)**: Tambah lagu ke antrean (`a`), navigasi antrean (`Tab`), putar lagu berikutnya otomatis saat lagu selesai, dan ulangi lagu sebelumnya (`p`).
- 🖥️ **Integrasi Penuh BSPWM & Polybar**:
  - **Global Hotkey**: Tekan `Super + Y` untuk membuka aplikasi dalam jendela melayang (*floating window*) di tengah layar.
  - **Rofi App Launcher**: Terdaftar otomatis sebagai aplikasi desktop sistem.
  - **Polybar & MPRIS**: Judul lagu dan artis otomatis terbaca oleh modul Polybar dan perintah `playerctl`.
- 󰋖 **Layar Bantuan Keybindings Interaktif (`?`)**: Tekan `?` kapan saja untuk melihat panduan tombol tanpa meninggalkan aplikasi.

---

## 📦 Dependensi Sistem (Dependencies)

Sebelum menjalankan aplikasi, pastikan dependensi berikut terpasang di sistem Linux Anda:

| Paket | Keterangan | Status di Sistem |
|---|---|---|
| **`python3`** (≥ 3.10) | Interpreter Python utama (modul bawaan `curses`, `socket`, `json`) | Wajib |
| **`mpv`** | Mesin pemutar audio/video terminal berkinerja tinggi | Wajib |
| **`mpv-mpris`** | Plugin DBus MPRIS agar MPV terhubung ke Polybar & `playerctl` | Sangat Direkomendasikan |
| **`yt-dlp`** | Engine pengekstrak audio YouTube versi terbaru | Wajib |
| **`JetBrainsMono Nerd Font`** | Font terminal agar icon musik (`󰎆`, `󰐊`, `󰕾`, dll.) tampil sempurna | Direkomendasikan |

### 📥 Perintah Instalasi Dependensi

#### 1. Untuk Debian / Ubuntu / Linux Mint:
```bash
# Pasang MPV dan integrasi MPRIS
sudo apt update
sudo apt install -y mpv mpv-mpris python3 curl
```

#### 2. Untuk Arch Linux / Manjaro:
```bash
sudo pacman -S mpv mpv-mpris python yt-dlp curl
```

#### 3. Untuk Fedora:
```bash
sudo dnf install -y mpv mpv-mpris python3 yt-dlp curl
```

#### 4. Memasang / Memperbarui `yt-dlp` (Versi Standalone Terbaru):
YouTube kerap memperbarui protokol API mereka. Gunakan binary mandiri resmi `yt-dlp` agar pencarian dan streaming selalu lancar:
```bash
mkdir -p ~/.local/bin
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o ~/.local/bin/yt-dlp
chmod +x ~/.local/bin/yt-dlp
```
*(Pastikan `~/.local/bin` sudah ada di dalam variabel `$PATH` shell Anda).*

---

## 🚀 Instalasi & Penyiapan (Setup)

### 1. Menjadikan Program Dapat Dijalankan di Mana Saja
File program utama terletak di `~/Scripts/ytmusic-tui/ytmusic.py`. Buat symlink ke direktori bin lokal Anda:
```bash
chmod +x ~/Scripts/ytmusic-tui/ytmusic.py
ln -sf ~/Scripts/ytmusic-tui/ytmusic.py ~/.local/bin/ytmusic
```

### 2. Integrasi Window Manager (BSPWM)
Agar aplikasi terbuka otomatis dalam mode jendela melayang (*floating*) berukuran ideal di tengah layar, tambahkan baris berikut ke `~/.config/bspwm/bspwmrc`:
```bash
bspc rule -a Kitty:ytmusic-term state=floating center=on rectangle=960x560+0+0
```

### 3. Shortcut Keyboard Global (SXHKD)
Tambahkan konfigurasi berikut ke `~/.config/sxhkd/sxhkdrc`:
```bash
# YouTube Music TUI (Floating Window)
super + y
	kitty --class ytmusic-term -e ytmusic
```
Lalu muat ulang sxhkd dengan:
```bash
pkill -USR1 -x sxhkd
```

### 4. Shortcut Menu Aplikasi (Rofi / Application Launcher)
Buat file desktop di `~/.local/share/applications/ytmusic.desktop`:
```ini
[Desktop Entry]
Name=YouTube Music TUI
Comment=Catppuccin Mocha TUI for YouTube Music by ArioDev7
Exec=kitty --class ytmusic-term -T "YouTube Music • by ArioDev7" -e /home/ario/.local/bin/ytmusic
Icon=multimedia-audio-player
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Player;
Keywords=youtube;music;tui;catppuccin;player;rice;ariodev7;
```
Perbarui cache database desktop:
```bash
update-desktop-database ~/.local/share/applications/
```

---

## 🎮 Cara Penggunaan & Kontrol (Keybindings)

### Cara Membuka Aplikasi
- **Pintasan Global**: Tekan **`Super + Y`** di keyboard.
- **Terminal**: Ketik perintah:
  ```bash
  ytmusic
  ```
- **Menu Rofi**: Tekan `Super + Space` atau `Super + D`, lalu cari **"YouTube Music TUI"**.

---

### ⌨️ Daftar Lengkap Tombol Kontrol

| Tombol Pintas | Kategori | Aksi / Fungsi |
|:---:|:---:|---|
| **`/`** atau **`s`** | **Pencarian** | Mengaktifkan bar pencarian di bagian bawah. Ketik judul/artis lalu tekan **`Enter`**. |
| **`Esc`** | **Pencarian** | Membatalkan input pencarian dan kembali ke navigasi normal. |
| **`k`** atau **`↑`** | **Navigasi** | Menggeser kursor ke baris lagu di atasnya (*Vim keys*). |
| **`j`** atau **`↓`** | **Navigasi** | Menggeser kursor ke baris lagu di bawahnya (*Vim keys*). |
| **`Enter`** | **Pemutaran** | Memutar lagu yang sedang disorot. |
| **`Spasi`** | **Pemutaran** | Jeda / Lanjutkan lagu (*Play / Pause toggle*). |
| **`a`** | **Antrean** | Menambahkan lagu yang disorot ke dalam antrean (*Queue*). |
| **`Tab`** | **Tampilan** | Beralih tab antara Hasil Pencarian dan Antrean (*Queue*). |
| **`d`** atau **`x`** | **Antrean** | Menghapus lagu yang disorot dari daftar antrean. |
| **`c`** | **Antrean** | Mengosongkan / membersihkan seluruh antrean lagu. |
| **`n`** | **Pemutaran** | Memutar lagu berikutnya di antrean (*Next*). |
| **`p`** | **Pemutaran** | Memutar lagu sebelumnya (*Previous*) atau mengulang dari detik 0. |
| **`r`** | **Pemutaran** | Mengganti mode putar ulang (*Repeat: OFF / SINGLE TRACK*). |
| **`+`** atau **`=`** | **Audio** | Menaikkan volume suara (+5%). |
| **`-`** atau **`_`** | **Audio** | Menurunkan volume suara (-5%). |
| **`m`** | **Audio** | Membisukan / mengaktifkan suara (*Mute / Unmute toggle*). |
| **`→`** atau **`l`** | **Durasi** | Geser waktu maju 10 detik (*Seek forward*). |
| **`←`** | **Durasi** | Geser waktu mundur 10 detik (*Seek backward*). |
| **`?`** atau **`h`** | **Bantuan** | Membuka layar pop-up panduan tombol keybindings. |
| **`q`** | **Sistem** | Keluar dari aplikasi dan membersihkan socket MPV. |

---

## 🔧 Struktur Teknis & Arsitektur (Architecture)

```text
ytmusic-tui/
├── ytmusic.py       # Source code utama (MpvController, Track, YoutubeMusicTUI)
├── README.md        # Dokumentasi lengkap proyek
└── __pycache__/     # Bytecode Python terkompilasi
```

- **IPC Socket**: `/tmp/ytmusic_mpv_<uid>.sock`
- **Model Komunikasi**: JSON-RPC asinkron via Unix Domain Socket.
- **Properti yang Dipantau Secara Live (`observe_property`)**:
  - `time-pos`: Posisi detik pemutaran real-time untuk progress bar.
  - `duration`: Total durasi aktual lagu.
  - `pause`: Deteksi status jeda/putar.
  - `mute`: Status pembisuan audio.
  - `end-file`: Deteksi otomatis saat lagu selesai untuk memutar antrean berikutnya (*gapless-like transition*).
- **Penanganan Kesalahan (*Error Handling*)**:
  - Auto-cleanup instans zombie MPV pada startup dan shutdown (`atexit`).
  - Proteksi penuh *try-except* pada pemanggilan `curses.use_default_colors()` dan kursor terminal.
  - Filter sanitasi hasil pencarian YouTube (mengabaikan channel ID `UC...` dan playlist rusak).

---

## ❓ FAQ & Penyelesaian Masalah (Troubleshooting)

#### 1. Lagu tidak mengeluarkan suara sama sekali?
- Pastikan paket `mpv` sudah terpasang:
  ```bash
  which mpv
  ```
- Periksa volume suara terminal atau sistem Anda melalui `pavucontrol` atau tombol `+` di aplikasi.
- Pastikan server audio sistem Anda (PipeWire atau PulseAudio) sedang berjalan normal:
  ```bash
  systemctl --user status pipewire
  ```

#### 2. Ikon musik dan kontrol tampil kotak-kotak (*tofu glyphs*)?
- Aplikasi ini menggunakan simbol **Nerd Fonts** (`JetBrainsMono Nerd Font`).
- Pastikan font diatur dengan benar di konfigurasi terminal Kitty Anda (`~/.config/kitty/kitty.conf`):
  ```conf
  font_family JetBrainsMono Nerd Font
  ```

#### 3. Pencarian tidak memunculkan hasil lagu?
- Pastikan koneksi internet Anda aktif.
- Perbarui binary `yt-dlp` ke rilis terbaru:
  ```bash
  yt-dlp -U
  # atau unduh ulang binary terbaru:
  curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o ~/.local/bin/yt-dlp
  ```

---

## 👤 Pengembang & Kontributor (Credits)

- **Author**: [ArioDev7](https://github.com/ArioBara)
- **Palette & Styling**: [Catppuccin Mocha](https://github.com/catppuccin/catppuccin)
- **Window Management**: BSPWM + Kitty + Polybar Rice Setup

---

<div align="center">
  <sub>Dibuat dengan dedikasi untuk komunitas Linux Ricing Indonesia. Enjoy the music! 🎧</sub>
</div>
