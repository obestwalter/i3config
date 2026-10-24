#!/usr/bin/env bash
# Debian/Ubuntu package names (sway >= 1.8 recommended)

sudo apt install --yes \
  bat \
  brightnessctl \
  dtrx \
  dunst \
  fonts-font-awesome \
  grim \
  imagemagick \
  jq \
  libnotify-bin \
  playerctl \
  py3status \
  rofi \
  slurp \
  sway \
  swaybg \
  swayidle \
  swaylock \
  wev \
  wl-clipboard \
  wshowkeys \
  wtype \
  xfce4-terminal
# rofi: needs wayland support (rofi-wayland on older distros, rofi >= 2.0 natively)
# optional: gwenview (screenshot-and-gwenview.sh), cliphist (clipboard history)
