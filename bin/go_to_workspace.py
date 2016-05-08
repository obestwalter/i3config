#!/usr/bin/python3
import subprocess
import sys

data = sys.stdin.readlines()[0]
test = subprocess.Popen(["i3-msg","workspace "+data], stdout=subprocess.PIPE)