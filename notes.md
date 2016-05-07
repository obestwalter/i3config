# XFCE

The basics to set it up can be cherry picked here: http://feeblenerd.blogspot.de/2015/11/pretty-i3-with-xfce.html

[internals](http://rabexc.org/posts/an-unwilling-dive-in-xfce4-internals)

All the configs are in `~/.config` and very tidy! Nice!

# Startup reorg

# Most of this should be done via XFCE now?
# not sure
# exec --no-startup-id synapse -s
# exec --no-startup-id glipper
# exec --no-startup-id gnome-settings-daemon
# exec --no-startup-id gnome-keyring-daemon --start --components=gpg,pkcs11,secrets,ssh
# exec --no-startup-id kwalletd
# exec --no-startup-id gnome-sound-applet
# exec --no-startup-id nm-applet &
# exec --no-startup-id /usr/lib/policykit-1-gnome/polkit-gnome-authentication-agent-1
# exec --no-startup-id sh -c '/usr/bin/nvidia-settings --load-config-only'

# legacy
# exec --no-startup-id classicmenu-indicator
# exec --no-startup-id diodon
# exec --no-startup-id $bins/start_xautolock.sh  # does not play with gnome
# exec --no-startup-id ulatencyd
# exec --no-startup-id "sh -c 'sleep 15; exec gmail-notify'"

# Software under consideration

## Orthodox file manager

* double commander

http://software.opensuse.org/download.html?project=home%3AAlexx2000&package=doublecmd-gtk

## Drop down terminal

* Guake

## Search files

`catfish --start <folder to search> <thing to search>`

## Clipboard manager

* glipper
* diodon ?

# Color scheme: solarized

# IPC

Do i3 stuff in script: i3-msg "move container to workspace 1"
