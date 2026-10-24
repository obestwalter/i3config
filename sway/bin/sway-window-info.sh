#!/usr/bin/env bash
# Replacement for i3-xprop.sh: print sway criteria for a window.
# Depends on: swaymsg, jq, slurp (optional, for picking a window with the mouse)
#
# usage: sway-window-info.sh           -> pick a window with the mouse (needs slurp)
#        sway-window-info.sh focused   -> the focused window
#        sway-window-info.sh all       -> all windows
#
# Native wayland windows have app_id, xwayland windows have class/instance
# ("shell": "xwayland"). Use whichever is set in for_window/assign criteria.

mode="${1:-pick}"

windows() {
    swaymsg -t get_tree | jq -r '
        [.. | objects | select(has("pid") and .pid != null and (.type == "con" or .type == "floating_con"))]'
}

fmt='
    "id=\(.id)",
    (if .app_id then "app_id=\"\(.app_id)\"" else empty end),
    (if .window_properties then "class=\"\(.window_properties.class)\" instance=\"\(.window_properties.instance)\"" else empty end),
    "title=\"\(.name)\"",
    "shell=\(.shell)",
    "[" + ([
        (if .app_id then "app_id=\"\(.app_id)\"" else empty end),
        (if .window_properties then "class=\"\(.window_properties.class)\"" else empty end),
        "title=\"\(.name)\""
    ] | join(" ")) + "]"
'

case "$mode" in
    focused)
        windows | jq -r ".[] | select(.focused) | $fmt"
        ;;
    all)
        windows | jq -r ".[] | $fmt, \"\""
        ;;
    pick)
        # slurp -r selects a rectangle, we use the window whose rect contains the click point
        geo=$(swaymsg -t get_tree | jq -r '.. | objects | select(has("pid") and .pid != null) | "\(.rect.x),\(.rect.y) \(.rect.width)x\(.rect.height)"' | slurp -r -f '%x %y %w %h') || exit 1
        read -r x y _ <<<"$geo"
        windows | jq -r --argjson x "${x:-0}" --argjson y "${y:-0}" \
            ".[] | select(.rect.x <= \$x and .rect.y <= \$y and (.rect.x + .rect.width) > \$x and (.rect.y + .rect.height) > \$y) | $fmt"
        ;;
    *)
        echo "usage: $(basename "$0") [pick|focused|all]" >&2
        exit 1
        ;;
esac
