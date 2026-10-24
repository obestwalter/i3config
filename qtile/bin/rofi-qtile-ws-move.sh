#!/bin/bash -
# Qtile equivalent of bin/rofi-i3-ws-move.sh (move focused window to selected workspace)

wslist () {
    python3 -c '
from libqtile.command.client import InteractiveCommandClient
c = InteractiveCommandClient()
for name in c.get_groups().keys():
    if name not in ("scratchpad", "_i3_scratchpad"):
        print(name)
'
}

case $1 in
    ?*)
        python3 -c '
import sys
from libqtile.command.client import InteractiveCommandClient
c = InteractiveCommandClient()
target = sys.argv[1]
for name in c.get_groups().keys():
    if name == target or name.strip().startswith(target.strip()):
        c.window.togroup(name)
        break
' "$1" > /dev/null 2>&1
        ;;
    *)
        wslist
        ;;
esac
