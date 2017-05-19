# i3 config miner

* [X] watch a folder for changes
* [ ] only react on changes to .i3config files
* [X] concatenate .i3conf files and write to config
* [ ] replace variables depending on certain criteria (e.g. hostname, number of connected monitors, etc.)
* [ ] think about integrating it into py3status


# idea

settings.py instead of settings.i3conf that can then automatically adjust to environment changes.

Environment changes that are interesting need to be polled then (e.g. number of connected monitors, processes being spawned, whatever)

... or turn this into a py3status module after all ...
