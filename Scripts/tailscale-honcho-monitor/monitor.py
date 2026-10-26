#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tailscale & Honcho Network Monitor (Ricing Edition)
Theme: Catppuccin Mocha
Designed for BSPWM, Kitty, and Linux Ricing enthusiasts.
Author: ArioDev7 & Antigravity
"""

import os
import sys
import time
import json
import curses
import socket
import datetime
import threading
import subprocess
import urllib.request
import urllib.error
from typing import Dict, List, Any, Optional

# Configuration Defaults
DEFAULT_HONCHO_URL = os.environ.get("HONCHO_API_URL", "http://vmi3356393:8001")
HONCHO_WORKSPACE = os.environ.get("HONCHO_WORKSPACE_ID", "hermes")
POLL_INTERVAL_SECS = 4.0

class DataFetcher:
    """Asynchronous background data collector for Tailscale and Honcho."""
    def __init__(self, honcho_url: str, workspace_id: str):
        self.honcho_url = honcho_url.rstrip("/")
        self.workspace_id = workspace_id
        
        self.lock = threading.Lock()
        self.running = True
        self.last_update = 0.0
        self.refresh_event = threading.Event()
        
        # Tailscale Data
        self.ts_online = False
        self.ts_self: Dict[str, Any] = {}
        self.ts_peers: List[Dict[str, Any]] = []
        self.ts_error: Optional[str] = None
        self.ts_peer_latencies: Dict[str, float] = {}
        
        # Honcho Data
        self.honcho_online = False
        self.honcho_latency_ms = 0.0
        self.honcho_error: Optional[str] = None
        self.honcho_workspaces: List[Dict[str, Any]] = []
        self.honcho_peers: List[Dict[str, Any]] = []
        self.honcho_queue: Dict[str, Any] = {}
        
        # Start worker thread
        self.thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.thread.start()

    def trigger_refresh(self):
        self.refresh_event.set()

    def _worker_loop(self):
        while self.running:
            self._fetch_tailscale()
            self._fetch_honcho()
            with self.lock:
                self.last_update = time.time()
            
            # Wait for interval or explicit trigger
            self.refresh_event.wait(timeout=POLL_INTERVAL_SECS)
            self.refresh_event.clear()

    def _fetch_tailscale(self):
        try:
            res = subprocess.run(
                ["tailscale", "status", "--json"],
                capture_output=True,
                text=True,
                timeout=3.0
            )
            if res.returncode == 0:
                data = json.loads(res.stdout)
                self_node = data.get("Self", {})
                peer_map = data.get("Peer", {})
                
                peers_list = []
                # Pinned entry: Perangkat Lokal Ini (Self Node)
                if self_node:
                    self_entry = dict(self_node)
                    self_entry["is_self"] = True
                    self_entry["Online"] = bool(self_node.get("Online", True))
                    self_entry["Relay"] = "Local (self)"
                    peers_list.append(self_entry)

                remote_peers = []
                for _, pinfo in peer_map.items():
                    remote_peers.append(pinfo)
                
                # Sort remote peers: online first, then by HostName
                remote_peers.sort(key=lambda x: (not x.get("Online", False), x.get("HostName", "").lower()))
                peers_list.extend(remote_peers)
                
                with self.lock:
                    self.ts_online = bool(self_node.get("Online", False))
                    self.ts_self = self_node
                    self.ts_peers = peers_list
                    self.ts_error = None
            else:
                with self.lock:
                    self.ts_online = False
                    self.ts_error = f"Tailscale error: code {res.returncode}"
        except Exception as e:
            with self.lock:
                self.ts_online = False
                self.ts_error = str(e)

        # Quick latency probe for online peers
        current_peers = []
        with self.lock:
            current_peers = [p for p in self.ts_peers if p.get("Online")]
        
        for p in current_peers[:6]: # Limit concurrent checks
            ips = p.get("TailscaleIPs", [])
            if ips:
                ip = ips[0]
                lat = self.ping_peer(ip, count=1, timeout_secs=1)
                if lat is not None:
                    with self.lock:
                        self.ts_peer_latencies[ip] = lat

    def ping_peer(self, ip: str, count: int = 1, timeout_secs: int = 1) -> Optional[float]:
        try:
            proc = subprocess.run(
                ["ping", "-c", str(count), "-W", str(timeout_secs), ip],
                capture_output=True,
                text=True,
                timeout=timeout_secs + 1.0
            )
            if proc.returncode == 0:
                for line in proc.stdout.splitlines():
                    if "min/avg/max" in line or "rtt" in line:
                        parts = line.split("=")[1].strip().split("/")
                        return float(parts[1])
        except Exception:
            pass
        return None

    def _fetch_honcho(self):
        # 1. Health check & Latency
        t0 = time.perf_counter()
        health_ok = False
        try:
            req = urllib.request.Request(
                f"{self.honcho_url}/health",
                headers={"User-Agent": "Netmon-Ricing/1.0"}
            )
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                if resp.status == 200:
                    health_ok = True
            lat = (time.perf_counter() - t0) * 1000.0
            with self.lock:
                self.honcho_online = health_ok
                self.honcho_latency_ms = lat
                self.honcho_error = None
        except Exception as e:
            with self.lock:
                self.honcho_online = False
                self.honcho_latency_ms = 0.0
                self.honcho_error = str(e)
            return

        # 2. Workspaces List
        try:
            req_ws = urllib.request.Request(
                f"{self.honcho_url}/v3/workspaces/list",
                data=b"{}",
                headers={"Content-Type": "application/json", "User-Agent": "Netmon-Ricing/1.0"},
                method="POST"
            )
            with urllib.request.urlopen(req_ws, timeout=2.5) as resp:
                ws_data = json.loads(resp.read().decode())
                with self.lock:
                    self.honcho_workspaces = ws_data.get("items", [])
        except Exception:
            pass

        # 3. Peers in Workspace
        try:
            req_p = urllib.request.Request(
                f"{self.honcho_url}/v3/workspaces/{self.workspace_id}/peers/list",
                data=b"{}",
                headers={"Content-Type": "application/json", "User-Agent": "Netmon-Ricing/1.0"},
                method="POST"
            )
            with urllib.request.urlopen(req_p, timeout=2.5) as resp:
                p_data = json.loads(resp.read().decode())
                with self.lock:
                    self.honcho_peers = p_data.get("items", [])
        except Exception:
            pass

        # 4. Queue Status
        try:
            req_q = urllib.request.Request(
                f"{self.honcho_url}/v3/workspaces/{self.workspace_id}/queue/status",
                headers={"User-Agent": "Netmon-Ricing/1.0"}
            )
            with urllib.request.urlopen(req_q, timeout=2.5) as resp:
                q_data = json.loads(resp.read().decode())
                with self.lock:
                    self.honcho_queue = q_data
        except Exception:
            pass

    def get_snapshot(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "ts_online": self.ts_online,
                "ts_self": dict(self.ts_self),
                "ts_peers": list(self.ts_peers),
                "ts_error": self.ts_error,
                "ts_peer_latencies": dict(self.ts_peer_latencies),
                "honcho_online": self.honcho_online,
                "honcho_latency_ms": self.honcho_latency_ms,
                "honcho_error": self.honcho_error,
                "honcho_workspaces": list(self.honcho_workspaces),
                "honcho_peers": list(self.honcho_peers),
                "honcho_queue": dict(self.honcho_queue),
                "last_update": self.last_update,
            }

    def stop(self):
        self.running = False
        self.refresh_event.set()


class NetmonTUI:
    """TUI Application for Tailscale and Honcho monitoring with Catppuccin Mocha theme."""
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.running = True
        
        # State
        self.active_tab = "OVERVIEW"  # "OVERVIEW", "PEERS", "HONCHO"
        self.tabs = ["OVERVIEW", "PEERS", "HONCHO"]
        self.tab_labels = {
            "OVERVIEW": "1. 󰒍 OVERVIEW & TOPOLOGY",
            "PEERS": "2. 󰛳 TAILSCALE PEERS",
            "HONCHO": "3. 󰌘 HONCHO MEMORY",
        }
        self.selected_idx = 0
        self.view_mode = "MAIN" # "MAIN", "HELP"
        self.status_message = "Siap memonitor jaringan..."
        self.status_time = time.time()
        
        # Animation
        self.pulse_frame = 0
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.wave_chars = [" ", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃"]
        self.wave_offset = 0

        # Background fetcher
        self.fetcher = DataFetcher(DEFAULT_HONCHO_URL, HONCHO_WORKSPACE)
        
        self._init_curses()

    def _init_curses(self):
        curses.start_color()
        curses.use_default_colors()
        curses.noecho()
        curses.raw()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)
        self._set_cursor(0)

        # Catppuccin Mocha Color Palette
        # Pair 1: Mauve / Magenta (#cba6f7)
        # Pair 2: Teal / Cyan (#94e2d5)
        # Pair 3: Green (#a6e3a1)
        # Pair 4: Peach / Yellow (#fab387)
        # Pair 5: Red (#f38ba8)
        # Pair 6: Sapphire / Blue (#89b4fa)
        # Pair 7: Text / White (#cdd6f4)
        # Pair 8: Selected highlight (Black on Mauve)
        # Pair 9: Secondary highlight (Black on Teal)
        curses.init_pair(1, curses.COLOR_MAGENTA, -1)
        curses.init_pair(2, curses.COLOR_CYAN, -1)
        curses.init_pair(3, curses.COLOR_GREEN, -1)
        curses.init_pair(4, curses.COLOR_YELLOW, -1)
        curses.init_pair(5, curses.COLOR_RED, -1)
        curses.init_pair(6, curses.COLOR_BLUE, -1)
        curses.init_pair(7, curses.COLOR_WHITE, -1)
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
        curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_CYAN)

    def _set_cursor(self, val: int):
        try:
            curses.curs_set(val)
        except Exception:
            pass

    def set_status(self, msg: str):
        self.status_message = msg
        self.status_time = time.time()

    def _draw_box(self, y: int, x: int, h: int, w: int, title: str = "", color_pair: int = 6):
        """Draw aesthetic rounded box."""
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
                t_str = f" {title} "[:max(0, w - 4)]
                self.stdscr.addstr(y, x + 2, t_str, curses.color_pair(1) | curses.A_BOLD)
        except curses.error:
            pass

    def _format_os_icon(self, os_name: str) -> str:
        os_lower = os_name.lower()
        if "linux" in os_lower:
            return "󰌽 Linux"
        elif "windows" in os_lower:
            return "󰍲 Windows"
        elif "android" in os_lower:
            return "󰀲 Android"
        elif "darwin" in os_lower or "macos" in os_lower or "ios" in os_lower:
            return "󰀵 Apple"
        return f"󰌘 {os_name}"

    def run(self):
        try:
            while self.running:
                self._update_animation()
                self._draw()
                self._handle_input()
                time.sleep(0.06)
        finally:
            self.fetcher.stop()

    def _update_animation(self):
        self.pulse_frame = (self.pulse_frame + 1) % len(self.spinner_chars)
        self.wave_offset = (self.wave_offset + 1) % len(self.wave_chars)

    def _handle_input(self):
        try:
            key = self.stdscr.getch()
        except Exception:
            return

        if key == -1:
            return

        # Help modal toggle
        if self.view_mode == "HELP":
            if key in [ord("?"), ord("h"), ord("H"), 27, 10, 13, ord("q"), ord("Q")]:
                self.view_mode = "MAIN"
                self.set_status("Kembali ke dashboard monitor.")
            return

        if key in [ord("q"), ord("Q"), 27]:
            self.running = False

        elif key in [ord("?"), ord("h"), ord("H"), curses.KEY_F1]:
            self.view_mode = "HELP"

        # Tab Switching
        elif key in [9]:  # Tab key
            curr = self.tabs.index(self.active_tab)
            self.active_tab = self.tabs[(curr + 1) % len(self.tabs)]
            self.selected_idx = 0
            self.set_status(f"Beralih ke tab: {self.active_tab}")

        elif key == ord("1"):
            self.active_tab = "OVERVIEW"
            self.selected_idx = 0
        elif key == ord("2"):
            self.active_tab = "PEERS"
            self.selected_idx = 0
        elif key == ord("3"):
            self.active_tab = "HONCHO"
            self.selected_idx = 0

        # Refresh
        elif key in [ord("r"), ord("R")]:
            self.fetcher.trigger_refresh()
            self.set_status("󰑓 Memperbarui data jaringan & Honcho...")

        # Navigation in Peers / Honcho
        elif key in [curses.KEY_UP, ord("k"), ord("K")]:
            if self.selected_idx > 0:
                self.selected_idx -= 1

        elif key in [curses.KEY_DOWN, ord("j"), ord("J")]:
            data = self.fetcher.get_snapshot()
            max_len = len(data["ts_peers"]) if self.active_tab == "PEERS" else len(data["honcho_peers"])
            if self.selected_idx < max_len - 1:
                self.selected_idx += 1

        # Ping Action in Peers view
        elif key in [ord("p"), ord("P")]:
            data = self.fetcher.get_snapshot()
            peers = data["ts_peers"]
            if 0 <= self.selected_idx < len(peers):
                peer = peers[self.selected_idx]
                name = peer.get("HostName", "peer")
                ips = peer.get("TailscaleIPs", [])
                if peer.get("is_self"):
                    self_ip = ips[0] if ips else "100.87.102.16"
                    self.set_status(f"󰄬 Perangkat lokal Anda ({name} • {self_ip}): loopback 0.0 ms")
                elif ips:
                    ip = ips[0]
                    self.set_status(f"󰖩 Melakukan ping langsung ke {name} ({ip})...")
                    def _do_ping():
                        lat = self.fetcher.ping_peer(ip, count=2, timeout_secs=2)
                        if lat is not None:
                            self.set_status(f"󰄬 Ping {name}: {lat:.1f} ms via WireGuard")
                        else:
                            self.set_status(f"󰅚 Gagal ping {name} (Host offline/timeout)")
                    threading.Thread(target=_do_ping, daemon=True).start()
                else:
                    self.set_status("IP peer tidak ditemukan.")

    def _draw(self):
        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()

        if h < 20 or w < 72:
            msg = "Ukuran terminal terlalu kecil! Harap perbesar (Min: 72x20)."
            try:
                self.stdscr.addstr(h // 2, max(0, (w - len(msg)) // 2), msg, curses.color_pair(5) | curses.A_BOLD)
            except curses.error:
                pass
            self.stdscr.refresh()
            return

        if self.view_mode == "HELP":
            self._draw_help_modal(h, w)
            self.stdscr.refresh()
            return

        data = self.fetcher.get_snapshot()

        # 1. Header Bar
        self._draw_header(w, data)

        # 2. Main Content based on Tab
        main_top = 4
        main_h = h - main_top - 3
        
        if self.active_tab == "OVERVIEW":
            self._draw_overview_tab(main_top, 0, main_h, w, data)
        elif self.active_tab == "PEERS":
            self._draw_peers_tab(main_top, 0, main_h, w, data)
        elif self.active_tab == "HONCHO":
            self._draw_honcho_tab(main_top, 0, main_h, w, data)

        # 3. Footer Bar
        self._draw_footer(h - 3, 0, 3, w, data)
        self.stdscr.refresh()

    def _draw_header(self, w: int, data: Dict[str, Any]):
        """Render top navigation and ricing header."""
        self._draw_box(0, 0, 4, w, "", 6)
        
        # Left Title
        spinner = self.spinner_chars[self.pulse_frame]
        title = f" 󰒍 TAILSCALE WIREMESH & HONCHO MONITOR • Catppuccin Mocha "
        try:
            self.stdscr.addstr(1, 2, title, curses.color_pair(1) | curses.A_BOLD)
            
            # Subtitle / Indicator
            spin_str = f"[{spinner} LIVE]"
            self.stdscr.addstr(1, len(title) + 2, spin_str, curses.color_pair(3) | curses.A_BOLD)

            # Tab Selector on Line 2
            tab_x = 3
            for tab_id in self.tabs:
                lbl = f" {self.tab_labels[tab_id]} "
                if tab_id == self.active_tab:
                    self.stdscr.addstr(2, tab_x, lbl, curses.color_pair(8) | curses.A_BOLD)
                else:
                    self.stdscr.addstr(2, tab_x, lbl, curses.color_pair(7))
                tab_x += len(lbl) + 2

            # Right info (Time + Host)
            now_str = datetime.datetime.now().strftime("%H:%M:%S")
            self_name = data.get("ts_self", {}).get("HostName", "localhost")
            right_info = f"󰌽 {self_name}  •  󰥔 {now_str}  •  [?] BANTUAN "
            self.stdscr.addstr(1, max(2, w - len(right_info) - 3), right_info, curses.color_pair(2))
        except curses.error:
            pass

    def _draw_overview_tab(self, y: int, x: int, h: int, w: int, data: Dict[str, Any]):
        """Render Overview tab with ASCII art topology and status cards."""
        # Top half: ASCII Topology Art Box (height: 12 lines)
        topo_h = min(13, h - 7)
        self._draw_box(y, x, topo_h, w, "󰛳 MESH TOPOLOGY & ACTIVE NODES", 2)

        # ASCII Topology Diagram
        self_node = data.get("ts_self", {})
        self_ip = self_node.get("TailscaleIPs", ["100.87.102.16"])[0]
        self_host = self_node.get("HostName", "ario-bzx")
        
        # Find Hermes and Cloud VPS
        peers_data = data.get("ts_peers", [])
        vps_node = next((p for p in peers_data if "vmi3356393" in p.get("HostName", "").lower()), {})
        vps_ip = vps_node.get("TailscaleIPs", ["100.125.78.92"])[0] if vps_node.get("TailscaleIPs") else "100.125.78.92"
        vps_status = "ONLINE" if vps_node.get("Online", True) else "OFFLINE"

        hermes_node = next((p for p in peers_data if "hermes" in p.get("HostName", "").lower()), {})
        hermes_ip = hermes_node.get("TailscaleIPs", ["100.67.73.15"])[0] if hermes_node.get("TailscaleIPs") else "100.67.73.15"
        hermes_status = "ONLINE" if hermes_node.get("Online") else "STANDBY"

        honcho_lat = f"{data.get('honcho_latency_ms', 0):.0f}ms" if data.get("honcho_online") else "--"

        # Wave effect
        wave_str = ""
        for i in range(min(24, max(5, (w - 55) // 2))):
            idx = (self.wave_offset + i) % len(self.wave_chars)
            wave_str += self.wave_chars[idx]

        diagram_lines = [
            f"  ┌─────────────────────┐                  ╭─────────────────────╮",
            f"  │  󰌽  {self_host:<15} │  ════ {wave_str} ════  │  󰌽  vmi3356393 (VPS) │",
            f"  │  IP: {self_ip:<14} │   Tailscale WireGuard    │  IP: {vps_ip:<15}│",
            f"  │  Status: ● LOCAL    │      Direct ~31ms        │  Status: ● {vps_status:<10}│",
            f"  └──────────┬──────────┘                          └──────────┬──────────┘",
            f"             │                                                │",
            f"             ├─────────────────────┐                          │  HTTP API :8001",
            f"             ▼                     ▼                          ▼",
            f"  ┌─────────────────────┐   ┌───────────────┐      ╭─────────────────────╮",
            f"  │  󰍲  hermes          │   │ 󰀲  I2401      │      │ 󰒍  HONCHO MEMORY    │",
            f"  │  IP: {hermes_ip:<14} │   │ 100.78.69.0   │      │ Workspace: hermes   │",
            f"  │  PC Kantor • {hermes_status:<7}│   │ Phone • ACTIVE│      │ Latency: {honcho_lat:<11}│",
            f"  └─────────────────────┘   └───────────────┘      ╰─────────────────────╯",
        ]

        try:
            for idx, line in enumerate(diagram_lines):
                if y + 1 + idx < y + topo_h - 1:
                    # Highlight colors depending on line
                    col = curses.color_pair(7)
                    if "HONCHO" in line or "Workspace" in line:
                        col = curses.color_pair(3) | curses.A_BOLD if data.get("honcho_online") else curses.color_pair(5)
                    elif "vmi3356393" in line or "VPS" in line:
                        col = curses.color_pair(6) | curses.A_BOLD if vps_status == "ONLINE" else curses.color_pair(5)
                    elif "hermes" in line or "Kantor" in line:
                        col = curses.color_pair(4) | curses.A_BOLD if hermes_status == "ONLINE" else curses.color_pair(5)
                    elif self_host in line or "LOCAL" in line:
                        col = curses.color_pair(1) | curses.A_BOLD
                    elif "WireGuard" in line or "wave" in line:
                        col = curses.color_pair(2)
                    self.stdscr.addstr(y + 1 + idx, x + 2, line[:w - 4], col)
        except curses.error:
            pass

        # Bottom half: 3 Metrics Cards (Tailscale, Honcho, Agents)
        cards_y = y + topo_h
        cards_h = max(6, h - topo_h)
        col_w = w // 3

        # Card 1: Tailscale
        self._draw_box(cards_y, x, cards_h, col_w, "󰒍 TAILSCALE MESH", 6)
        try:
            ts_stat = "● TERHUBUNG" if data.get("ts_online") else "○ TERPUTUS"
            ts_col = curses.color_pair(3) if data.get("ts_online") else curses.color_pair(5)
            peers = data.get("ts_peers", [])
            online_p = sum(1 for p in peers if p.get("Online"))
            
            self.stdscr.addstr(cards_y + 1, x + 2, f"Status  : {ts_stat}", ts_col | curses.A_BOLD)
            self.stdscr.addstr(cards_y + 2, x + 2, f"Device  : {self_host} ({self_ip})", curses.color_pair(7))
            self.stdscr.addstr(cards_y + 3, x + 2, f"Peers   : {online_p}/{len(peers)} Node Online", curses.color_pair(2))
            if cards_h > 5:
                self.stdscr.addstr(cards_y + 4, x + 2, f"Relay   : DERP (sin - Singapore)", curses.color_pair(4))
        except curses.error:
            pass

        # Card 2: Honcho API
        c2_x = x + col_w
        self._draw_box(cards_y, c2_x, cards_h, col_w, "󰌘 HONCHO API SERVER", 3)
        try:
            h_stat = "● AKTIF & MERESPONS" if data.get("honcho_online") else "○ TIDAK TERHUBUNG"
            h_col = curses.color_pair(3) if data.get("honcho_online") else curses.color_pair(5)
            lat_ms = data.get("honcho_latency_ms", 0.0)
            
            self.stdscr.addstr(cards_y + 1, c2_x + 2, f"Layanan : {h_stat}", h_col | curses.A_BOLD)
            self.stdscr.addstr(cards_y + 2, c2_x + 2, f"Host    : {self.fetcher.honcho_url}", curses.color_pair(7))
            self.stdscr.addstr(cards_y + 3, c2_x + 2, f"Latency : {lat_ms:.1f} ms", curses.color_pair(3 if lat_ms < 100 else 4))
            if cards_h > 5:
                q_info = data.get("honcho_queue", {})
                done = q_info.get("completed_work_units", 0)
                tot = q_info.get("total_work_units", 0)
                self.stdscr.addstr(cards_y + 4, c2_x + 2, f"Queue   : {done}/{tot} Deriver Units", curses.color_pair(2))
        except curses.error:
            pass

        # Card 3: Memory & MCP Integration
        c3_x = x + (col_w * 2)
        c3_w = w - (col_w * 2)
        self._draw_box(cards_y, c3_x, cards_h, c3_w, "󰛳 MEMORY & MCP INTEGRATION", 1)
        try:
            ws_list = data.get("honcho_workspaces", [])
            peers_list = data.get("honcho_peers", [])
            ws_name = ws_list[0].get("metadata", {}).get("display_name", "Autopreneur") if ws_list else "hermes"
            
            mcp_bin = os.path.expanduser("~/.local/bin/honcho-mcp")
            mcp_ready = os.path.exists(mcp_bin) and os.access(mcp_bin, os.X_OK)
            mcp_str = "● TERPASANG" if mcp_ready else "○ BELUM DI-SETUP"
            
            self.stdscr.addstr(cards_y + 1, c3_x + 2, f"Workspace : {ws_name} ({len(ws_list)})", curses.color_pair(1) | curses.A_BOLD)
            self.stdscr.addstr(cards_y + 2, c3_x + 2, f"Peers AI  : {len(peers_list)} Terdaftar", curses.color_pair(2))
            self.stdscr.addstr(cards_y + 3, c3_x + 2, f"MCP Server: {mcp_str}", curses.color_pair(3 if mcp_ready else 4))
            if cards_h > 5:
                self.stdscr.addstr(cards_y + 4, c3_x + 2, f"Client    : Antigravity / Claude / Codex", curses.color_pair(7))
        except curses.error:
            pass

    def _draw_peers_tab(self, y: int, x: int, h: int, w: int, data: Dict[str, Any]):
        """Render Tailscale Peers list table."""
        self._draw_box(y, x, h, w, "󰛳 TAILSCALE DEVICES & WIREGUARD PEERS", 2)
        
        peers = data.get("ts_peers", [])
        latencies = data.get("ts_peer_latencies", {})

        # Table Header
        header_y = y + 1
        hdr = f"  {'STATUS':<10} {'HOSTNAME':<18} {'OS':<14} {'IP ADDRESS':<18} {'PING':<10} {'RELAY'}"
        try:
            self.stdscr.addstr(header_y, x + 2, hdr[:w - 4], curses.color_pair(2) | curses.A_BOLD)
            self.stdscr.addstr(header_y + 1, x + 2, "─" * min(len(hdr) + 6, w - 4), curses.color_pair(6))
        except curses.error:
            pass

        row_start_y = header_y + 2
        visible_rows = h - 5

        if not peers:
            try:
                self.stdscr.addstr(row_start_y + 2, x + 4, "Tidak ada peer ditemukan atau Tailscale belum aktif.", curses.color_pair(5))
            except curses.error:
                pass
            return

        for idx, peer in enumerate(peers[:visible_rows]):
            is_selected = (idx == self.selected_idx)
            is_online = peer.get("Online", False)
            is_self = peer.get("is_self", False)
            hostname = peer.get("HostName", "Unknown")
            os_name = self._format_os_icon(peer.get("OS", "linux"))
            ips = peer.get("TailscaleIPs", ["--"])
            ip_str = ips[0] if ips else "--"
            relay = peer.get("Relay", "direct") or "direct"
            
            lat = latencies.get(ip_str)
            
            if is_self:
                disp_host = f"{hostname} (Me)"
                stat_badge = "● (Saya)"
                stat_color = curses.color_pair(1) # Mauve accent
                ping_str = "Local"
                relay = "Local Node"
            else:
                disp_host = hostname
                stat_badge = "● Online" if is_online else "○ Offline"
                stat_color = curses.color_pair(3) if is_online else curses.color_pair(5)
                ping_str = f"{lat:.1f} ms" if lat is not None else ("Active" if is_online else "--")

            line_str = f"  {stat_badge:<10} {disp_host:<18} {os_name:<14} {ip_str:<18} {ping_str:<10} {relay}"
            
            try:
                if is_selected:
                    self.stdscr.addstr(row_start_y + idx, x + 2, line_str[:w - 4], curses.color_pair(8) | curses.A_BOLD)
                else:
                    self.stdscr.addstr(row_start_y + idx, x + 2, line_str[:w - 4], curses.color_pair(7))
                    # Color the status dot specifically
                    dot_pos = x + 4
                    self.stdscr.addstr(row_start_y + idx, dot_pos, stat_badge, stat_color | curses.A_BOLD)
            except curses.error:
                pass

        # Hint at bottom of panel
        try:
            hint = "[ ↑/↓ atau k/j: Navigasi  •  [p]: Ping Langsung ke Node Terpilih ]"
            self.stdscr.addstr(y + h - 2, x + 4, hint, curses.color_pair(4))
        except curses.error:
            pass

    def _draw_honcho_tab(self, y: int, x: int, h: int, w: int, data: Dict[str, Any]):
        """Render Honcho Workspaces, AI Agents, and Queue Details."""
        self._draw_box(y, x, h, w, "󰌘 HONCHO AI MEMORY & WORKSPACE DETAILS", 3)

        ws_list = data.get("honcho_workspaces", [])
        peers = data.get("honcho_peers", [])
        queue = data.get("honcho_queue", {})
        
        left_w = min(46, w // 2)
        right_x = x + left_w + 1
        right_w = w - left_w - 2

        # Left Column: Workspace Profile & Agent Roles
        try:
            self.stdscr.addstr(y + 2, x + 3, "󰋖 INFORMASI WORKSPACE", curses.color_pair(1) | curses.A_BOLD)
            self.stdscr.addstr(y + 3, x + 3, "─" * (left_w - 6), curses.color_pair(6))

            if ws_list:
                ws = ws_list[0]
                meta = ws.get("metadata", {})
                disp_name = meta.get("display_name", ws.get("id"))
                note = meta.get("note", "-")
                created = ws.get("created_at", "-")[:10]
                
                self.stdscr.addstr(y + 4, x + 3, f"ID        : {ws.get('id')}", curses.color_pair(7))
                self.stdscr.addstr(y + 5, x + 3, f"Nama      : {disp_name}", curses.color_pair(3) | curses.A_BOLD)
                self.stdscr.addstr(y + 6, x + 3, f"Catatan   : {note[:left_w - 16]}", curses.color_pair(7))
                self.stdscr.addstr(y + 7, x + 3, f"Dibuat    : {created}", curses.color_pair(4))

                # Agent Setup Breakdown
                agent_setup = meta.get("agent_setup", {}).get("agents", {})
                self.stdscr.addstr(y + 9, x + 3, "󰒍 STRUKTUR AGENT TERCATAT", curses.color_pair(2) | curses.A_BOLD)
                self.stdscr.addstr(y + 10, x + 3, "─" * (left_w - 6), curses.color_pair(6))

                cur_y = y + 11
                for aname, ainfo in list(agent_setup.items())[:max(1, h - 16)]:
                    role = ainfo.get("role", "")
                    model = ainfo.get("model", "")
                    self.stdscr.addstr(cur_y, x + 3, f"• {aname:<12}: {role}", curses.color_pair(7))
                    cur_y += 1
            else:
                self.stdscr.addstr(y + 4, x + 3, "Tidak ada data workspace dari Honcho.", curses.color_pair(5))

            # Queue Progress Box at Bottom of Left Column
            q_y = y + h - 5
            if q_y > y + 12:
                total_u = queue.get("total_work_units", 0)
                comp_u = queue.get("completed_work_units", 0)
                prog = (comp_u / max(1, total_u))
                bar_len = left_w - 18
                filled = int(bar_len * prog)
                bar = "█" * filled + "░" * (bar_len - filled)
                self.stdscr.addstr(q_y, x + 3, f"Deriver Progress ({comp_u}/{total_u}):", curses.color_pair(2))
                self.stdscr.addstr(q_y + 1, x + 3, f"[{bar}] {int(prog * 100)}%", curses.color_pair(3) | curses.A_BOLD)
        except curses.error:
            pass

        # Right Column: Registered Peers List
        try:
            self.stdscr.addstr(y + 2, right_x + 2, f"󰠃 DAFTAR PEERS TERDAFTAR ({len(peers)})", curses.color_pair(1) | curses.A_BOLD)
            self.stdscr.addstr(y + 3, right_x + 2, "─" * (right_w - 4), curses.color_pair(6))

            peer_rows = h - 6
            for idx, p in enumerate(peers[:peer_rows]):
                is_sel = (idx == self.selected_idx)
                pid = p.get("id", "Unknown")
                pdate = p.get("created_at", "-")[:10]
                badge = "󰌘"
                if "claude" in pid:
                    badge = "󰛳"
                elif "orchestrator" in pid:
                    badge = "󰒍"
                elif "shopee" in pid:
                    badge = "󰄬"

                p_str = f" {badge}  {pid:<20}  {pdate}"
                if is_sel:
                    self.stdscr.addstr(y + 4 + idx, right_x + 2, p_str[:right_w - 4], curses.color_pair(8) | curses.A_BOLD)
                else:
                    self.stdscr.addstr(y + 4 + idx, right_x + 2, p_str[:right_w - 4], curses.color_pair(7))
        except curses.error:
            pass

    def _draw_footer(self, y: int, x: int, h: int, w: int, data: Dict[str, Any]):
        """Render bottom status bar and keybindings."""
        self._draw_box(y, x, h, w, "", 6)
        
        # Left status text
        status_txt = f"󰅟 {self.status_message}"
        try:
            self.stdscr.addstr(y + 1, x + 2, status_txt[:w - 42], curses.color_pair(4) | curses.A_BOLD)

            # Right shortcuts
            keys_info = "[Tab] Ganti Tab  •  [r] Refresh  •  [q] Keluar "
            self.stdscr.addstr(y + 1, max(2, w - len(keys_info) - 2), keys_info, curses.color_pair(2))
        except curses.error:
            pass

    def _draw_help_modal(self, h: int, w: int):
        """Render interactive full-screen help modal."""
        box_w = min(68, w - 4)
        box_h = min(18, h - 4)
        start_y = max(1, (h - box_h) // 2)
        start_x = max(1, (w - box_w) // 2)

        self._draw_box(start_y, start_x, box_h, box_w, "󰋖 PANDUAN PINTASAN KEYBINDINGS", 6)

        shortcuts = [
            ("Tab", "Beralih antar tab (Overview <-> Peers <-> Honcho)"),
            ("1, 2, 3", "Langsung lompat ke Tab 1, 2, atau 3"),
            ("k / ↑, j / ↓", "Navigasi baris pada daftar Node/Peers"),
            ("p", "Kirim ping langsung ke node Tailscale yang dipilih"),
            ("r", "Paksa refresh/pembaruan data Tailscale & Honcho"),
            ("?, h, F1", "Buka / Tutup panduan bantuan ini"),
            ("q, Esc", "Keluar dari aplikasi monitoring"),
        ]

        try:
            for idx, (k_lbl, k_desc) in enumerate(shortcuts):
                row_y = start_y + 2 + idx
                if row_y < start_y + box_h - 2:
                    self.stdscr.addstr(row_y, start_x + 4, f"{k_lbl:<12}", curses.color_pair(3) | curses.A_BOLD)
                    self.stdscr.addstr(row_y, start_x + 18, f": {k_desc}"[:box_w - 20], curses.color_pair(7))

            close_hint = "[ Tekan sembarang tombol / Esc untuk kembali ]"
            self.stdscr.addstr(start_y + box_h - 2, start_x + (box_w - len(close_hint)) // 2, close_hint, curses.color_pair(4) | curses.A_BOLD)
        except curses.error:
            pass


def main():
    try:
        curses.wrapper(lambda stdscr: NetmonTUI(stdscr).run())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
