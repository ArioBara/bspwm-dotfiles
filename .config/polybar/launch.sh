#!/usr/bin/env bash

# Terminate already running bar instances
killall -q polybar

# Wait until the processes have been shut down
while pgrep -u $UID -x polybar >/dev/null; do sleep 0.1; done

# Launch Polybar for all connected monitors
if command -v xrandr > /dev/null; then
  for m in $(xrandr --query | grep " connected" | cut -d" " -f1); do
    nohup polybar main -c "$HOME/.config/polybar/config.ini" >> /tmp/polybar.log 2>&1 &
  done
  disown -a 2>/dev/null || true
else
  nohup polybar main -c "$HOME/.config/polybar/config.ini" >> /tmp/polybar.log 2>&1 &
  disown -a 2>/dev/null || true
fi
