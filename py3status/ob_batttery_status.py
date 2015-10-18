# -*- coding: utf-8 -*-
import subprocess


# noinspection PyUnusedLocal
class Py3status(object):
    firstWarning = False
    secondWarning = False

    @staticmethod
    def _notify(msg, expireTime=2000, urgency="normal"):
        subprocess.call(
            ["notify-send",
             "--urgency=%s" % (urgency),
             "--expire-time=%s" % (expireTime),
             "%s" % (msg)])

    def battery_status(self, json=None, i3status_config=None):
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
                        self.firstWarning = True
                        self._notify("battery low - will shutdown soon ...",
                                     expireTime=1000, urgency="critical")
                    if percentage < 8:
                        self.secondWarning = True
                        self._notify("!!!! WILL SHUTDOWN IN 60 SECONDS !!!!",
                                     expireTime=60000, urgency="critical")
                        subprocess.call(["sudo", "shutdown", "-h", "+1"])
        response['full_text'] = msg if "full" not in msg else ""
        return (1, response)
