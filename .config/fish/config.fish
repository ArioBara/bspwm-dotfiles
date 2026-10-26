# ==============================================================================
#  FISH SHELL CONFIGURATION - CATPPUCCIN MOCHA THEME
# ==============================================================================

# Disable default welcome greeting
set -g fish_greeting ""

# Environment Variables & PATH
for p in "$HOME/.local/bin" "$HOME/.opencode/bin" "$HOME/.cargo/bin"
    if test -d "$p"; and not contains "$p" $PATH
        set -gx PATH "$p" $PATH
    end
end

set -gx GTK_THEME "catppuccin-mocha-mauve-standard+default"
set -gx QT_QPA_PLATFORMTHEME "gtk2"

# --- Catppuccin Mocha Syntax Highlighting Colors ---
set -g fish_color_normal cdd6f4
set -g fish_color_command cba6f7 --bold
set -g fish_color_keyword f38ba8
set -g fish_color_quote a6e3a1
set -g fish_color_redirection f5c2e7
set -g fish_color_end fab387
set -g fish_color_error f38ba8
set -g fish_color_param 89b4fa
set -g fish_color_comment 6c7086
set -g fish_color_selection --background=313244
set -g fish_color_search_match --background=313244
set -g fish_color_operator 94e2d5
set -g fish_color_escape eba0ac
set -g fish_color_autosuggestion 6c7086

# --- Useful Aliases ---
alias ls='ls --color=auto'
alias ll='ls -lah --color=auto'
alias l='ls -CF --color=auto'
alias grep='grep --color=auto'
alias c='clear'
alias clock='tty-clock -c -C 4 -B -s'
alias music='cava'
alias bspwmrc='nano ~/.config/bspwm/bspwmrc'
alias sxhkdrc='nano ~/.config/sxhkd/sxhkdrc'
alias polybarcfg='nano ~/.config/polybar/config.ini'
alias reload='bspc wm -r; and pkill -USR1 -x sxhkd; and notify-send -u low "BSPWM" "Environment reloaded"'

# --- Custom Catppuccin Prompt ---
function fish_prompt
    set -l last_status $status
    set -l stat_color (set_color a6e3a1)
    if test $last_status -ne 0
        set stat_color (set_color f38ba8)
    end

    # User & Host
    set -l user_color (set_color cba6f7 --bold)
    set -l host_color (set_color 89b4fa)
    set -l dir_color (set_color 94e2d5 --bold)
    set -l git_color (set_color fab387)

    # Git branch info
    set -l git_info ""
    if command -v git >/dev/null; and test -d .git
        set -l branch (git branch --show-current 2>/dev/null)
        if test -n "$branch"
            set git_info " $git_color(󰘬 $branch)"
        end
    end

    echo -s "$user_color$USER" (set_color 6c7086)"@" "$host_color$hostname" " " "$dir_color"(prompt_pwd) "$git_info"
    echo -n -s "$stat_color󰄾 " (set_color normal)
end


# Added by Antigravity CLI installer
set -gx PATH "/home/ario/.local/bin" $PATH
