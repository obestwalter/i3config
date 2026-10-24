#!/usr/bin/env bash
# Debian/Ubuntu package names. Qtile itself: the distro package is often old, consider pipx/pip:
#   pipx install qtile   (needs python3-xcffib, python3-cairocffi, libpangocairo, libxkbcommon-dev)

sudo apt install --yes \
  bat \
  dtrx \
  dunst \
  fonts-font-awesome \
  nitrogen \
  playerctl \
  python3-xcffib \
  python3-cairocffi \
  python3-dbus-next \
  qtile \
  rofi \
  screenkey \
  scrot \
  xbacklight \
  xdotool \
  xfce4-terminal \
  xfce4-screenshooter \
  xkeycaps \
  xtrlock \
  i3lock \
  unclutter \
  wmctrl \
  x11-utils
# x11-utils: xprop (qtile-window-info.sh). picom is optional (see configs-other in the i3 folder).
