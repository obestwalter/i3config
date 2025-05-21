# TODO

* check todos in the config files
* check out branch-new-laptop-experiments
* autostart (what do I need? Gather from all over the place)
* terminal: show running command in title https://stackoverflow.com/q/71459823
* make little helper scripts to show shortcuts, but they need to be made mode-aware
  * something like this, but cleverer: grep "^bindsym \$win" config.d/* | sort | awk '{$1=""; print $0}'
  * maybe little python script is better
* set cursor theme: https://wiki.archlinux.org/title/Cursor_themes

## background stuff

oliver.bestwalter@LINX-000050:~$ pgrep -af plasma
1661604 /usr/bin/plasma-browser-integration-host chrome-extension://cimiefiiaegbelhefglklhhakcgmhkai/
oliver.bestwalter@LINX-000050:~$ pgrep -af kde
135 kdevtmpfs
1661570 /usr/lib/x86_64-linux-gnu/libexec/xdg-desktop-portal-kde
1661695 /usr/lib/x86_64-linux-gnu/libexec/kdeconnectd

ls config.d/ | grep -v "^control"
grep "^bindsym \$win" config.d/* | sort | awk '{$1=""; print $0}'