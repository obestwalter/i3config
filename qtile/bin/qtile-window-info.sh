#!/usr/bin/env bash
# Replacement for i3-xprop.sh: print the properties needed for Qtile `Match(...)` rules.
# X11 only (Qtile's Wayland backend has no xprop, use `qtile cmd-obj -o window -f info` there).
# Depends on: xprop
#
# usage: qtile-window-info.sh            -> click on a window
#        qtile-window-info.sh focused    -> focused window (via qtile cmd-obj, works for X11 and Wayland)
#
# Qtile mapping: WM_CLASS = "instance", "class" -> Match(wm_instance_class=..., wm_class=...),
#                _NET_WM_NAME -> Match(title=...), WM_WINDOW_ROLE -> Match(role=...)

if [ "$1" = "focused" ]; then
    qtile cmd-obj -o window -f info
    exit $?
fi

command -v xprop > /dev/null 2>&1 || { echo "$(basename "$0"): xprop: command not found" >&2; exit 1; }

props=$(xprop WM_CLASS _NET_WM_NAME WM_NAME WM_WINDOW_ROLE)
[ -n "$props" ] || exit 1

# first quoted string after "=" ... n-th quoted string
nth() { printf '%s\n' "$props" | sed -n "s/^$1([A-Z0-9_]*) = //p" | head -1; }

wm_class_line=$(nth WM_CLASS)
instance=$(printf '%s' "$wm_class_line" | sed -n 's/^"\([^"]*\)", "\([^"]*\)"$/\1/p')
class=$(printf '%s' "$wm_class_line" | sed -n 's/^"\([^"]*\)", "\([^"]*\)"$/\2/p')
title=$(nth _NET_WM_NAME)
[ -n "$title" ] || title=$(nth WM_NAME)
role=$(nth WM_WINDOW_ROLE)

echo "wm_class (class):    $class"
echo "wm_instance_class:   $instance"
echo "title:               $title"
echo "role:                $role"
echo
args=()
[ -n "$class" ] && args+=("wm_class=\"$class\"")
[ -n "$instance" ] && args+=("wm_instance_class=\"$instance\"")
[ -n "$title" ] && args+=("title=$title")
[ -n "$role" ] && args+=("role=$role")
printf 'Match('
( IFS=,; printf '%s' "${args[*]}" | sed 's/,/, /g' )
printf ')\n'
