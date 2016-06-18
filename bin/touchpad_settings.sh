#!/bin/bash

xinput set-prop "SynPS/2 Synaptics TouchPad" "Synaptics Locked Drags" 1
xinput set-prop "SynPS/2 Synaptics TouchPad" "Synaptics Tap Action" 0, 0, 0, 0, 1, 3, 2

# old busted json settings
# use xinput, xinput list, xinput list-props, xinput list-props <id>
# to get features of the device
#
# {
#  "circular_scrolling": false,
#  "circular_touchpad": false,
#  "rt_tap_action": 2,
#  "circular_scrolling_distance": 5.73,
#  "edge_motion_always": false,
#  "horizontal_scrolling_distance": 107,
#  "horizontal_two_finger_scrolling": true,
#  "horizontal_edge_scrolling": true,
#  "lt_tap_action": 0,
#  "tap_and_drag_gesture": true,
#  "f2_tap_action": 3,
#  "corner_coasting": false,
#  "acceleration_factor": 0.0371,
#  "fast_taps": false,
#  "vertical_edge_scrolling": true,
#  "maximum_speed": 1.75,
#  "circular_scrolling_trigger": 0,
#  "minimum_speed": 1.0,
#  "locked_drags": true,
#  "vertical_two_finger_scrolling": true,
#  "f1_tap_action": 1,
#  "coasting_speed": 20.0,
#  "vertical_scrolling_distance": 107,
#  "f3_tap_action": 0,
#  "locked_drags_timeout": 5.0,
#  "lb_tap_action": 0,
#  "rb_tap_action": 3
#}
