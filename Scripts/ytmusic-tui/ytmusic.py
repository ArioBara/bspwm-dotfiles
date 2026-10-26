#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ytmusic-tui: YouTube Music Terminal User Interface
Author & Ricing: ArioDev7
Dirancang khusus untuk Linux Ricing (Catppuccin Mocha, BSPWM & Kitty).
"""

import os
import sys
import time
import json
import socket
import shutil
import random
import atexit
import curses
import subprocess
import threading
from typing import List, Dict, Optional

# Path binary yt-dlp & IPC socket
LOCAL_YT_DLP = os.path.expanduser("~/.local/bin/yt-dlp")
YT_DLP_BIN = LOCAL_YT_DLP if os.path.exists(LOCAL_YT_DLP) else "yt-dlp"
IPC_SOCKET = f"/tmp/ytmusic_mpv_{os.getuid()}.sock"

class Track:
    def __init__(self, video_id: str, title: str, artist: str, duration: int, duration_str: str):
        self.video_id = video_id
        self.title = title.strip()
        self.artist = artist.strip() if artist else "YouTube Artist"
        self.duration = duration
        self.duration_str = duration_str or "00:00"

class MpvController:
    """Mengelola proses pemutar MPV melalui IPC Unix Socket JSON-RPC secara asinkron."""
    def __init__(self, on_track_end_callback=None):
        self.process: Optional[subprocess.Popen] = None
        self.sock: Optional[socket.socket] = None
        self.on_track_end = on_track_end_callback
        
        self.current_track: Optional[Track] = None
        self.is_playing = False
        self.is_paused = False
        self.is_muted = False
        self.volume = 80
        self.time_pos = 0.0
        self.duration = 0.0
        self.loop_mode = "off"  # "off", "single"
        
        self._lock = threading.Lock()
        self._running = False
        self._reader_thread: Optional[threading.Thread] = None

    def is_mpv_installed(self) -> bool:
        return shutil.which("mpv") is not None

    def start(self) -> bool:
        if not self.is_mpv_installed():
            return False

        # Bersihkan instans MPV dan socket lama
        self._cleanup_old_instances()

        cmd = [
            "mpv",
            "--no-video",
            "--idle=yes",
            f"--input-ipc-server={IPC_SOCKET}",
            f"--volume={self.volume}",
            "--demuxer-max-bytes=10M",
            "--demuxer-readahead-secs=15",
            "--ytdl-format=bestaudio/best",
        ]

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
        except Exception:
            return False

        # Tunggu socket siap (maks 3 detik)
        for _ in range(30):
            if os.path.exists(IPC_SOCKET):
                break
            time.sleep(0.1)

        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.connect(IPC_SOCKET)
        except Exception:
            return False

        self._running = True
        self._reader_thread = threading.Thread(target=self._socket_reader, daemon=True)
        self._reader_thread.start()

        # Daftarkan observasi properti ke MPV
        self.send_command(["observe_property", 1, "time-pos"])
        self.send_command(["observe_property", 2, "duration"])
        self.send_command(["observe_property", 3, "pause"])
        self.send_command(["observe_property", 4, "mute"])
        return True

    def _cleanup_old_instances(self):
        try:
            subprocess.run(["pkill", "-9", "-f", f"input-ipc-server={IPC_SOCKET}"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        if os.path.exists(IPC_SOCKET):
            try:
                os.remove(IPC_SOCKET)
            except OSError:
                pass

    def send_command(self, cmd_list: list):
        with self._lock:
            if not self.sock:
                return
            try:
                msg = json.dumps({"command": cmd_list}) + "\n"
                self.sock.sendall(msg.encode("utf-8"))
            except Exception:
                pass

    def play(self, track: Track):
        self.current_track = track
        self.duration = float(track.duration or 0)
        self.time_pos = 0.0
        self.is_playing = True
        self.is_paused = False

        url = f"https://www.youtube.com/watch?v={track.video_id}"
        self.send_command(["loadfile", url, "replace"])
        self.send_command(["set_property", "pause", False])

    def toggle_pause(self):
        if not self.is_playing:
            return
        self.send_command(["cycle", "pause"])

    def toggle_mute(self):
        self.send_command(["cycle", "mute"])

    def seek(self, seconds: int):
        if self.is_playing:
            self.send_command(["seek", seconds, "relative"])

    def adjust_volume(self, delta: int):
        self.volume = max(0, min(130, self.volume + delta))
        self.send_command(["set_property", "volume", self.volume])

    def stop(self):
        self._running = False
        self.is_playing = False
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass
        self.sock = None
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=1.0)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None
        if os.path.exists(IPC_SOCKET):
            try:
                os.remove(IPC_SOCKET)
            except OSError:
                pass

    def _socket_reader(self):
        """Membaca event dan perubahan properti MPV secara asinkron (Event-Driven)."""
        try:
            f = self.sock.makefile("r", encoding="utf-8", errors="ignore")
        except Exception:
            return

        for line in f:
            if not self._running:
                break
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                evt = data.get("event")
                if evt == "property-change":
                    name = data.get("name")
                    val = data.get("data")
                    if name == "time-pos" and isinstance(val, (int, float)):
                        self.time_pos = float(val)
                    elif name == "duration" and isinstance(val, (int, float)):
                        self.duration = float(val)
                    elif name == "pause" and isinstance(val, bool):
                        self.is_paused = val
                    elif name == "mute" and isinstance(val, bool):
                        self.is_muted = val

                elif evt == "playback-restart":
                    self.is_playing = True

                elif evt == "end-file":
                    reason = data.get("reason")
                    if reason in ["eof", "stop"]:
                        self.is_playing = False
                        self.time_pos = 0.0
                        if self.on_track_end:
                            self.on_track_end(reason)
            except Exception:
                pass

class YoutubeMusicTUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.mpv = MpvController(on_track_end_callback=self._handle_track_finished)
        
        # State Data
        self.search_results: List[Track] = []
        self.queue: List[Track] = []
        self.history: List[Track] = []
        self.active_tab = "SEARCH"  # "SEARCH" atau "QUEUE"
        self.selected_idx = 0
        self.query = "lofi hip hop beats"
        
        # UI State
        self.view_mode = "PLAYER"   # "PLAYER" atau "HELP"
        self.search_active = False  # Sedang mengetik pencarian
        self.search_input = []      # List karakter input pencarian
        self.is_searching = False   # Background worker sedang aktif
        
        self.status_message = "Tekan [/] untuk Cari Lagu • [?] Bantuan Keybindings • by ArioDev7"
        self.status_time = time.time()
        
        # Animasi equalizer
        self.eq_heights = [2, 4, 6, 8, 7, 5, 3, 6, 8, 4, 2, 5, 7, 3, 6, 8]
        self.eq_chars = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        
        self._init_curses()
        self._running = True

    def _init_curses(self):
        try:
            if curses.has_colors():
                curses.start_color()
        except Exception:
            pass

        try:
            curses.use_default_colors()
        except Exception:
            pass

        self._set_cursor(0)
        self.stdscr.nodelay(True)
        self.stdscr.timeout(100) # Loop 100ms untuk kelancaran animasi & responsivitas

    def _set_cursor(self, val: int):
        try:
            curses.curs_set(val)
        except Exception:
            pass

        # Skema Catppuccin Mocha (selaras dengan konfigurasi Kitty)
        curses.init_pair(1, curses.COLOR_MAGENTA, -1) # Mauve (#cba6f7)
        curses.init_pair(2, curses.COLOR_CYAN, -1)    # Teal (#94e2d5)
        curses.init_pair(3, curses.COLOR_GREEN, -1)   # Green (#a6e3a1)
        curses.init_pair(4, curses.COLOR_YELLOW, -1)  # Peach/Yellow (#fab387)
        curses.init_pair(5, curses.COLOR_RED, -1)     # Red (#f38ba8)
        curses.init_pair(6, curses.COLOR_BLUE, -1)    # Blue/Sapphire (#89b4fa)
        curses.init_pair(7, curses.COLOR_WHITE, -1)   # Text (#cdd6f4)
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_MAGENTA) # Baris Terpilih Aktif
        curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_CYAN)    # Secondary Accent

    def set_status(self, msg: str):
        self.status_message = msg
        self.status_time = time.time()

    def search_youtube(self, query: str):
        """Menjalankan pencarian YouTube di background thread tanpa membekukan antarmuka."""
        q = query.strip()
        if not q:
            return
        self.query = q
        self.is_searching = True
        self.set_status(f"󰠃 Mencari '{self.query}' di YouTube...")

        def _worker():
            cmd = [
                YT_DLP_BIN,
                "--dump-json",
                "--flat-playlist",
                "--no-warnings",
                f"ytsearch20:{self.query}"
            ]
            results = []
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )
                for line in proc.stdout:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        vid = data.get("id")
                        # Filter channel atau link yang bukan video
                        if not vid or str(vid).startswith("UC") or data.get("_type") == "playlist":
                            continue

                        title = data.get("title", "Unknown Title")
                        uploader = data.get("uploader") or data.get("channel") or "YouTube Artist"
                        dur = data.get("duration") or 0
                        dur_str = data.get("duration_string") or self._format_time(dur)
                        results.append(Track(str(vid), title, uploader, int(dur), dur_str))
                    except Exception:
                        continue
                proc.wait()
            except Exception as e:
                self.set_status(f"Gagal mencari: {e}")
            finally:
                self.search_results = results
                self.selected_idx = 0
                self.is_searching = False
                self.active_tab = "SEARCH"
                if results:
                    self.set_status(f"󰄬 Ditemukan {len(results)} lagu untuk '{self.query}'.")
                else:
                    self.set_status(f"󰅚 Tidak ditemukan hasil untuk '{self.query}'. Coba kata kunci lain.")

        threading.Thread(target=_worker, daemon=True).start()

    def play_track(self, track: Track):
        if self.mpv.current_track and self.mpv.current_track.video_id != track.video_id:
            self.history.append(self.mpv.current_track)
        self.set_status(f"󰐊 Memuat audio: {track.title[:32]}...")
        self.mpv.play(track)

    def _handle_track_finished(self, reason: str):
        """Callback saat lagu selesai diputar oleh MPV."""
        if self.mpv.loop_mode == "single" and self.mpv.current_track:
            self.play_track(self.mpv.current_track)
        elif self.queue:
            next_song = self.queue.pop(0)
            self.play_track(next_song)

    def _format_time(self, seconds: float) -> str:
        s = int(max(0, seconds))
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    def _get_active_list(self) -> List[Track]:
        return self.search_results if self.active_tab == "SEARCH" else self.queue

    def run(self):
        # Jalankan MPV
        if not self.mpv.start():
            self._render_missing_mpv()
            return

        # Daftarkan penutupan aman pada atexit
        atexit.register(self.mpv.stop)

        # Mulai dengan pencarian awal otomatis
        self.search_youtube(self.query)

        while self._running:
            self._update_animation()
            self._draw()
            self._handle_input()

        self.mpv.stop()

    def _update_animation(self):
        # Animasi bar visualizer jika sedang memutar musik
        if self.mpv.is_playing and not self.mpv.is_paused:
            for i in range(len(self.eq_heights)):
                delta = random.randint(-2, 2)
                self.eq_heights[i] = max(1, min(8, self.eq_heights[i] + delta))
        else:
            for i in range(len(self.eq_heights)):
                self.eq_heights[i] = 1

    def _handle_input(self):
        try:
            key = self.stdscr.getch()
        except Exception:
            return

        if key == -1:
            return

        # 1. Mode Bantuan (Help Modal aktif)
        if self.view_mode == "HELP":
            # Sembarang tombol atau Esc akan menutup menu bantuan
            if key in [ord("?"), ord("h"), ord("H"), 27, 10, 13, curses.KEY_ENTER, ord("q"), ord("Q")]:
                self.view_mode = "PLAYER"
                self.set_status("Kembali ke pemutar musik.")
            return

        # 2. Mode Input Pencarian Aktif
        if self.search_active:
            if key == 27: # Esc -> Batalkan pencarian
                self.search_active = False
                self._set_cursor(0)
                self.set_status("Pencarian dibatalkan.")
            elif key in [10, 13, curses.KEY_ENTER]: # Enter -> Jalankan pencarian
                q = "".join(self.search_input).strip()
                self.search_active = False
                self._set_cursor(0)
                if q:
                    self.search_youtube(q)
            elif key in [curses.KEY_BACKSPACE, 127, 8]: # Backspace
                if self.search_input:
                    self.search_input.pop()
            elif 32 <= key <= 126: # Karakter teks
                if len(self.search_input) < 50:
                    self.search_input.append(chr(key))
            return

        # 3. Mode Normal Pemutar Musik (Normal Controls)
        items = self._get_active_list()

        if key in [ord("q"), ord("Q")]:
            self._running = False

        # Buka Bantuan Keybindings
        elif key in [ord("?"), ord("h"), ord("H"), curses.KEY_F1]:
            self.view_mode = "HELP"

        # Buka Input Pencarian
        elif key in [ord("/"), ord("s"), ord("S"), curses.KEY_F3]:
            self.search_active = True
            self.search_input = []
            self._set_cursor(1)

        # Navigasi Baris
        elif key in [curses.KEY_UP, ord("k"), ord("K")]:
            if self.selected_idx > 0:
                self.selected_idx -= 1

        elif key in [curses.KEY_DOWN, ord("j"), ord("J")]:
            if self.selected_idx < len(items) - 1:
                self.selected_idx += 1

        # Putar Lagu Terpilih
        elif key in [10, 13, curses.KEY_ENTER]:
            if 0 <= self.selected_idx < len(items):
                self.play_track(items[self.selected_idx])

        # Tambahkan ke Antrean
        elif key in [ord("a"), ord("A")]:
            if 0 <= self.selected_idx < len(items):
                track = items[self.selected_idx]
                self.queue.append(track)
                self.set_status(f"󰄬 Masuk antrean: {track.title[:30]}")

        # Hapus dari Antrean
        elif key in [ord("d"), ord("x")]:
            if self.active_tab == "QUEUE" and 0 <= self.selected_idx < len(self.queue):
                removed = self.queue.pop(self.selected_idx)
                if self.selected_idx >= len(self.queue):
                    self.selected_idx = max(0, len(self.queue) - 1)
                self.set_status(f"Dihapus dari antrean: {removed.title[:30]}")

        # Bersihkan Antrean
        elif key == ord("c"):
            if self.active_tab == "QUEUE":
                self.queue.clear()
                self.selected_idx = 0
                self.set_status("Antrean telah dibersihkan.")

        # Play / Pause
        elif key == ord(" "):
            self.mpv.toggle_pause()
            st = "󰏤 Dijeda" if self.mpv.is_paused else "󰐊 Melanjutkan"
            self.set_status(st)

        # Alihkan Tab (Hasil Cari <-> Antrean)
        elif key == 9: # Tab
            self.active_tab = "QUEUE" if self.active_tab == "SEARCH" else "SEARCH"
            self.selected_idx = 0
            self.set_status(f"Beralih ke tab: {self.active_tab}")

        # Seek Maju / Mundur
        elif key in [curses.KEY_RIGHT, ord("l")]:
            self.mpv.seek(10)
            self.set_status("󰒭 Maju +10 detik")

        elif key in [curses.KEY_LEFT]:
            self.mpv.seek(-10)
            self.set_status("󰒮 Mundur -10 detik")

        # Volume
        elif key in [ord("+"), ord("=")]:
            self.mpv.adjust_volume(5)
            self.set_status(f"󰕾 Volume: {self.mpv.volume}%")

        elif key in [ord("-"), ord("_")]:
            self.mpv.adjust_volume(-5)
            self.set_status(f"󰕾 Volume: {self.mpv.volume}%")

        elif key == ord("m"):
            self.mpv.toggle_mute()
            st = "󰖁 Suara Dibisukan" if self.mpv.is_muted else f"󰕾 Suara Aktif ({self.mpv.volume}%)"
            self.set_status(st)

        # Next / Prev
        elif key in [ord("n"), ord("N")]:
            if self.queue:
                next_song = self.queue.pop(0)
                self.play_track(next_song)
            else:
                self.set_status("Antrean lagu kosong. Tekan [a] untuk menambahkan lagu.")

        elif key in [ord("p"), ord("P")]:
            if self.history:
                prev_song = self.history.pop()
                self.play_track(prev_song)
            elif self.mpv.is_playing:
                self.mpv.seek(-9999) # Ulangi dari detik 0
                self.set_status("Mengulang lagu dari awal.")
            else:
                self.set_status("Riwayat lagu kosong.")

        # Repeat Mode Toggle
        elif key in [ord("r"), ord("R")]:
            modes = ["off", "single"]
            curr_idx = modes.index(self.mpv.loop_mode)
            self.mpv.loop_mode = modes[(curr_idx + 1) % len(modes)]
            self.set_status(f"󰑖 Mode Ulang: {self.mpv.loop_mode.upper()}")

    def _draw_box(self, y: int, x: int, h: int, w: int, title: str, color_pair: int):
        """Menggambar frame dengan sudut membulat khas ricing."""
        if h < 2 or w < 2:
            return
        attr = curses.color_pair(color_pair)
        try:
            self.stdscr.addstr(y, x, "╭" + "─" * (w - 2) + "╮", attr)
            for row in range(y + 1, y + h - 1):
                self.stdscr.addstr(row, x, "│", attr)
                self.stdscr.addstr(row, x + w - 1, "│", attr)
            self.stdscr.addstr(y + h - 1, x, "╰" + "─" * (w - 2) + "╯", attr)
            if title:
                t_str = f" {title} "[:w - 4]
                self.stdscr.addstr(y, x + 2, t_str, curses.color_pair(1) | curses.A_BOLD)
        except curses.error:
            pass

    def _draw(self):
        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()

        if h < 18 or w < 64:
            msg = "Terminal terlalu kecil! Harap perbesar ukuran jendela terminal."
            try:
                self.stdscr.addstr(h // 2, max(0, (w - len(msg)) // 2), msg, curses.color_pair(5) | curses.A_BOLD)
            except curses.error:
                pass
            self.stdscr.refresh()
            return

        # Jika mode Bantuan aktif, tampilkan tampilan Bantuan penuh
        if self.view_mode == "HELP":
            self._draw_help_screen(h, w)
            self.stdscr.refresh()
            return

        # 1. Header Bar dengan branding "by ArioDev7"
        header_title = " 󰎆  YOUTUBE MUSIC TUI  •  by ArioDev7  •  CATPPUCCIN MOCHA "
        self._draw_box(0, 0, 3, w, "", 6)
        try:
            self.stdscr.addstr(1, 2, header_title, curses.color_pair(1) | curses.A_BOLD)
            active_info = f"[Tab] TAB: {self.active_tab} ({len(self._get_active_list())} lagu)  •  [?] BANTUAN "
            self.stdscr.addstr(1, max(2, w - len(active_info) - 2), active_info, curses.color_pair(2) | curses.A_BOLD)
        except curses.error:
            pass

        # Tata letak split panel
        main_top = 3
        bottom_h = 3
        main_h = h - main_top - bottom_h
        
        split_x = int(w * 0.58)
        left_w = split_x
        right_w = w - split_x

        # 2. Panel Kiri: Hasil Pencarian / Antrean
        list_title = f"󰠃 Hasil: '{self.query[:16]}' [ / Cari ]" if self.active_tab == "SEARCH" else "󰒮 Antrean Lagu (Queue)"
        self._draw_box(main_top, 0, main_h, left_w, list_title, 6)
        self._draw_track_list(main_top + 1, 1, main_h - 2, left_w - 2)

        # 3. Panel Kanan: Player Card & Animated Equalizer
        self._draw_box(main_top, split_x, main_h, right_w, "󰋋 Sedang Diputar", 6)
        self._draw_player_card(main_top + 1, split_x + 1, main_h - 2, right_w - 2)

        # 4. Footer Bar: Status / Baris Input Pencarian
        foot_y = h - bottom_h
        self._draw_box(foot_y, 0, bottom_h, w, "", 6)

        try:
            if self.search_active:
                # Baris input pencarian langsung di footer
                typed = "".join(self.search_input)
                prompt_text = f" 󰠃 CARI YOUTUBE: > {typed}█"
                hint_text = "[Enter] Cari  •  [Esc] Batal "
                self.stdscr.addstr(foot_y + 1, 2, prompt_text[:w - len(hint_text) - 4], curses.color_pair(3) | curses.A_BOLD)
                if w > len(hint_text) + 20:
                    self.stdscr.addstr(foot_y + 1, w - len(hint_text) - 2, hint_text, curses.color_pair(4) | curses.A_BOLD)
            else:
                # Baris status biasa & tombol bantuan
                status_text = f" {self.status_message}"[:w - 40]
                shortcuts = "[?] Bantuan  [/] Cari  [Spasi] Jeda  [Enter] Putar  [a] Antre  [q] Keluar"
                self.stdscr.addstr(foot_y + 1, 2, status_text, curses.color_pair(4) | curses.A_BOLD)
                if w > len(shortcuts) + len(status_text) + 4:
                    self.stdscr.addstr(foot_y + 1, w - len(shortcuts) - 2, shortcuts, curses.color_pair(7))
        except curses.error:
            pass

        self.stdscr.refresh()

    def _draw_track_list(self, y: int, x: int, h: int, w: int):
        items = self._get_active_list()
        if self.is_searching:
            spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            spin = spinner_chars[int(time.time() * 8) % len(spinner_chars)]
            msg = f"{spin} Sedang mencari '{self.query}' di YouTube..."
            try:
                self.stdscr.addstr(y + 2, x + 2, msg[:w - 4], curses.color_pair(2) | curses.A_BOLD)
            except curses.error:
                pass
            return

        if not items:
            msg = "Tidak ada lagu. Tekan [/] untuk mulai mencari!" if self.active_tab == "SEARCH" else "Antrean kosong. Tekan [a] pada hasil cari untuk menambah lagu."
            try:
                self.stdscr.addstr(y + 2, x + 2, msg[:w - 4], curses.color_pair(7))
            except curses.error:
                pass
            return

        max_visible = h
        start_idx = 0
        if self.selected_idx >= max_visible:
            start_idx = self.selected_idx - max_visible + 1

        for row_i in range(max_visible):
            idx = start_idx + row_i
            if idx >= len(items):
                break

            track = items[idx]
            is_selected = (idx == self.selected_idx)
            is_playing_this = (self.mpv.current_track and self.mpv.current_track.video_id == track.video_id)

            if is_playing_this:
                icon = "󰐊" if not self.mpv.is_paused else "󰏤"
            else:
                icon = f"{idx + 1:02d}"

            dur = track.duration_str
            avail_w = max(10, w - len(dur) - 8)
            title_part = f"{track.title} - {track.artist}"[:avail_w]
            line_str = f" {icon}  {title_part:<{avail_w}} {dur} "[:w]

            try:
                if is_selected:
                    self.stdscr.addstr(y + row_i, x, line_str, curses.color_pair(8) | curses.A_BOLD)
                elif is_playing_this:
                    self.stdscr.addstr(y + row_i, x, line_str, curses.color_pair(3) | curses.A_BOLD)
                else:
                    self.stdscr.addstr(y + row_i, x, line_str, curses.color_pair(7))
            except curses.error:
                pass

    def _draw_player_card(self, y: int, x: int, h: int, w: int):
        track = self.mpv.current_track
        
        if self.mpv.is_playing:
            state_str = "󰏤 DIJEDA" if self.mpv.is_paused else "󰐊 SEDANG MEMUTAR"
            state_color = curses.color_pair(4) if self.mpv.is_paused else curses.color_pair(3)
        else:
            state_str = "󰓛 BERHENTI"
            state_color = curses.color_pair(7)

        try:
            # 1. Status badge
            self.stdscr.addstr(y + 1, x + 2, state_str, state_color | curses.A_BOLD)

            # 2. Judul & Artis
            if track:
                title = track.title[:w - 4]
                artist = f"󰠃 {track.artist}"[:w - 4]
                self.stdscr.addstr(y + 3, x + 2, title, curses.color_pair(1) | curses.A_BOLD)
                self.stdscr.addstr(y + 4, x + 2, artist, curses.color_pair(2))
            else:
                self.stdscr.addstr(y + 3, x + 2, "Pilih lagu dan tekan [Enter]", curses.color_pair(7))
                self.stdscr.addstr(y + 4, x + 2, "untuk mulai streaming audio.", curses.color_pair(7))

            # 3. Waveform Equalizer
            eq_y = y + 7
            if eq_y + 2 < y + h:
                eq_line = ""
                for val in self.eq_heights[:(w - 6) // 2]:
                    eq_line += self.eq_chars[val] + " "
                self.stdscr.addstr(eq_y, x + 2, eq_line[:w - 4], curses.color_pair(2) | curses.A_BOLD)

            # 4. Progress Bar
            cur_sec = self.mpv.time_pos
            tot_sec = self.mpv.duration or (track.duration if track else 0) or 1.0
            fraction = max(0.0, min(1.0, cur_sec / tot_sec))
            
            cur_time_str = self._format_time(cur_sec)
            tot_time_str = self._format_time(tot_sec)
            
            bar_w = max(10, w - len(cur_time_str) - len(tot_time_str) - 8)
            filled_len = int(bar_w * fraction)
            bar = "━" * filled_len + "╸" + "━" * max(0, bar_w - filled_len) if filled_len < bar_w else "━" * bar_w
            
            progress_y = y + 10
            if progress_y < y + h:
                prog_str = f"{cur_time_str} {bar} {tot_time_str}"[:w - 4]
                self.stdscr.addstr(progress_y, x + 2, prog_str, curses.color_pair(1))

            # 5. Volume & Mode Info
            info_y = y + 12
            if info_y < y + h:
                vol_bar_w = 10
                vol_filled = int(vol_bar_w * (self.mpv.volume / 100.0))
                vol_bar = "█" * min(vol_bar_w, vol_filled) + "░" * max(0, vol_bar_w - vol_filled)
                mute_tag = " [MUTED]" if self.mpv.is_muted else ""
                vol_str = f"󰕾 Vol: {self.mpv.volume:3d}% [{vol_bar}]{mute_tag}"
                loop_str = f"󰑖 Ulang: {self.mpv.loop_mode.upper()}  •  by ArioDev7"
                self.stdscr.addstr(info_y, x + 2, vol_str[:w - 4], curses.color_pair(3))
                if info_y + 1 < y + h:
                    self.stdscr.addstr(info_y + 1, x + 2, loop_str[:w - 4], curses.color_pair(4))

        except curses.error:
            pass

    def _draw_help_screen(self, h: int, w: int):
        """Menggambar layar penuh panduan keybindings yang bersih dan terstruktur."""
        box_w = min(74, w - 2)
        box_h = min(24, h - 2)
        start_y = max(1, (h - box_h) // 2)
        start_x = max(1, (w - box_w) // 2)

        self._draw_box(start_y, start_x, box_h, box_w, "󰋖 PANDUAN KEYBINDINGS • by ArioDev7", 6)

        categories = [
            ("󰎆 NAVIGASI & PEMUTARAN", [
                ("k / ↑, j / ↓", "Geser pilihan baris lagu (Vim keys)"),
                ("Enter", "Putar lagu yang sedang disorot"),
                ("Spasi", "Jeda / Lanjutkan (Play / Pause)"),
                ("a", "Tambahkan lagu ke Antrean (Queue)"),
                ("Tab", "Beralih tab (Hasil Cari <-> Antrean)"),
                ("d / x", "Hapus lagu dari antrean"),
                ("c", "Bersihkan seluruh isi antrean"),
                ("n / p", "Lagu berikutnya (Next) / Lagu sebelumnya (Prev)"),
                ("r", "Mode ulang lagu (Off / Single Track)"),
            ]),
            ("󰕾 KONTROL AUDIO & DURASI", [
                ("+ / =", "Naikkan volume (+5%)"),
                ("- / _", "Turunkan volume (-5%)"),
                ("m", "Bisukan suara (Mute toggle)"),
                ("→ / ←", "Geser durasi maju / mundur 10 detik"),
            ]),
            ("󰠃 PENCARIAN & SISTEM", [
                ("/ atau s", "Buka dialog pencarian YouTube"),
                ("? atau h", "Buka / Tutup panduan keybindings ini"),
                ("q", "Keluar dari YouTube Music TUI"),
            ]),
        ]

        try:
            cur_y = start_y + 2
            for cat_title, items in categories:
                if cur_y >= start_y + box_h - 4:
                    break
                self.stdscr.addstr(cur_y, start_x + 3, cat_title, curses.color_pair(2) | curses.A_BOLD)
                cur_y += 1
                for key_lbl, desc in items:
                    if cur_y >= start_y + box_h - 3:
                        break
                    self.stdscr.addstr(cur_y, start_x + 5, f"{key_lbl:<14}", curses.color_pair(3) | curses.A_BOLD)
                    self.stdscr.addstr(cur_y, start_x + 20, f": {desc}"[:box_w - 22], curses.color_pair(7))
                    cur_y += 1
                cur_y += 1

            bottom_hint = "[ Tekan sembarang tombol / Esc untuk kembali ke Pemutar ]"
            self.stdscr.addstr(start_y + box_h - 2, max(start_x + 2, start_x + (box_w - len(bottom_hint)) // 2),
                               bottom_hint, curses.color_pair(4) | curses.A_BOLD)
        except curses.error:
            pass

    def _render_missing_mpv(self):
        """Dialog bantuan jika MPV belum terpasang."""
        curses.curs_set(0)
        while True:
            self.stdscr.erase()
            h, w = self.stdscr.getmaxyx()
            box_w = min(68, w - 4)
            box_h = 11
            y = max(1, (h - box_h) // 2)
            x = max(1, (w - box_w) // 2)

            self._draw_box(y, x, box_h, box_w, "󰅚 Dependensi Diperlukan", 5)
            try:
                self.stdscr.addstr(y + 2, x + 3, "Aplikasi ini membutuhkan 'mpv' untuk streaming audio YouTube.", curses.color_pair(7) | curses.A_BOLD)
                self.stdscr.addstr(y + 4, x + 3, "Buka terminal Anda dan jalankan perintah berikut:", curses.color_pair(7))
                cmd_hint = "sudo apt install -y mpv mpv-mpris"
                self.stdscr.addstr(y + 5, x + 5, f"> {cmd_hint}", curses.color_pair(3) | curses.A_BOLD)
                self.stdscr.addstr(y + 7, x + 3, "Paket 'mpv-mpris' juga otomatis menghubungkannya ke Polybar / playerctl!", curses.color_pair(2))
                self.stdscr.addstr(y + 9, x + 3, "Tekan [q] untuk keluar.", curses.color_pair(4) | curses.A_BOLD)
            except curses.error:
                pass
            self.stdscr.refresh()

            ch = self.stdscr.getch()
            if ch in [ord("q"), ord("Q"), 27]:
                break
            time.sleep(0.1)

def main():
    curses.wrapper(lambda scr: YoutubeMusicTUI(scr).run())

if __name__ == "__main__":
    main()
