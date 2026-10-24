#!/usr/bin/env bash
# Replaces scrot / xfce4-screenshooter. Depends on: grim, slurp, wl-clipboard
# usage: screenshot.sh [full|region]   -> saves to ~/ and copies to the clipboard

filename="$HOME/scrot-$(date +"%y-%m-%d-%H-%M-%S").png"
case "${1:-full}" in
    region) grim -g "$(slurp)" "$filename" || exit 1 ;;
    *)      grim "$filename" ;;
esac
wl-copy < "$filename"
notify-send -t 1000 -a 'CENTRAL-CONTROL-PROGRAM' "screenshot: $filename"
