# Inter process communication

## I3

Do i3 stuff in script: i3-msg "move container to workspace 1"

## Dbus

http://unix.stackexchange.com/questions/46301/a-list-of-available-dbus-services

https://wiki.gnome.org/action/show/Apps/DFeet?action=show&redirect=DFeet

    import dbus
    
    for service in dbus.SystemBus().list_names():
    print(service)
   
    for service in dbus.SessionBus().list_names():
        print(service)
