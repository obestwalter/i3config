#!/usr/bin/env bash

#!/bin/bash
for output in $(xrandr | grep '\Wconnected' | awk '{ print $1 }'); do
    if [[ $output =~ ^DP-3.*$ ]]; then
            dp3=$output
    fi
done
for output in $(xrandr | grep '\Wconnected' | awk '{ print $1 }'); do
    if [[ ! $output =~ ^LVDS.*$ ]]; then
       xrandr --output $dp3 --auto --output $output --pos 0x0 --auto \
              --right-of $dp3 --primary
    fi
done
