import math
from datetime import datetime, timedelta


TIMEDELTA = timedelta(hours=6)
LONG_DATE_FORMAT = '%A, %d %b %Y - %H:%M'
SERVER_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def dt_to_string(time, now=datetime.now()):
    ret = datetime.strptime(time.strip(), SERVER_DATE_FORMAT)
    ret = ret + TIMEDELTA
    delta = now - ret
    return f'{ret.strftime(LONG_DATE_FORMAT)} ({delta_to_ago(delta)})'

def dt_format(dt):
    return datetime.fromtimestamp(dt).strftime(LONG_DATE_FORMAT)

def delta_to_ago(delta):
    h = math.floor(delta.seconds / 3600)
    m = math.floor((delta.seconds % 3600) / 60)
    return f'{h}h {m}m ago'