# Random unsorted stuff

## Links

https://feeding.cloud.geek.nz/posts/creating-a-modern-tiling-desktop-environment-using-i3/

[i3 companion](https://github.com/DarkStarSword/junk/tree/master/config/home/.i3)

## XFCE

The basics to set it up can be cherry picked here: http://feeblenerd.blogspot.de/2015/11/pretty-i3-with-xfce.html

[internals](http://rabexc.org/posts/an-unwilling-dive-in-xfce4-internals)

All the configs are in `~/.config` and very tidy! Nice!


## Snippets

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

