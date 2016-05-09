# XFCE

The basics to set it up can be cherry picked here: http://feeblenerd.blogspot.de/2015/11/pretty-i3-with-xfce.html

[internals](http://rabexc.org/posts/an-unwilling-dive-in-xfce4-internals)

All the configs are in `~/.config` and very tidy! Nice!

# Startup reorg

Most of this should be done via XFCE now? not sure

    exec --no-startup-id synapse -s
    exec --no-startup-id glipper
    exec --no-startup-id gnome-settings-daemon
    exec --no-startup-id gnome-keyring-daemon --start --components=gpg,pkcs11,secrets,ssh
    exec --no-startup-id kwalletd
    exec --no-startup-id gnome-sound-applet
    exec --no-startup-id nm-applet &
    exec --no-startup-id /usr/lib/policykit-1-gnome/polkit-gnome-authentication-agent-1
    exec --no-startup-id sh -c '/usr/bin/nvidia-settings --load-config-only'

    exec --no-startup-id classicmenu-indicator
    exec --no-startup-id diodon
    exec --no-startup-id $bins/start_xautolock.sh  does not play with gnome
    exec --no-startup-id ulatencyd
    exec --no-startup-id "sh -c 'sleep 15; exec gmail-notify'"

# Bindings reorg

# FIXME configure in XFCE and throw out ####################
    
    exec --no-startup-id xmodmap ~/.xmodmap
    exec --no-startup-id "setxkbmap -model pc105 -layout de -variant nodeadkeys"
    exec --no-startup-id dropbox start
    # Set wm name to something Java recognizes (overriden if run in .xsessionrc)
    exec_always --no-startup-id wmname LG3D
    # try to set sane working config for 3 screens
    exec_always --no-startup-id $bin/xrandr_work.sh
    # always adjust wallpapers in case screens/resolutions changed
    exec_always --no-startup-id $bin/delayed_nitrogen_restore.sh

# Special window settings reorg

    # ASSIGN Apps to specific windows #
    #assign [class="^Firefox$"] 10
    #assign [class="^Chromium-browser$"] 10
    
    # PYCHARM
    set $pcWin Debug|Inspection|^Find$|^Changes$|TeamCity|^Run$|Version Control|Messages
    set $pcWin2 ^Database Console|^Grep Console|^Unversioned Files
    # set $pcWin3 ^Commit Changes|
    for_window [class="jetbrains-pycharm" instance="sun-awt-X11-XFramePeer"] floating disable
    # for_window [class="jetbrains-pycharm" instance="sun-awt-X11-XDialogPeer"] floating disable
    for_window [class="jetbrains-pycharm" title="($pcWin|$pcWin2)"] floating disable
    assign [class="jetbrains-pycharm" title="($pcWin|$pcWin2)"] 2
    
    #assign [class="jetbrains-pycharm" instance="sun-awt-X11-XDialogPeer"] 2
    #for_window [class="jetbrains-pycharm" title="Commit Changes"] floating enable
    # the little navigation popup has a space as the title ...
    #for_window [class="jetbrains-pycharm" instance="sun-awt-X11-XDialogPeer" title=" "] floating enable
    
    # RDP
    for_window [class="xfreerdp"]floating disable
    
    
    # GENERAL
    #for_window [title="Event Tester|Save Screencast|Copying|Moving|in Path"] floating enable
    
    for_window [title="synapse"] border none


# Snippets

## move mouse out of the way with window if context key is pressed
bindsym $mod+e exec xdotool getactivewindow mousemove -w '%1' 0 0

## jump to next open vim instance

bindsym $mod+a [class="urxvt" title="VIM"] focus

## Grab a window and move it to active workspace
bindsym $mod+F1 [class="Firefox"] move workspace current

## Tagging
 
    # does not work as expected
    # Nav is creating new workspace 1 even if renamed to 1: dev or 1:dev
    bindsym $mod+Mod1+r exec i3-input -F 'rename workspace to "%s"' -P 'New name: '

## Back and forth

    exec --no-startup-id $bin/focus_last.py
    bindsym Mod1+Tab exec $bin/focus_last.py --switch
    
## stuff

    bindsym $mod+Num_Lock exec $bin/lockscreen_with_wallpaper.sh
    bindsym $mod+Shift+Num_Lock exec $bin/lockscreen_with_suspend.sh
    bindsym $mod+Mod1+Shift+w exec $bin/get_wininfo.sh
    
* Windows key is main modifier - see `xmodmap` for info about modifier keys

# Software under consideration

## Orthodox file manager

* double commander

http://software.opensuse.org/download.html?project=home%3AAlexx2000&package=doublecmd-gtk

## Drop down terminal

* Guake

## Clipboard manager

* glipper
* diodon ?

# IPC

Do i3 stuff in script: i3-msg "move container to workspace 1"
