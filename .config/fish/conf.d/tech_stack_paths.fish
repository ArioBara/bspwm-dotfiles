# Tech Stack & Dev Environment PATHs - Auto Generated
set -gx BUN_INSTALL "$HOME/.bun"
set -gx DENO_INSTALL "$HOME/.deno"
set -gx PNPM_HOME "$HOME/.local/share/pnpm"
set -gx DOTNET_ROOT "$HOME/.dotnet"

for p in "$HOME/.local/bin" "$HOME/.cargo/bin" "$HOME/.bun/bin" "$HOME/.deno/bin" "$HOME/.dotnet" "$HOME/.dotnet/tools" "$HOME/.flutter/bin" "$HOME/go/bin" "$HOME/.local/share/pnpm"
    if test -d "$p"; and not contains "$p" $PATH
        set -gx PATH "$p" $PATH
    end
end
