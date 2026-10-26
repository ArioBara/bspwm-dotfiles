#!/usr/bin/env python3
"""
Desktop Right-Click Context Menu for BSPWM
Author: ArioDev7
Catppuccin Mocha themed desktop context menu triggered by right-clicking on the wallpaper.
"""

import os
import sys
import subprocess
import signal
import time
import fcntl
import re

PID_FILE = "/tmp/desktop_menu.pid"
LOG_FILE = "/tmp/desktop_menu.log"
SCRIPT_PATH = os.path.realpath(__file__)

MENU_ITEMS = [
    # (Label, Command list or None for separator)
    ("󰞷  Buka Terminal (Kitty)", ["kitty"]),
    ("  File Manager (Ranger)", ["kitty", "--class", "ranger-term", "-T", " Ranger File Manager", "-e", "ranger"]),
    ("  Web Browser (Chromium)", ["chromium"]),
    ("  Cari Aplikasi (Rofi)", ["bash", os.path.expanduser("~/.config/rofi/launcher.sh")]),
    ("── ──────────────────────────", None),
    ("🍈  Guava Ricing Toolbox", ["kitty", "--class", "guava-term", "-T", "🍈 Guava Toolbox", "-e", "guava"]),
    ("🎵  YouTube Music (TUI)", ["kitty", "--class", "ytmusic-term", "-T", "🎵 YouTube Music", "-e", "ytmusic"]),
    ("🌐  NetMon Network Monitor", ["kitty", "--class", "netmon-term", "-T", "Mesh & Honcho Monitor • by ArioDev7", "-e", "netmon"]),
    ("⚙️  Autostart Manager", ["kitty", "--class", "autostart-term", "-T", "⚙️ Autostart Manager", "-e", os.path.expanduser("~/.local/bin/autostart-manager")]),
    ("🐳  Dockman (Docker Manager)", ["kitty", "--class", "dockman-term", "-T", "🐳 Docker TUI Manager", "-e", os.path.expanduser("~/.local/bin/dockman")]),
    ("󰊢  Gitman (Git Dashboard)", ["kitty", "--class", "gitman-term", "-T", "󰊢 Git Project Dashboard", "-e", os.path.expanduser("~/.local/bin/gitman")]),
    ("🧹  System Cleaner", ["kitty", "--class", "cleaner-term", "-T", "🧹 System Cleaner", "-e", os.path.expanduser("~/.local/bin/system-cleaner")]),
    ("📋  ClipVault (Clipboard)", ["kitty", "--class", "clipvault-term", "-T", "📋 ClipVault Manager", "-e", os.path.expanduser("~/.local/bin/clipvault")]),
    ("📝  QuickNote (Catatan)", ["kitty", "--class", "quicknote-term", "-T", "📝 QuickNote Scratchpad", "-e", os.path.expanduser("~/.local/bin/quicknote")]),
    ("🎯  App Sniper (Process Killer)", ["kitty", "--class", "sniper-term", "-T", "🎯 App Sniper Process Killer", "-e", os.path.expanduser("~/.local/bin/app-sniper")]),
    ("🎨  Palette Forge (Color Tools)", ["kitty", "--class", "palette-term", "-T", "🎨 Palette Forge", "-e", os.path.expanduser("~/.local/bin/palette-forge")]),
    ("📡  NetScout (Network Tools)", ["kitty", "--class", "netscout-term", "-T", "📡 NetScout Network Tools", "-e", os.path.expanduser("~/.local/bin/netscout")]),
    ("── ──────────────────────────", None),
    ("󰏘  Tema & Ricing Switcher", ["bash", os.path.expanduser("~/.config/bspwm/scripts/theme_switcher.sh")]),
    ("🖼️  Ganti Wallpaper (Acak)", ["bash", os.path.expanduser("~/.config/bspwm/scripts/set_wallpaper.sh"), "random"]),
    ("🔄  Restart BSPWM (Refresh)", ["bspc", "wm", "-r"]),
    ("  Shortcut Cheatsheet", ["bash", os.path.expanduser("~/.config/bspwm/scripts/shortcut_rofi.sh")]),
    ("🎥  Screen Recorder (SSR)", ["simplescreenrecorder"]),
    ("── ──────────────────────────", None),
    ("  Power Menu", ["bash", os.path.expanduser("~/.config/rofi/powermenu.sh")]),
]


def is_desktop_click(root):
    """
    Check if the click coordinate is truly empty desktop wallpaper:
    1. bspc pointed.window is empty (no managed tiled/floating window).
    2. Window under pointer is not polybar or dunst.
    """
    try:
        res = subprocess.run(
            ["bspc", "query", "-N", "-n", "pointed.window"],
            capture_output=True,
            text=True,
            timeout=0.15
        )
        if res.returncode == 0 and res.stdout.strip():
            return False
    except Exception:
        pass

    try:
        pointer = root.query_pointer()
        child = pointer.child
        if child and getattr(child, "id", 0) != 0:
            cls = child.get_wm_class()
            if cls:
                name, cl = cls
                lower_name = name.lower()
                lower_cl = cl.lower()
                if any(k in lower_name or k in lower_cl for k in ["polybar", "dunst", "panel", "dock"]):
                    return False
    except Exception:
        pass

    return True


def show_menu():
    """Display the Rofi context menu at mouse position using native -m -3 flag."""
    theme_path = os.path.expanduser("~/.config/rofi/desktopmenu.rasi")
    menu_text = "\n".join(item[0] for item in MENU_ITEMS)

    # -m -3: Native Rofi flag that places menu right at the cursor and handles clamping
    # -format i: Returns exact 0-based selected index to prevent any string/whitespace mismatch
    rofi_cmd = [
        "rofi",
        "-dmenu",
        "-format", "i",
        "-p", "󰍜 Desktop",
        "-theme", theme_path,
        "-m", "-3"
    ]

    try:
        proc = subprocess.run(
            rofi_cmd,
            input=menu_text,
            capture_output=True,
            text=True
        )
        if proc.returncode != 0:
            return

        chosen_str = proc.stdout.strip()
        if not chosen_str.isdigit():
            return

        idx = int(chosen_str)
        if 0 <= idx < len(MENU_ITEMS):
            label, cmd = MENU_ITEMS[idx]
            if cmd:
                # Sleep briefly to ensure rofi has unmapped and released X11 keyboard/pointer grabs
                time.sleep(0.2)
                subprocess.Popen(cmd, start_new_session=True)
    except Exception as e:
        print(f"Error launching menu: {e}", file=sys.stderr)


def run_daemon(foreground=False):
    """Background listener for X11 Button3 (right-click) on root window."""
    try:
        from Xlib import X, display
    except ImportError:
        print("Error: python3-xlib is required for daemon mode.", file=sys.stderr)
        sys.exit(1)

    if not foreground:
        # Standard double-fork to detach cleanly from parent shell
        if os.fork() > 0:
            sys.exit(0)
        os.setsid()
        if os.fork() > 0:
            sys.exit(0)

        # Redirect standard file descriptors so daemon is fully detached
        sys.stdout.flush()
        sys.stderr.flush()
        with open("/dev/null", "rb", 0) as devnull:
            os.dup2(devnull.fileno(), sys.stdin.fileno())
        with open(LOG_FILE, "ab", 0) as log:
            os.dup2(log.fileno(), sys.stdout.fileno())
            os.dup2(log.fileno(), sys.stderr.fileno())

    # Ignore SIGHUP so daemon survives terminal closure
    signal.signal(signal.SIGHUP, signal.SIG_IGN)

    # File locking to strictly ensure only ONE daemon instance runs
    try:
        lock_fd = open(PID_FILE, "w")
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fd.write(str(os.getpid()))
        lock_fd.flush()
    except (BlockingIOError, OSError):
        print(f"Desktop menu daemon is already running. Exiting.")
        sys.exit(0)

    def cleanup(*args):
        try:
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
        except OSError:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    d = display.Display()
    root = d.screen().root

    # Grab Button 3 (Right Click) synchronously on the root window
    root.grab_button(
        3,
        X.AnyModifier,
        False,
        X.ButtonPressMask,
        X.GrabModeSync,
        X.GrabModeSync,
        X.NONE,
        X.NONE
    )
    d.sync()

    try:
        while True:
            ev = d.next_event()
            if ev.type != X.ButtonPress:
                continue

            if ev.detail != 3:
                # Not button 3: replay immediately
                d.allow_events(X.ReplayPointer, ev.time)
                d.flush()
                continue

            if is_desktop_click(root):
                # Desktop click: CONSUME EVENT (AsyncPointer unfreezes pointer without replay)
                d.allow_events(X.AsyncPointer, ev.time)
                d.flush()

                # Launch menu asynchronously
                subprocess.Popen(
                    [sys.executable, SCRIPT_PATH, "--menu"],
                    start_new_session=True
                )
            else:
                # Click was on an application window or bar: PASS-THROUGH (ReplayPointer)
                d.allow_events(X.ReplayPointer, ev.time)
                d.flush()
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"Daemon error: {e}\n")
    finally:
        try:
            root.ungrab_button(3, X.AnyModifier)
            d.sync()
        except Exception:
            pass
        cleanup()


def kill_daemon():
    """Stop any currently running daemon instance."""
    pids_killed = False
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, signal.SIGTERM)
            pids_killed = True
        except Exception:
            pass
        try:
            os.remove(PID_FILE)
        except OSError:
            pass

    # Also kill any leftover processes matching desktop_menu
    res = subprocess.run(["pkill", "-f", "desktop_menu.py.*--daemon"], capture_output=True)
    if res.returncode == 0 or pids_killed:
        print("Desktop menu daemon stopped.")
    else:
        print("No running desktop menu daemon found.")


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--daemon":
            run_daemon(foreground=False)
        elif arg == "--foreground":
            run_daemon(foreground=True)
        elif arg == "--kill":
            kill_daemon()
        elif arg == "--menu":
            show_menu()
        elif arg == "--status":
            if os.path.exists(PID_FILE):
                try:
                    with open(PID_FILE) as f:
                        pid = int(f.read().strip())
                    os.kill(pid, 0)
                    print(f"Daemon is running (PID {pid})")
                    return
                except OSError:
                    pass
            print("Daemon is not running.")
        elif arg in ("-h", "--help"):
            print("Usage: desktop_menu.py [--daemon | --foreground | --menu | --kill | --status]")
        else:
            show_menu()
    else:
        show_menu()


if __name__ == "__main__":
    main()
