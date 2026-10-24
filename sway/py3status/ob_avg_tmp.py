# -*- coding: utf-8 -*-
import subprocess


class Py3status:
    """show averagy tmp"""
    # noinspection PyUnusedLocal
    def avg_tmp(self, json=None, i3status_config=None):
        output = subprocess.check_output(["acpi", "-t"]).strip()
        lines = output.splitlines()
        cumulatedTmp = 0
        color = i3status_config['color_good']
        numTmps = 0
        for line in lines:
            tokens = line.split(" ")
            state, tmp = tokens[2:4]
            tmpFloat = float(tmp)
            if state != "ok,":
                color = i3status_config['color_bad']
            if tmpFloat > 1.0:
                numTmps += 1
                cumulatedTmp += tmpFloat

        msg = "%s°" % (int(cumulatedTmp) / numTmps)
        response = {'full_text': msg, 'name': 'cpuTmp', 'color': color}
        return (5, response)
