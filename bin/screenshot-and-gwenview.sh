#!/usr/bin/env bash

filename="scrot-$(date +"%y-%m-%d-%T").png"
scrot "$HOME/$filename"
gwenview "$HOME/$filename"
