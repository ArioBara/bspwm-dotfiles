# AI Agents CLI PATH - Auto Generated
for p in "$HOME/.local/bin" "$HOME/.opencode/bin"
    if test -d "$p"; and not contains "$p" $PATH
        set -gx PATH "$p" $PATH
    end
end
