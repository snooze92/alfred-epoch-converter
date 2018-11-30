# encoding: utf-8

import datetime
import subprocess
import sys
import time
from workflow import Workflow, ICON_CLOCK, ICON_NOTE

LOGGER = None # Set in the main...
MAX_SECONDS_TIMESTAMP = 10000000000
MAX_SUBSECONDS_ITERATION = 4


def get_divisor(timestamp):
    for power in range(MAX_SUBSECONDS_ITERATION):
        divisor = pow(1e3, power)
        if timestamp < MAX_SECONDS_TIMESTAMP * divisor:
            return divisor
    return 0


def convert(timestamp, converter):
    divisor = get_divisor(timestamp)
    LOGGER.debug('Found divisor [{divisor}] for timestamp [{timestamp}]'.format(**locals()))
    if divisor > 0:
        seconds, subseconds = divmod(timestamp, divisor)
        return '.'.join([converter(seconds).isoformat(), str(subseconds).rstrip('0').rstrip('.')]).rstrip('0').rstrip('.')


def add_conversion(wf, timestamp, descriptor, converter):
    converted = convert(timestamp, converter)
    description = descriptor + ' time for ' + str(timestamp)
    if converted is None:
        raise Exception('Timestamp [{timestamp}] is not supported'.format(**locals()))
    else:
        LOGGER.debug('Returning [{converted}] as [{description}] for [{timestamp}]'.format(**locals()))
        wf.add_item(title=converted, subtitle=description, arg=converted, valid=True, icon=ICON_CLOCK)


def add_current(wf, unit, multiplier):
    converted = str(int(time.time() * multiplier))
    description = 'Current timestamp ({unit})'.format(**locals())
    LOGGER.debug('Returning [{converted}] as [{description}]'.format(**locals()))
    wf.add_item(title=converted, subtitle=description, arg=converted, valid=True, icon=ICON_NOTE)


def get_clipboard_data():
    p = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE)
    exit_code = p.wait()
    return p.stdout.read()


def main(wf):
    if len(wf.args) > 0:
        query = wf.args[0]
        if query:
            LOGGER.debug('Got query [{query}]'.format(**locals()))
            timestamp = float(query)
            add_conversion(wf, timestamp, 'Local', datetime.datetime.fromtimestamp)
            add_conversion(wf, timestamp, 'UTC', datetime.datetime.utcfromtimestamp)

    clipboard = get_clipboard_data()
    if clipboard:
        LOGGER.debug('Got clipboard [{clipboard}]'.format(**locals()))
        try:
            timestamp = float(clipboard)
            add_conversion(wf, timestamp, '(clipboard) Local', datetime.datetime.fromtimestamp)
            add_conversion(wf, timestamp, '(clipboard) UTC', datetime.datetime.utcfromtimestamp)
        except:
            LOGGER.debug('Unable to convert clipboard [{clipboard}]')

    add_current(wf, 's', 1)
    add_current(wf, 'ms', 1e3)
    add_current(wf, 'us', 1e6)
    add_current(wf, 'ns', 1e9)

    wf.send_feedback()


if __name__ == u"__main__":
    wf = Workflow()
    LOGGER = wf.logger
    sys.exit(wf.run(main))