# -*- coding: utf-8 -*-
import subprocess


def df_free(path):
    output = subprocess.check_output(["df", path, "-H"]).strip()
    tokens = output.split(" ")
    tokens = [t for t in tokens if t]
    free, percentage = tokens[-3:-1]
    return (free, percentage)


# noinspection PyUnusedLocal
class Py3status(object):
    # def vpn(self, json=None, i3status_config=None):
    #     vpnRunning = os.path.exists("/var/run/openvpn.pid")
    #     if not vpnRunning:
    #         return (0, {'full_text': "", 'name': 'vpn'})
    #
    #     response = {'full_text': "##VPN ACTIVE##", 'name': 'vpn'}
    #     if i3status_config['colors']:
    #         response['color'] = "#DD55CC"
    #     return (0, response)

    # def dhcp(self, json=None, i3status_config=None):
    #     dhcLientRunning = os.path.exists("/var/run/dhclient.pid")
    #     if dhcLientRunning:
    #         return
    #
    #     response = {'full_text': "DHCLIENT DOWN", 'name': 'dhClient'}
    #     if i3status_config['colors']:
    #         response['color'] = i3status_config['color_bad']
    #     return (0, response)

    def net(self, json=None, i3status_config=None):
        # todo check for eth0 first (ifconfig eth0 or ip addr)
        # todo get ip addrs
        # ip -o -f inet addr
        # ip -o -f inet6 addr

        stdout = subprocess.check_output(["iwconfig", "wlan0"])
        tokens = [t for t in stdout.split("  ") if t]
        elems = {}
        color = i3status_config['color_bad']
        for token in tokens:
            if "ESSID:" in token:
                elems["essid"] = token.split(":")[-1].strip()[1:-1]
            if "Bit Rate=" in token:
                elems["bitrate"] = token.split("=")[-1].strip()
            if "Link Quality=" in token:
                z, n = token.split("=")[-1].strip().split("/")
                percentage = int(z) * 100 / int(n)
                elems["quality"] = "%s%%" % (percentage)
                if percentage > 65:
                    color = i3status_config['color_good']
                else:
                    color = i3status_config['color_degraded']
        if len(elems) != 3:
            return

        msg = "%(essid)s %(bitrate)s %(quality)s" % (elems)
        response = {'full_text': msg, 'name': 'wlan'}
        if i3status_config['colors']:
            response['color'] = color
        return (1, response)

    def bat(self, json=None, i3status_config=None):
        # Design capacity 4343mAh
        # Battery 0: Unknown, 97%
        # Battery 0: Full, 100%
        # Battery 0: Discharging, 75%, 01:26:12 remaining
        # Battery 0: Charging, 82%, 00:14:58 until charged
        output = subprocess.check_output(["acpi"]).strip()
        tokens = output.split(" ")
        if len(tokens) == 4:
            activity = tokens[2]
            percentage = int(tokens[-1][:-1])
            msg = "%s (%s%%)" % (activity[:-1].lower(), percentage)
        else:
            activity, percentage, time = tokens[2:5]
            activity = activity[:3].lower()
            percentage = int(percentage[:-2])
            msg = "%s %s%% %s" % (activity, percentage, time)
        response = {'full_text': msg, 'name': 'df_root'}
        if i3status_config['colors']:
            if  percentage > 40:
                response['color'] = i3status_config['color_good']
            elif  percentage > 10:
                response['color'] = i3status_config['color_degraded']
            else:
                response['color'] = i3status_config['color_bad']
                if activity == "dis":
                    warnbar = "###" * (20 - percentage)
                    msg = "%s %s %s" % (warnbar, msg, warnbar)
        return (1, response)

    # def disk(self, json=None, i3status_config=None):
    #     rootFree, rootPerc = df_free("/")
    #     homeFree, homePerc = df_free("/home/obestwalter")
    #     lowestPerc = min(rootPerc, homePerc)
    #     msg = "/".join([rootFree, homeFree])
    #     response = {'full_text': msg, 'name': 'df_root'}
    #     if i3status_config['colors']:
    #         if lowestPerc < 10:
    #             response['color'] = i3status_config['color_degraded']
    #         else:
    #             response['color'] = i3status_config['color_good']
    #
    #     return (2, response)

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

    # def maxTmp(self, json=None, i3status_config=None):
    #     output = subprocess.check_output(["acpi", "-t"]).strip()
    #     lines = output.splitlines()
    #     maxTmp = 0
    #     color = i3status_config['color_good']
    #     for line in lines:
    #         tokens = line.split(" ")
    #         state, tmp = tokens[2:4]
    #         tmpFloat = float(tmp)
    #         if tmpFloat > maxTmp:
    #             maxTmp = tmpFloat
    #         if state != "ok,":
    #             color = i3status_config['color_bad']
    #
    #     msg = "%s°" % (int(maxTmp))
    #     response = {'full_text': msg, 'name': 'cpuTmp', 'color': color}
    #     return (5, response)

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

    # def excuse(self, json=None, i3status_config=None):
    #     output = subprocess.check_output(["fortune", "bofh-excuses"])
    #     output = output.split(":")[1].replace("\n", " ")
    #     color = i3status_config['color_degraded']
    #     response = {'full_text': output, 'name': 'excuse'}
    #     return (0, response)


if __name__ == '__main__':
    i3status_config = {
        "colors": True,
        "color_good": "good",
        "color_degraded": "degraded",
        "color_bad": "bad"}

    def try_stuff():
        ps = Py3status()
        #print "bat", ps.bat(i3status_config=i3status_config)
        #print "load", ps.cpuLoad(i3status_config=i3status_config)
        #print "dhcp", ps.dhcp(i3status_config=i3status_config)
        #print "maxTmp", ps.maxTmp(i3status_config=i3status_config)
        print "avgTmp", ps.avgTmp(i3status_config=i3status_config)
        #print "disk", ps.disk(i3status_config=i3status_config)
        print "net", ps.net(i3status_config=i3status_config)
        #print "vpn", ps.vpn(i3status_config=i3status_config)
        # print "excuse", ps.excuse(i3status_config=i3status_config)

    try_stuff()
