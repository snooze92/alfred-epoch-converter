#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Partly cloudy ⛅️  🌡️+48°F (feels +45°F, 56%) 🌬️→7mph 🌗 Sat Mar 26 10:55:59 2022


import datetime
import re
import subprocess
import sys
import time
import json
import importlib

importlib.reload(sys) #not sure this is needed.



#sys.setdefaultencoding('utf-8')

MAX_SECONDS_TIMESTAMP = 10000000000
MAX_SUBSECONDS_ITERATION = 4
result = {"items": []}

def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


def get_divisor(timestamp):
    for power in range(MAX_SUBSECONDS_ITERATION):
        divisor = pow(1e3, power)
        if timestamp < MAX_SECONDS_TIMESTAMP * divisor:
            return int(divisor)
    return 0


def convert(timestamp, converter):
    divisor = get_divisor(timestamp)
    log('Found divisor [{divisor}] for timestamp [{timestamp}]'.format(**locals()))
    if divisor > 0:
        seconds, subseconds = divmod(timestamp, divisor)
        subseconds_str = '{:.9f}'.format(subseconds / float(divisor))
        return converter(seconds).isoformat() + subseconds_str[1:].rstrip('0').rstrip('.')


def add_epoch_to_time_conversion(timestamp, descriptor, converter):
    converted = convert(timestamp, converter)
    description = descriptor + ' time for ' + str(timestamp)
    if converted is None:
        raise Exception('Timestamp [{timestamp}] is not supported'.format(**locals()))
    else:
        log('Returning [{converted}] as [{description}] for [{timestamp}]'.format(**locals()))
        result["items"].append({
        "title": converted,
        'subtitle': description,
        'valid': True,
        
        "icon": {
            "path": 'icons/Clock.icns'
        },
        'arg': converted
            }) 
        
def add_time_to_epoch_conversion(dt, descriptor, converter, multiplier):
    converted = str(int((dt - converter(0)).total_seconds() * multiplier))
    description = descriptor + ' epoch for ' + str(dt)
    result["items"].append({
        "title": converted,
        'subtitle': description,
        'valid': True,
        
        "icon": {
            "path": 'icons/Clock.icns'
        },
        'arg': converted
            }) 

    

def attempt_conversions(input, prefix=''):
    try:
        timestamp = float(input)
        add_epoch_to_time_conversion(timestamp, '{prefix}Local'.format(**locals()), datetime.datetime.fromtimestamp)
        add_epoch_to_time_conversion(timestamp, '{prefix}UTC'.format(**locals()), datetime.datetime.utcfromtimestamp)
    except:
        log('Unable to read [{input}] as an epoch timestamp'.format(**locals()))

    try:
        match = re.match('(\d{4}-\d{2}-\d{2})?[ T]?((\d{2}:\d{2})(:\d{2})?(.\d+)?)?', str(input))
        date, time, hour_minutes, seconds, subseconds = match.groups()
        if date or time:
                dt = datetime.datetime.strptime(
                (date or datetime.datetime.now().strftime('%Y-%m-%d')) + ' ' +
                (hour_minutes or '00:00') + (seconds or ':00') +
                ('.000000' if subseconds is None else subseconds[:7]),
                '%Y-%m-%d %H:%M:%S.%f'
                )

                add_time_to_epoch_conversion(dt, '{prefix}Local s.'.format(**locals()), datetime.datetime.fromtimestamp, 1)
                add_time_to_epoch_conversion(dt, '{prefix}Local ms.'.format(**locals()), datetime.datetime.fromtimestamp, 1e3)
                add_time_to_epoch_conversion(dt, '{prefix}Local us.'.format(**locals()), datetime.datetime.fromtimestamp, 1e6)
                add_time_to_epoch_conversion(dt, '{prefix}Local ns.'.format(**locals()), datetime.datetime.fromtimestamp, 1e9)

                add_time_to_epoch_conversion(dt, '{prefix}UTC s.'.format(**locals()), datetime.datetime.utcfromtimestamp, 1)
                add_time_to_epoch_conversion(dt, '{prefix}UTC ms.'.format(**locals()), datetime.datetime.utcfromtimestamp, 1e3)
                add_time_to_epoch_conversion(dt, '{prefix}UTC us.'.format(**locals()), datetime.datetime.utcfromtimestamp, 1e6)
                add_time_to_epoch_conversion(dt, '{prefix}UTC ns.'.format(**locals()), datetime.datetime.utcfromtimestamp, 1e9)
    except:
        log('Unable to read [{input}] as a human-readable datetime'.format(**locals()))


def add_current(unit, multiplier):
    converted = str(int(time.time() * multiplier))
    description = 'Current timestamp ({unit})'.format(**locals())
    log('Returning [{converted}] as [{description}]'.format(**locals()))
    result["items"].append({
        "title": converted,
        'subtitle': description,
        'valid': True,
        
        "icon": {
            "path": 'icons/AlertNoteIcon.icns'
        },
        'arg': converted
            }) 
    


def get_clipboard_data():
    p = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE)
    exit_code = p.wait()
    return p.stdout.read()


def main():
    if len(sys.argv) > 1:
        query = sys.argv[1]
        if query:
            log('Got query [{query}]'.format(**locals()))
            attempt_conversions(query)
            

    clipboard = get_clipboard_data()
    if clipboard:
        log('Got clipboard [{clipboard}]'.format(**locals()))
        attempt_conversions(clipboard, prefix='(clipboard) ')

    add_current('s', 1)
    add_current('ms', 1e3)
    add_current('µs', 1e6)
    add_current('ns', 1e9)
    print (json.dumps(result))
    


if __name__ == u"__main__":
    main ()