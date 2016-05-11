import subprocess


class Py3status(object):
    # noinspection PyUnusedLocal
    def cpu_load(self, json=None, i3status_config=None):
        output = subprocess.check_output(["uptime"]).strip()
        tokens = output.split(" ")
        load1minute = float(tokens[-3][:-1].replace(",", "."))
        msg = "%0.2f" % (load1minute)
        response = {'full_text': msg, 'name': 'cpuLoad'}
        if i3status_config['colors']:
            if load1minute < 0.5:
                response['color'] = i3status_config['color_good']
            elif load1minute < 2:
                response['color'] = i3status_config['color_degraded']
            else:
                response['color'] = i3status_config['color_bad']
        return (2, response)
