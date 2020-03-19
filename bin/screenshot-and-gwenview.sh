#!/usr/bin/env bash

filename="scrot-$(date +"%y-%m-%d-%H-%M-%S").png"
scrot "$HOME/$filename"
gwenview "$HOME/$filename"
