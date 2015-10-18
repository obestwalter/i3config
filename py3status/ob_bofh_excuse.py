# -*- coding: utf-8 -*-
import subprocess


# noinspection PyUnusedLocal
class Py3status(object):
    def bofh_excuse(self, json=None, i3status_config=None):
        output = subprocess.check_output(["fortune", "bofh-excuses"])
        output = output.split(":")[1].replace("\n", " ")
        color = i3status_config['color_degraded']
        response = {'full_text': output, 'name': 'excuse'}
        return (0, response)
