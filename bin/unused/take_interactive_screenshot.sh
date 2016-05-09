#!/bin/bash

notify-send --expire-time 100 "select area for screenshot"
scrot --select
notify-send --urgency=low "screenshot taken"
