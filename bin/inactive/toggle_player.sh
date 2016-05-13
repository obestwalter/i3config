#!/bin/sh
#
# Author: Dennis Hodapp
# Filename: cplay
# Requires: cmus
#
# Tests if cmus is running and starts it if it isn't.
# Else it toggles play/pause.
# This command will break if you rename it to
# something containing "cmus".

TERMINAL=/usr/bin/xterm
SHELL=/bin/sh

if ! ps aux | grep -w "cmus$" | grep -v grep > /dev/null ; then
  ${TERMINAL} -e $SHELL -c cmus & > /dev/null
else
  cmus-remote -u
fi
