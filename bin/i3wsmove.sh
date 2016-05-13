#!/bin/bash - 
wslist () {
    i3-msg -t get_workspaces | tr ',' '\n' | grep '"name":' | sed 's/"name":"\(.*\)"/\1/g' | sort -V
}

case $1 in
    [0-9]*)
        i3-msg move container to workspace number "$1" > /dev/null
        ;;
    ?*)
        i3-msg move container to workspace "$1" > /dev/null
        ;;
    *)
        wslist
        ;;
esac
