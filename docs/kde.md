## KDE with i3 as wm

I am still on 5.24, so [this](https://maxnatt.gitlab.io/posts/kde-plasma-with-i3wm/#kde-524-and-older) works for me:

`sudo nano /usr/share/xsessions/kde-with-i3.desktop`

    [Desktop Entry]
    Name=kde-i3
    Comment=KDE with i3
    Exec=/usr/local/sbin/kde-i3
    TryExec=/usr/local/sbin/kde-i3
    Type=Application
    X-LightDM-DesktopName=kde-i3
    DesktopNames=kde-i3
    Keywords=tiling;wm;windowmanager;window;manager;kde;

`sudo nano /usr/local/sbin/kde-i3`

    #!/bin/sh
    export KDEWM=/usr/bin/i3
    exec /usr/bin/startplasma-x11

`sudo chmod a+x /usr/local/sbin/kde-i3`

# Misc

# Disable KDE global shortcuts

    gdbus call --session --dest=org.kde.kglobalaccel --object-path=/kglobalaccel --method=org.kde.KGlobalAccel.blockGlobalShortcuts 'true'
