#!/usr/bin/python
#
# pomodoro_daily_chart.py
# 
# Author: Brett Hutley <brett@hutley.net>
#
# This code is to extract the list of Pomodoros from my Mac OS/X calendar
# using the program 'callistevents' https://github.com/bhutley/callistevents
# and then create a bar-chart aggregating the work done each hour, in order
# to show how my productivity looks during the day.
# 
# It will create a chart called prod_YYYY-MM-DD.png in the current directory.
import os, sys
import subprocess
import datetime

# This is the path to the callistevents program
callistevents_prog = os.path.expanduser('~/my/bin/callistevents')

time_buckets = [0.0 for i in xrange(0, 24)]

colours_to_use = [
    '#000000',
    '#990000',
    '#CC0000',
    '#994C00',
    '#CC6600',
    '#999900',
    '#FFFF00',
    '#009900',
    '#00CC00',
    '#00FF00',
    '#33FF33',
]

start_date = datetime.date.today()
start_date_str = ("%d-%02d-%02d" % (start_date.year, start_date.month, start_date.day, ))
p = subprocess.Popen([callistevents_prog, '-c', 'Pomodoros', '-s', start_date_str ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()
lines = out.split("\n")
for line in lines:
    fields = line.split("\t")
    if len(fields) >= 3:
        sta = fields[1]
        end = fields[2]

        if len(sta) == 16 and len(end) == 16:
            sta_hr = int(sta[11:13])
            sta_mn = int(sta[14:])

            end_hr = int(end[11:13])
            end_mn = int(end[14:])

            if sta_hr == end_hr:
                mins = end_mn - sta_mn
                time_buckets[sta_hr] += float(mins) / 60.0
            else:
                for h in xrange(sta_hr, end_hr+1):
                    if h == sta_hr:
                        mins = 60.0 - sta_mn
                        time_buckets[sta_hr] += float(mins) / 60.0
                    elif h == end_hr:
                        mins = end_mn
                        time_buckets[end_hr] += float(mins) / 60.0
                    else:
                        time_buckets[h] += 1.0

## OK, the code following is for generating the plot.
# The code above has no dependencies on matplotlib

import numpy as n
from pylab import figure, show
import matplotlib.cm as cm
import matplotlib.colors as colors

width = 1.0
fig = figure()
ax = fig.add_subplot(111)
rects1 = ax.bar(xrange(0, 24), time_buckets, width,
                    color='r')

cc = colors.ColorConverter()
for i in xrange(0, len(time_buckets)):
    offset = int(round(time_buckets[i] * 10.0))
    if offset >= len(colours_to_use):
        offset = len(colours_to_use)-1
    r = rects1[i]
    r.set_color( cc.to_rgb(colours_to_use[offset]) )


ax.set_ylabel('Productivity')
ax.set_xlabel('Hour')
ax.set_title('Productivity for %s' % (start_date_str, ))
ax.set_axis_bgcolor('#EEE9E9')
ax.set_ylim(0, 1.0)
ax.set_xticks(xrange(0, 24))

fig.savefig("prod_%s.png" % (start_date_str, ), format="png")
