# -*- coding: utf-8 -*-
import subprocess


def notify(msg, expireTime=2000, urgency="normal"):
    subprocess.call(
        ["notify-send",
         "--urgency=%s" % (urgency),
         "--expire-time=%s" % (expireTime),
         "%s" % (msg)])

# noinspection PyUnusedLocal
class Py3status(object):
    def bat(self, json=None, i3status_config=None):
        # Design capacity 4343mAh
        # Battery 0: Unknown, 97%
        # Battery 0: Full, 100%
        # Battery 0: Discharging, 75%, 01:26:12 remaining
        # Battery 0: Charging, 82%, 00:14:58 until charged
        response = {'name': 'df_root'}
        output = subprocess.check_output(["acpi"]).strip()
        tokens = output.split(" ")
        if len(tokens) == 4:
            activity = tokens[2]
            percentage = int(tokens[-1][:-1])
            msg = "%s (%s%%)" % (activity[:-1].lower(), percentage)
        else:
            activity, percentage, time = tokens[2:5]
            activity = activity[:3].lower().strip()
            percentage = int(percentage[:-2])
            msg = "%s %s%% %s" % (activity, percentage, time)
        if i3status_config['colors']:
            if percentage > 40:
                response['color'] = i3status_config['color_good']
            elif percentage > 20:
                response['color'] = i3status_config['color_degraded']
            else:
                response['color'] = i3status_config['color_bad']
                if activity == "dis":
                    if percentage < 15:
                        notify("battery low - will shutdown soon ...",
                               expireTime=1000, urgency="critical")
                    if percentage < 8:
                        notify("!!!! WILL SHUTDOWN IN 60 SECONDS !!!!",
                               expireTime=60000, urgency="critical")
                        subprocess.call(["sudo", "shutdown", "-h", "+1"])
        response['full_text'] = msg if not "full" in msg else ""
        return (1, response)

    def cpuLoad(self, json=None, i3status_config=None):
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

    def avgTmp(self, json=None, i3status_config=None):
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

    def excuse(self, json=None, i3status_config=None):
        output = subprocess.check_output(["fortune", "bofh-excuses"])
        output = output.split(":")[1].replace("\n", " ")
        color = i3status_config['color_degraded']
        response = {'full_text': output, 'name': 'excuse'}
        return (0, response)


if __name__ == '__main__':
    i3status_config = {
        "colors": True,
        "color_good": "good",
        "color_degraded": "degraded",
        "color_bad": "bad"}

    def try_stuff():
        ps = Py3status()
        print "bat", ps.bat(i3status_config=i3status_config)
        print "load", ps.cpuLoad(i3status_config=i3status_config)
        print "avgTmp", ps.avgTmp(i3status_config=i3status_config)
        print "excuse", ps.excuse(i3status_config=i3status_config)

    try_stuff()
