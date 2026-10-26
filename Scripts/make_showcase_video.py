#!/usr/bin/env python3
"""
Automated Ricing Showcase & Video Recorder
Author: ArioDev7
Automates window placements, plays synchronized audio, showcases Neofetch,
Cava, tty-clock, custom TUI tools, Desktop Context Menu, and live theme switching
while recording a crisp 1080p video via SimpleScreenRecorder.
"""

import os
import sys
import time
import subprocess
import wave
import struct
import math
import glob

MUSIC_FILE = "/tmp/showcase_music.wav"
FINAL_VIDEO = os.path.expanduser("~/Videos/ricing_showcase.mp4")


def ensure_picom():
    """Ensure picom compositor is active for rounded corners and shadows."""
    res = subprocess.run(["pgrep", "-x", "picom"], capture_output=True)
    if res.returncode != 0:
        conf = os.path.expanduser("~/.config/picom/picom.conf")
        if os.path.exists(conf):
            subprocess.Popen(["picom", "--config", conf, "-b"])
            time.sleep(0.3)


def generate_music():
    """Synthesize a 45-second energetic synthwave track so CAVA visualizes real music."""
    sample_rate = 44100
    duration = 45.0
    num_samples = int(sample_rate * duration)

    # Chords: C minor, Ab major, Eb major, Bb major, Fm7, G7
    progression = [
        [261.63, 311.13, 392.00, 466.16], # Cm7
        [207.65, 261.63, 311.13, 392.00], # Abmaj7
        [311.13, 392.00, 466.16, 587.33], # Eb
        [233.08, 293.66, 349.23, 466.16], # Bb
        [174.61, 207.65, 261.63, 311.13], # Fm7
        [196.00, 246.94, 293.66, 349.23], # G7
    ]
    chord_len = 3.87 # ~3.87s per chord
    note_len = 0.242 # 16th notes arpeggio (~124 BPM)

    with wave.open(MUSIC_FILE, 'w') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        frames = bytearray()
        for i in range(num_samples):
            t = i / sample_rate

            chord_idx = int(t / chord_len) % len(progression)
            chord = progression[chord_idx]

            arp_idx = int(t / note_len) % len(chord)
            freq = chord[arp_idx]
            bass_freq = chord[0] / 4.0 # Deep warm bass

            # Synth lead with harmonic overtones
            lead = 0.22 * math.sin(2 * math.pi * freq * t) + 0.12 * math.sin(4 * math.pi * freq * t) + 0.06 * math.sin(6 * math.pi * freq * t)
            # Warm sub-bass
            bass = 0.38 * math.sin(2 * math.pi * bass_freq * t)

            # Punchy kick drum every 0.484s (124 BPM)
            t_kick = t % 0.484
            kick = 0.50 * math.sin(2 * math.pi * (120 * math.exp(-20 * t_kick)) * t_kick) * math.exp(-12 * t_kick)

            # Crisp hi-hat every 0.242s
            t_hat = t % 0.242
            hat = 0.09 * (math.sin(2 * math.pi * 8000 * t_hat) + math.sin(2 * math.pi * 12000 * t_hat)) * math.exp(-38 * t_hat)

            val = lead + bass + kick + hat
            val = max(-1.0, min(1.0, val))
            sample = int(val * 32767)
            frames.extend(struct.pack('<hh', sample, sample))

        wav.writeframes(frames)
    print("Synthesized showcase audio track successfully.")


def close_windows(classes):
    """Close windows by class gracefully."""
    for c in classes:
        subprocess.run(["pkill", "-f", c], capture_output=True)


def run_showcase():
    print("=" * 60)
    print("Starting Automated Ricing Showcase Video Recording...")
    print("=" * 60)

    # 0. Compositor check
    ensure_picom()

    # 1. Synthesize soundtrack
    generate_music()

    # 2. Switch to VGA-1 clean workspace 1
    subprocess.run(["bspc", "monitor", "-f", "VGA-1"])
    subprocess.run(["bspc", "desktop", "-f", "1"])
    time.sleep(0.5)

    # Clean existing windows on desktop 1
    close_windows(["kitty", "cava", "tty-clock", "cmatrix"])

    # Record initial files in ~/Videos
    existing_videos = set(glob.glob(os.path.expanduser("~/Videos/*.mp4")))

    # 3. Start SimpleScreenRecorder
    print("Starting screen recording via SimpleScreenRecorder...")
    ssr = subprocess.Popen(
        ["simplescreenrecorder", "--start-recording", "--start-hidden"],
        stdin=subprocess.PIPE,
        text=True
    )
    time.sleep(2.0)

    # 4. Start background music playback
    print("Playing showcase audio track...")
    audio_proc = subprocess.Popen(["paplay", MUSIC_FILE])

    try:
        # --- SCENE 1: Clean Desktop Intro (3.5s) ---
        print("[Scene 1/6] Clean Desktop Intro...")
        subprocess.run(["xdotool", "mousemove", "2326", "540"])
        time.sleep(3.5)

        # --- SCENE 2: Neofetch Kurama Showcase (6.0s) ---
        print("[Scene 2/6] Neofetch Kurama Showcase...")
        subprocess.run(["bspc", "rule", "-a", "Kitty:neofetch-term", "-o", "state=floating", "rectangle=920x560+1866+260"])
        neofetch_proc = subprocess.Popen(
            ["kitty", "--class", "neofetch-term", "-T", "󰄛 System Specs • Neofetch", "-e", "bash", "-c", "neofetch; sleep 8"]
        )
        time.sleep(5.5)
        neofetch_proc.terminate()
        time.sleep(0.5)

        # --- SCENE 3: Audio Visualizer & Neon Clock (7.0s) ---
        print("[Scene 3/6] CAVA Audio Visualizer & Neon Clock...")
        # Clock stacked above CAVA
        subprocess.run(["bspc", "rule", "-a", "Kitty:clock-term", "-o", "state=floating", "rectangle=560x280+2046+140"])
        clock_proc = subprocess.Popen(
            ["kitty", "--class", "clock-term", "-T", "🕒 Neon Clock", "-e", "tty-clock", "-c", "-C", "4", "-B", "-s"]
        )
        time.sleep(0.3)
        # CAVA directly below clock
        subprocess.run(["bspc", "rule", "-a", "Kitty:cava-term", "-o", "state=floating", "rectangle=960x440+1846+460"])
        cava_proc = subprocess.Popen(
            ["kitty", "--class", "cava-term", "-T", "🎵 CAVA Visualizer", "-e", "cava"]
        )
        time.sleep(6.5)
        clock_proc.terminate()
        cava_proc.terminate()
        time.sleep(0.5)

        # --- SCENE 4: TUI Apps & CMatrix Side-by-Side (6.5s) ---
        print("[Scene 4/6] Side-by-Side: Dockman TUI & CMatrix...")
        subprocess.run(["bspc", "rule", "-a", "Kitty:dockman-term", "-o", "state=floating", "rectangle=900x680+1406+160"])
        dockman_proc = subprocess.Popen(
            ["kitty", "--class", "dockman-term", "-T", "🐳 Docker TUI Manager", "-e", os.path.expanduser("~/.local/bin/dockman")]
        )
        time.sleep(0.3)
        subprocess.run(["bspc", "rule", "-a", "Kitty:cmatrix-term", "-o", "state=floating", "rectangle=900x680+2346+160"])
        cmatrix_proc = subprocess.Popen(
            ["kitty", "--class", "cmatrix-term", "-T", "🟩 CMatrix Matrix Rain", "-e", "cmatrix", "-C", "magenta", "-u", "3", "-s"]
        )
        time.sleep(6.0)
        dockman_proc.terminate()
        cmatrix_proc.terminate()
        time.sleep(0.5)

        # --- SCENE 5: Desktop Context Menu (4.5s) ---
        print("[Scene 5/6] Desktop Right-Click Context Menu...")
        subprocess.run(["xdotool", "mousemove", "2326", "500"])
        time.sleep(0.3)
        menu_proc = subprocess.Popen([os.path.expanduser("~/.local/bin/desktop-menu")])
        time.sleep(1.0)
        # Simulate smooth navigation through menu items
        for _ in range(4):
            subprocess.run(["xdotool", "key", "Down"])
            time.sleep(0.4)
        time.sleep(0.6)
        subprocess.run(["xdotool", "key", "Escape"])
        time.sleep(0.5)

        # --- SCENE 6: Live Dynamic Theme Switching (7.5s) ---
        print("[Scene 6/6] Live Theme Transition (Tokyo Night -> Catppuccin)...")
        subprocess.run(["bash", os.path.expanduser("~/.config/bspwm/scripts/theme_switcher.sh"), "tokyo-night"])
        time.sleep(3.5)
        subprocess.run(["bash", os.path.expanduser("~/.config/bspwm/scripts/theme_switcher.sh"), "catppuccin"])
        time.sleep(3.5)

        # --- Outro Clean Desktop (2.5s) ---
        print("Outro...")
        time.sleep(2.5)

    finally:
        # Stop audio
        try:
            audio_proc.terminate()
        except Exception:
            pass

        # Finalize SimpleScreenRecorder
        print("Finalizing video recording...")
        try:
            ssr.stdin.write("record-save\n")
            ssr.stdin.flush()
            ssr.stdin.close()
            time.sleep(2.5)
            ssr.terminate()
            ssr.wait(timeout=4.0)
        except Exception:
            try:
                ssr.kill()
            except Exception:
                pass

    # Find the newly created video file
    time.sleep(1.5)
    current_videos = set(glob.glob(os.path.expanduser("~/Videos/*.mp4")))
    new_files = list(current_videos - existing_videos)

    if new_files:
        latest_file = max(new_files, key=os.path.getmtime)
        print(f"Recorded file: {latest_file}")
        # Copy to final video path
        subprocess.run(["cp", "-f", latest_file, FINAL_VIDEO])
        print(f"Video saved as: {FINAL_VIDEO}")
    else:
        # Fallback to the latest simplescreenrecorder file
        ssr_files = glob.glob(os.path.expanduser("~/Videos/simplescreenrecorder-*.mp4"))
        if ssr_files:
            latest_ssr = max(ssr_files, key=os.path.getmtime)
            subprocess.run(["cp", "-f", latest_ssr, FINAL_VIDEO])
            print(f"Video saved from latest SSR: {FINAL_VIDEO}")

    # Check file size & send notification
    if os.path.exists(FINAL_VIDEO):
        size_mb = os.path.getsize(FINAL_VIDEO) / (1024 * 1024)
        print(f"Success! Showcase video created: {FINAL_VIDEO} ({size_mb:.2f} MB)")
        subprocess.run(["notify-send", "-u", "normal", "-i", "video-x-generic", "🎬 Ricing Showcase Video", f"Video berhasil direkam ({size_mb:.2f} MB)"])
    else:
        print("Video generation finished.")


if __name__ == "__main__":
    run_showcase()
