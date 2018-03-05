#!/bin/bash

#xinput list-props "DLL07BF:01 06CB:7A13 Touchpad"
#Device 'DLL07BF:01 06CB:7A13 Touchpad':
#	Device Enabled (140):	1
#	Coordinate Transformation Matrix (142):	1.000000, 0.000000, 0.000000, 0.000000, 1.000000, 0.000000, 0.000000, 0.000000, 1.000000
#	libinput Tapping Enabled (278):	1
#	libinput Tapping Enabled Default (279):	0
#	libinput Tapping Drag Enabled (280):	1
#	libinput Tapping Drag Enabled Default (281):	1
#	libinput Tapping Drag Lock Enabled (282):	0
#	libinput Tapping Drag Lock Enabled Default (283):	0
#	libinput Tapping Button Mapping Enabled (284):	1, 0
#	libinput Tapping Button Mapping Default (285):	1, 0
#	libinput Natural Scrolling Enabled (286):	0
#	libinput Natural Scrolling Enabled Default (287):	0
#	libinput Left Handed Enabled (288):	0
#	libinput Left Handed Enabled Default (289):	0
#	libinput Accel Speed (290):	0.000000
#	libinput Accel Speed Default (291):	0.000000
#	libinput Scroll Methods Available (292):	1, 1, 0
#	libinput Scroll Method Enabled (293):	1, 0, 0
#	libinput Scroll Method Enabled Default (294):	1, 0, 0
#	libinput Click Methods Available (295):	1, 1
#	libinput Click Method Enabled (296):	1, 0
#	libinput Click Method Enabled Default (297):	1, 0
#	libinput Middle Emulation Enabled (298):	0
#	libinput Middle Emulation Enabled Default (299):	0
#	libinput Send Events Modes Available (263):	1, 1
#	libinput Send Events Mode Enabled (264):	0, 0
#	libinput Send Events Mode Enabled Default (265):	0, 0
#	libinput Disable While Typing Enabled (300):	1
#	libinput Disable While Typing Enabled Default (301):	1
#	Device Node (266):	"/dev/input/event10"
#	Device Product ID (267):	1739, 31251
#	libinput Drag Lock Buttons (302):	<no items>
#	libinput Horizontal Scroll Enabled (303):	1
#22:30:01 ob@h2g2 [0] < ~ >  277 %


xinput set-prop "DLL07BF:01 06CB:7A13 Touchpad" "libinput Tapping Enabled" 1
#xinput set-prop "DLL07BF:01 06CB:7A13 Touchpad" "libinput Tapping Enabled Default" 1
xinput set-prop "DLL07BF:01 06CB:7A13 Touchpad" "libinput Tapping Drag Lock Enabled"	1
#xinput set-prop "DLL07BF:01 06CB:7A13 Touchpad" "libinput Tapping Drag Lock Default"	1

