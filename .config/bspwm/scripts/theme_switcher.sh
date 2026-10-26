#!/usr/bin/env bash

# ==============================================================================
#  DYNAMIC THEME SWITCHER FOR BSPWM
# ==============================================================================
# Mengubah tema seluruh sistem secara simultan:
# 1. Polybar Colors
# 2. Kitty Terminal Theme
# 3. Rofi Launcher & Menu Colors
# 4. BSPWM Border Colors
# 5. Dunst Notification Colors
# 6. Matching Wallpaper
# ==============================================================================

THEME_DIR="$HOME/.config/bspwm/themes"
WALL_DIR="$HOME/.config/bspwm/wallpapers"
CURRENT_THEME_FILE="$HOME/.config/bspwm/current_theme"

mkdir -p "$THEME_DIR"

notify() {
    local theme_name="$1"
    local desc="$2"
    if command -v dunstify &>/dev/null; then
        dunstify -a "Theme Switcher" -r 9998 -u low -i "preferences-desktop-theme" "󰏘 Tema Aktif: $theme_name" "$desc"
    elif command -v notify-send &>/dev/null; then
        notify-send -u low -i "preferences-desktop-theme" "󰏘 Tema Aktif: $theme_name" "$desc"
    fi
}

apply_catppuccin() {
    # 1. Polybar
    cat << 'EOF' > "$HOME/.config/polybar/colors.ini"
[colors]
# Catppuccin Mocha Palette
base         = #1e1e2e
mantle       = #181825
crust        = #11111b
surface0     = #313244
surface1     = #45475a
surface2     = #585b70
overlay0     = #6c7086
overlay1     = #7f849c
overlay2     = #9399b2
text         = #cdd6f4
subtext0     = #a6adc8
subtext1     = #bac2de
lavender     = #b4befe
blue         = #89b4fa
sapphire     = #74c7ec
sky          = #89dceb
teal         = #94e2d5
green        = #a6e3a1
yellow       = #f9e2af
peach        = #fab387
maroon       = #eba0ac
red          = #f38ba8
mauve        = #cba6f7
pink         = #f5c2e7
flamingo     = #f2cdcd
rosewater    = #f5e0dc

transparent  = #00000000
background   = #181825
background-alt = #313244
foreground   = #cdd6f4
primary      = #cba6f7
secondary    = #89b4fa
alert        = #f38ba8
disabled     = #6c7086
EOF

    # 2. Kitty Terminal
    cat << 'EOF' > "$HOME/.config/kitty/theme.conf"
foreground            #cdd6f4
background            #1e1e2e
selection_foreground  #1e1e2e
selection_background  #f5e0dc
cursor                #f5e0dc
cursor_text_color     #11111b

color0  #45475a
color1  #f38ba8
color2  #a6e3a1
color3  #f9e2af
color4  #89b4fa
color5  #f5c2e7
color6  #94e2d5
color7  #bac2de
color8  #585b70
color9  #f38ba8
color10 #a6e3a1
color11 #f9e2af
color12 #89b4fa
color13 #f5c2e7
color14 #94e2d5
color15 #a6adc8
EOF

    # 3. Rofi
    cat << 'EOF' > "$HOME/.config/rofi/colors.rasi"
* {
    bg-col:       #1e1e2e;
    bg-col-light: #313244;
    border-col:   #cba6f7;
    selected-col: #45475a;
    blue:         #89b4fa;
    mauve:        #cba6f7;
    teal:         #94e2d5;
    green:        #a6e3a1;
    peach:        #fab387;
    yellow:       #f9e2af;
    red:          #f38ba8;
    fg-col:       #cdd6f4;
    fg-col2:      #f38ba8;
    grey:         #6c7086;
}
EOF

    # 4. BSPWM Borders
    bspc config normal_border_color   "#313244"
    bspc config active_border_color   "#585b70"
    bspc config focused_border_color  "#cba6f7"
    bspc config presel_feedback_color "#f5c2e7"

    # 5. Dunst
    sed -i 's/^    frame_color = .*/    frame_color = "#cba6f7"/' "$HOME/.config/dunst/dunstrc" 2>/dev/null || true
    sed -i 's/^    background = .*/    background = "#1e1e2e"/' "$HOME/.config/dunst/dunstrc" 2>/dev/null || true

    # 6. Wallpaper
    "$HOME/.config/bspwm/scripts/set_wallpaper.sh" "cat_mocha.png"

    echo "catppuccin" > "$CURRENT_THEME_FILE"
    notify "Catppuccin Mocha" "Tema pastel dark modern bernuansa Lavender"
}

apply_tokyo_night() {
    # 1. Polybar
    cat << 'EOF' > "$HOME/.config/polybar/colors.ini"
[colors]
# Tokyo Night Palette
base         = #1a1b26
mantle       = #16161e
crust        = #13141c
surface0     = #24283b
surface1     = #292e42
surface2     = #414868
overlay0     = #565f89
overlay1     = #737aa2
overlay2     = #9aa5ce
text         = #c0caf5
subtext0     = #a9b1d6
subtext1     = #9aa5ce
lavender     = #b4f9f8
blue         = #7aa2f7
sapphire     = #7dcfff
sky          = #7dcfff
teal         = #73daca
green        = #9ece6a
yellow       = #e0af68
peach        = #ff9e64
maroon       = #f7768e
red          = #f7768e
mauve        = #bb9af7
pink         = #bb9af7
flamingo     = #ff9e64
rosewater    = #f7768e

transparent  = #00000000
background   = #16161e
background-alt = #24283b
foreground   = #c0caf5
primary      = #7aa2f7
secondary    = #bb9af7
alert        = #f7768e
disabled     = #565f89
EOF

    # 2. Kitty Terminal
    cat << 'EOF' > "$HOME/.config/kitty/theme.conf"
foreground            #c0caf5
background            #1a1b26
selection_foreground  #c0caf5
selection_background  #283457
cursor                #c0caf5
cursor_text_color     #1a1b26

color0  #15161e
color1  #f7768e
color2  #9ece6a
color3  #e0af68
color4  #7aa2f7
color5  #bb9af7
color6  #7dcfff
color7  #a9b1d6
color8  #414868
color9  #f7768e
color10 #9ece6a
color11 #e0af68
color12 #7aa2f7
color13 #bb9af7
color14 #7dcfff
color15 #c0caf5
EOF

    # 3. Rofi
    cat << 'EOF' > "$HOME/.config/rofi/colors.rasi"
* {
    bg-col:       #1a1b26;
    bg-col-light: #24283b;
    border-col:   #7aa2f7;
    selected-col: #292e42;
    blue:         #7aa2f7;
    mauve:        #bb9af7;
    teal:         #7dcfff;
    green:        #9ece6a;
    peach:        #ff9e64;
    yellow:       #e0af68;
    red:          #f7768e;
    fg-col:       #c0caf5;
    fg-col2:      #f7768e;
    grey:         #565f89;
}
EOF

    # 4. BSPWM Borders
    bspc config normal_border_color   "#24283b"
    bspc config active_border_color   "#414868"
    bspc config focused_border_color  "#7aa2f7"
    bspc config presel_feedback_color "#bb9af7"

    # 5. Dunst
    sed -i 's/^    frame_color = .*/    frame_color = "#7aa2f7"/' "$HOME/.config/dunst/dunstrc" 2>/dev/null || true
    sed -i 's/^    background = .*/    background = "#1a1b26"/' "$HOME/.config/dunst/dunstrc" 2>/dev/null || true

    # 6. Wallpaper
    "$HOME/.config/bspwm/scripts/set_wallpaper.sh" "gundam_neotokyo.jpg"

    echo "tokyo-night" > "$CURRENT_THEME_FILE"
    notify "Tokyo Night" "Tema modern bernuansa Cyberpunk Indigo Blue"
}

apply_nord() {
    # 1. Polybar
    cat << 'EOF' > "$HOME/.config/polybar/colors.ini"
[colors]
# Nord Palette
base         = #2e3440
mantle       = #242933
crust        = #1f232a
surface0     = #3b4252
surface1     = #434c5e
surface2     = #4c566a
overlay0     = #616e88
overlay1     = #7b88a1
overlay2     = #909daf
text         = #eceff4
subtext0     = #e5e9f0
subtext1     = #d8dee9
lavender     = #88c0d0
blue         = #81a1c1
sapphire     = #88c0d0
sky          = #8fbcbb
teal         = #88c0d0
green        = #a3be8c
yellow       = #ebcb8b
peach        = #d08770
maroon       = #bf616a
red          = #bf616a
mauve        = #b48ead
pink         = #b48ead
flamingo     = #d08770
rosewater    = #eceff4

transparent  = #00000000
background   = #242933
background-alt = #3b4252
foreground   = #eceff4
primary      = #88c0d0
secondary    = #81a1c1
alert        = #bf616a
disabled     = #616e88
EOF

    # 2. Kitty Terminal
    cat << 'EOF' > "$HOME/.config/kitty/theme.conf"
foreground            #eceff4
background            #2e3440
selection_foreground  #2e3440
selection_background  #88c0d0
cursor                #d8dee9
cursor_text_color     #2e3440

color0  #3b4252
color1  #bf616a
color2  #a3be8c
color3  #ebcb8b
color4  #81a1c1
color5  #b48ead
color6  #88c0d0
color7  #e5e9f0
color8  #4c566a
color9  #bf616a
color10 #a3be8c
color11 #ebcb8b
color12 #81a1c1
color13 #b48ead
color14 #8fbcbb
color15 #eceff4
EOF

    # 3. Rofi
    cat << 'EOF' > "$HOME/.config/rofi/colors.rasi"
* {
    bg-col:       #2e3440;
    bg-col-light: #3b4252;
    border-col:   #88c0d0;
    selected-col: #434c5e;
    blue:         #81a1c1;
    mauve:        #88c0d0;
    teal:         #8fbcbb;
    green:        #a3be8c;
    peach:        #d08770;
    yellow:       #ebcb8b;
    red:          #bf616a;
    fg-col:       #eceff4;
    fg-col2:      #bf616a;
    grey:         #616e88;
}
EOF

    # 4. BSPWM Borders
    bspc config normal_border_color   "#3b4252"
    bspc config active_border_color   "#4c566a"
    bspc config focused_border_color  "#88c0d0"
    bspc config presel_feedback_color "#81a1c1"

    # 5. Dunst
    sed -i 's/^    frame_color = .*/    frame_color = "#88c0d0"/' "$HOME/.config/dunst/dunstrc" 2>/dev/null || true
    sed -i 's/^    background = .*/    background = "#2e3440"/' "$HOME/.config/dunst/dunstrc" 2>/dev/null || true

    # 6. Wallpaper
    "$HOME/.config/bspwm/scripts/set_wallpaper.sh" "waves_Waves%20Dark%206016x6016.jpg"

    echo "nord" > "$CURRENT_THEME_FILE"
    notify "Nord" "Tema Arctic minimalis bernuansa Frost & Snow"
}

apply_gruvbox() {
    # 1. Polybar
    cat << 'EOF' > "$HOME/.config/polybar/colors.ini"
[colors]
# Gruvbox Dark Palette
base         = #282828
mantle       = #1d2021
crust        = #141617
surface0     = #3c3836
surface1     = #504945
surface2     = #665c54
overlay0     = #7c6f64
overlay1     = #928374
overlay2     = #a89984
text         = #ebdbb2
subtext0     = #d5c4a1
subtext1     = #bdae93
lavender     = #83a598
blue         = #83a598
sapphire     = #8ec07c
sky          = #8ec07c
teal         = #8ec07c
green        = #b8bb26
yellow       = #fabd2f
peach        = #fe8019
maroon       = #fb4934
red          = #fb4934
mauve        = #d3869b
pink         = #d3869b
flamingo     = #fe8019
rosewater    = #ebdbb2

transparent  = #00000000
background   = #1d2021
background-alt = #3c3836
foreground   = #ebdbb2
primary      = #fabd2f
secondary    = #fe8019
alert        = #fb4934
disabled     = #7c6f64
EOF

    # 2. Kitty Terminal
    cat << 'EOF' > "$HOME/.config/kitty/theme.conf"
foreground            #ebdbb2
background            #282828
selection_foreground  #282828
selection_background  #fabd2f
cursor                #ebdbb2
cursor_text_color     #282828

color0  #282828
color1  #cc241d
color2  #98971a
color3  #d79921
color4  #458588
color5  #b16286
color6  #689d6a
color7  #a89984
color8  #928374
color9  #fb4934
color10 #b8bb26
color11 #fabd2f
color12 #83a598
color13 #d3869b
color14 #8ec07c
color15 #ebdbb2
EOF

    # 3. Rofi
    cat << 'EOF' > "$HOME/.config/rofi/colors.rasi"
* {
    bg-col:       #282828;
    bg-col-light: #3c3836;
    border-col:   #fabd2f;
    selected-col: #504945;
    blue:         #83a598;
    mauve:        #fabd2f;
    teal:         #8ec07c;
    green:        #b8bb26;
    peach:        #fe8019;
    yellow:       #fabd2f;
    red:          #fb4934;
    fg-col:       #ebdbb2;
    fg-col2:      #fb4934;
    grey:         #7c6f64;
}
EOF

    # 4. BSPWM Borders
    bspc config normal_border_color   "#3c3836"
    bspc config active_border_color   "#665c54"
    bspc config focused_border_color  "#fabd2f"
    bspc config presel_feedback_color "#fe8019"

    # 5. Dunst
    sed -i 's/^    frame_color = .*/    frame_color = "#fabd2f"/' "$HOME/.config/dunst/dunstrc" 2>/dev/null || true
    sed -i 's/^    background = .*/    background = "#282828"/' "$HOME/.config/dunst/dunstrc" 2>/dev/null || true

    # 6. Wallpaper
    "$HOME/.config/bspwm/scripts/set_wallpaper.sh" "shaded_landscape.png"

    echo "gruvbox" > "$CURRENT_THEME_FILE"
    notify "Gruvbox Dark" "Tema retro hangat bernuansa Gold & Earth Tones"
}

apply_everforest() {
    # 1. Polybar
    cat << 'EOF' > "$HOME/.config/polybar/colors.ini"
[colors]
# Everforest Palette
base         = #2d353b
mantle       = #232a2e
crust        = #1e2326
surface0     = #343f44
surface1     = #475258
surface2     = #56635f
overlay0     = #7a8478
overlay1     = #859289
overlay2     = #9da9a0
text         = #d3c6aa
subtext0     = #e4d6b6
subtext1     = #d3c6aa
lavender     = #7fbbb3
blue         = #7fbbb3
sapphire     = #83c092
sky          = #83c092
teal         = #83c092
green        = #a7c080
yellow       = #dbbc7f
peach        = #e69875
maroon       = #e67e80
red          = #e67e80
mauve        = #d699b6
pink         = #d699b6
flamingo     = #e69875
rosewater    = #d3c6aa

transparent  = #00000000
background   = #232a2e
background-alt = #343f44
foreground   = #d3c6aa
primary      = #a7c080
secondary    = #83c092
alert        = #e67e80
disabled     = #7a8478
EOF

    # 2. Kitty Terminal
    cat << 'EOF' > "$HOME/.config/kitty/theme.conf"
foreground            #d3c6aa
background            #2d353b
selection_foreground  #2d353b
selection_background  #a7c080
cursor                #d3c6aa
cursor_text_color     #2d353b

color0  #232a2e
color1  #e67e80
color2  #a7c080
color3  #dbbc7f
color4  #7fbbb3
color5  #d699b6
color6  #83c092
color7  #d3c6aa
color8  #56635f
color9  #e67e80
color10 #a7c080
color11 #dbbc7f
color12 #7fbbb3
color13 #d699b6
color14 #83c092
color15 #fdf6e3
EOF

    # 3. Rofi
    cat << 'EOF' > "$HOME/.config/rofi/colors.rasi"
* {
    bg-col:       #2d353b;
    bg-col-light: #343f44;
    border-col:   #a7c080;
    selected-col: #475258;
    blue:         #7fbbb3;
    mauve:        #a7c080;
    teal:         #83c092;
    green:        #a7c080;
    peach:        #e69875;
    yellow:       #dbbc7f;
    red:          #e67e80;
    fg-col:       #d3c6aa;
    fg-col2:      #e67e80;
    grey:         #7a8478;
}
EOF

    # 4. BSPWM Borders
    bspc config normal_border_color   "#343f44"
    bspc config active_border_color   "#56635f"
    bspc config focused_border_color  "#a7c080"
    bspc config presel_feedback_color "#83c092"

    # 5. Dunst
    sed -i 's/^    frame_color = .*/    frame_color = "#a7c080"/' "$HOME/.config/dunst/dunstrc" 2>/dev/null || true
    sed -i 's/^    background = .*/    background = "#2d353b"/' "$HOME/.config/dunst/dunstrc" 2>/dev/null || true

    # 6. Wallpaper
    "$HOME/.config/bspwm/scripts/set_wallpaper.sh" "landscapes_Clearday.jpg"

    echo "everforest" > "$CURRENT_THEME_FILE"
    notify "Everforest" "Tema sejuk bernuansa alam & natural green"
}

apply_one_piece() {
    # 1. Polybar
    cat << 'EOF' > "$HOME/.config/polybar/colors.ini"
[colors]
# One Piece Straw Hat Palette
base         = #0f141c
mantle       = #0a0d14
crust        = #06080d
surface0     = #1a2332
surface1     = #26344d
surface2     = #384c6e
overlay0     = #5c677d
overlay1     = #7b88a1
overlay2     = #a8dadc
text         = #f1faee
subtext0     = #a8dadc
subtext1     = #e0e6ed
lavender     = #4ea8de
blue         = #4ea8de
sapphire     = #0077b6
sky          = #48cae4
teal         = #06d6a0
green        = #06d6a0
yellow       = #ffd166
peach        = #f77f00
maroon       = #e63946
red          = #e63946
mauve        = #e63946
pink         = #f77f00
flamingo     = #ffd166
rosewater    = #f1faee

transparent  = #00000000
background   = #0a0d14
background-alt = #1a2332
foreground   = #f1faee
primary      = #e63946
secondary    = #ffd166
alert        = #e63946
disabled     = #5c677d
EOF

    # 2. Kitty Terminal
    cat << 'EOF' > "$HOME/.config/kitty/theme.conf"
foreground            #f1faee
background            #0f141c
selection_foreground  #0f141c
selection_background  #ffd166
cursor                #ffd166
cursor_text_color     #0f141c

color0  #1a2332
color1  #e63946
color2  #06d6a0
color3  #ffd166
color4  #4ea8de
color5  #f77f00
color6  #a8dadc
color7  #f1faee
color8  #5c677d
color9  #e63946
color10 #06d6a0
color11 #ffd166
color12 #4ea8de
color13 #f77f00
color14 #a8dadc
color15 #ffffff
EOF

    # 3. Rofi
    cat << 'EOF' > "$HOME/.config/rofi/colors.rasi"
* {
    bg-col:       #0f141c;
    bg-col-light: #1a2332;
    border-col:   #e63946;
    selected-col: #26344d;
    blue:         #4ea8de;
    mauve:        #e63946;
    teal:         #06d6a0;
    green:        #06d6a0;
    peach:        #f77f00;
    yellow:       #ffd166;
    red:          #e63946;
    fg-col:       #f1faee;
    fg-col2:      #e63946;
    grey:         #5c677d;
}
EOF

    # 4. BSPWM Borders
    bspc config normal_border_color   "#1a2332"
    bspc config active_border_color   "#26344d"
    bspc config focused_border_color  "#e63946"
    bspc config presel_feedback_color "#ffd166"

    # 5. Dunst
    sed -i 's/^    frame_color = .*/    frame_color = "#e63946"/' "$HOME/.config/dunst/dunstrc" 2>/dev/null || true
    sed -i 's/^    background = .*/    background = "#0f141c"/' "$HOME/.config/dunst/dunstrc" 2>/dev/null || true

    # 6. Wallpaper
    "$HOME/.config/bspwm/scripts/set_wallpaper.sh" "one_piece.jpg"

    echo "one-piece" > "$CURRENT_THEME_FILE"
    notify "One Piece" "Tema Bajak Laut Topi Jerami bernuansa Crimson & Gold Sunset"
}

apply_naruto() {
    # 1. Polybar
    cat << 'EOF' > "$HOME/.config/polybar/colors.ini"
[colors]
# Naruto Sage Mode Palette
base         = #12131a
mantle       = #0b0c10
crust        = #07080a
surface0     = #1c1e29
surface1     = #282b3d
surface2     = #3b3f57
overlay0     = #5c6079
overlay1     = #7b80a1
overlay2     = #9aa0c7
text         = #f8f9fa
subtext0     = #ced4da
subtext1     = #adb5bd
lavender     = #00f0ff
blue         = #00f0ff
sapphire     = #38bdf8
sky          = #00f0ff
teal         = #2ec4b6
green        = #52b788
yellow       = #ffb703
peach        = #ff7700
maroon       = #d90429
red          = #d90429
mauve        = #ff7700
pink         = #ff7700
flamingo     = #ffb703
rosewater    = #f8f9fa

transparent  = #00000000
background   = #0b0c10
background-alt = #1c1e29
foreground   = #f8f9fa
primary      = #ff7700
secondary    = #00f0ff
alert        = #d90429
disabled     = #5c6079
EOF

    # 2. Kitty Terminal
    cat << 'EOF' > "$HOME/.config/kitty/theme.conf"
foreground            #f8f9fa
background            #12131a
selection_foreground  #12131a
selection_background  #ff7700
cursor                #ff7700
cursor_text_color     #12131a

color0  #1c1e29
color1  #d90429
color2  #52b788
color3  #ffb703
color4  #00f0ff
color5  #ff7700
color6  #2ec4b6
color7  #ced4da
color8  #5c6079
color9  #d90429
color10 #52b788
color11 #ffb703
color12 #00f0ff
color13 #ff7700
color14 #2ec4b6
color15 #ffffff
EOF

    # 3. Rofi
    cat << 'EOF' > "$HOME/.config/rofi/colors.rasi"
* {
    bg-col:       #12131a;
    bg-col-light: #1c1e29;
    border-col:   #ff7700;
    selected-col: #282b3d;
    blue:         #00f0ff;
    mauve:        #ff7700;
    teal:         #2ec4b6;
    green:        #52b788;
    peach:        #ff7700;
    yellow:       #ffb703;
    red:          #d90429;
    fg-col:       #f8f9fa;
    fg-col2:      #d90429;
    grey:         #5c6079;
}
EOF

    # 4. BSPWM Borders
    bspc config normal_border_color   "#1c1e29"
    bspc config active_border_color   "#282b3d"
    bspc config focused_border_color  "#ff7700"
    bspc config presel_feedback_color "#00f0ff"

    # 5. Dunst
    sed -i 's/^    frame_color = .*/    frame_color = "#ff7700"/' "$HOME/.config/dunst/dunstrc" 2>/dev/null || true
    sed -i 's/^    background = .*/    background = "#12131a"/' "$HOME/.config/dunst/dunstrc" 2>/dev/null || true

    # 6. Wallpaper
    "$HOME/.config/bspwm/scripts/set_wallpaper.sh" "naruto.jpg"

    echo "naruto" > "$CURRENT_THEME_FILE"
    notify "Naruto Shippuden" "Tema Sage Mode bernuansa Kurama Orange & Chakra Cyan"
}

reload_services() {
    # Reload Polybar
    "$HOME/.config/polybar/launch.sh"

    # Reload Dunst
    killall -q dunst 2>/dev/null || true
    nohup dunst -config "$HOME/.config/dunst/dunstrc" >/dev/null 2>&1 &

    # Reload Kitty instances
    killall -SIGUSR1 kitty 2>/dev/null || true
}

apply_theme() {
    local target="$1"
    case "$target" in
        catppuccin)
            apply_catppuccin
            ;;
        tokyo-night|tokyonight)
            apply_tokyo_night
            ;;
        nord)
            apply_nord
            ;;
        gruvbox)
            apply_gruvbox
            ;;
        everforest)
            apply_everforest
            ;;
        one-piece|onepiece)
            apply_one_piece
            ;;
        naruto)
            apply_naruto
            ;;
        random)
            "$HOME/.config/bspwm/scripts/set_wallpaper.sh" random
            notify "Wallpaper Acak" "Wallpaper latar belakang telah diacak"
            return
            ;;
        *)
            echo "Usage: $0 {catppuccin|tokyo-night|nord|gruvbox|everforest|one-piece|naruto|random}"
            exit 1
            ;;
    esac
    reload_services
}

# If an argument is provided, apply directly
if [ -n "$1" ]; then
    apply_theme "$1"
    exit 0
fi

# Otherwise, show interactive Rofi selector
CURRENT="catppuccin"
[ -f "$CURRENT_THEME_FILE" ] && CURRENT=$(cat "$CURRENT_THEME_FILE")

OPTIONS="󰄛 Catppuccin Mocha\n󰣇 Tokyo Night\n󰤨 Nord\n󰔎 Gruvbox Dark\n󰌪 Everforest\n󰀞 One Piece (Straw Hat)\n󰘳 Naruto (Sage Mode)\n🎲 Random Wallpaper"

CHOSEN=$(echo -e "$OPTIONS" | rofi -dmenu -i -theme ~/.config/rofi/mocha.rasi -p "󰏘 Style & Theme (Aktif: $CURRENT)" -lines 8)

case "$CHOSEN" in
    *"Catppuccin"*)
        apply_theme "catppuccin"
        ;;
    *"Tokyo Night"*)
        apply_theme "tokyo-night"
        ;;
    *"Nord"*)
        apply_theme "nord"
        ;;
    *"Gruvbox"*)
        apply_theme "gruvbox"
        ;;
    *"Everforest"*)
        apply_theme "everforest"
        ;;
    *"One Piece"*)
        apply_theme "one-piece"
        ;;
    *"Naruto"*)
        apply_theme "naruto"
        ;;
    *"Random Wallpaper"*)
        apply_theme "random"
        ;;
esac
