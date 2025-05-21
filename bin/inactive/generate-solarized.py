#!/usr/bin/env python

base03  = '002b36'
base02  = '073642'
base01  = '586e75'
base00  = '657b83'
base0   = '839496'
base1   = '93a1a1'
base2   = 'eee8d5'
base3   = 'fdf6e3'
yellow  = 'b58900'
orange  = 'cb4b16'
red     = 'dc322f'
magenta = 'd33682'
violet  = '6c71c4'
blue    = '268bd2'
cyan    = '2aa198'
green   = '859900'


BACKGROUND = base03
COLOR = base01
TITLE = base1
TITLE_BORDER = base0
ACTIVE = base1


def rebase(rebase03, rebase02, rebase01, rebase00,
           rebase0, rebase1, rebase2, rebase3):
    BACKGROUND = rebase03
    COLOR = rebase0
    TITLE = rebase1
    TITLE_BORDER = rebase0
    ACTIVE = rebase1


def accentize(accent):
    ACTIVE = accent
    COLOR = accent


def light():
    rebase(base3, base2, base1, base0, base00, base01, base02, base03)


def dark():
    rebase(base03, base02, base01, base00, base0, base1, base2, base3)

