# -*- encoding: utf8 -*-
# © Toons

from . import __PY3__

if not __PY3__:
	import cfg
else:
	from . import cfg

import datetime
import pytz

def getTimestamp(**kw):
	delta = datetime.timedelta(**kw)
	return getTime(datetime.datetime.now(pytz.UTC) - delta)

def getTime(time=None):
	delta = (datetime.datetime.now(pytz.UTC) if not time else time) - cfg.begintime
	return delta.total_seconds()

def getRealTime(epoch=None):
	epoch = getTime() if epoch == None else epoch
	return cfg.begintime + datetime.timedelta(seconds=epoch)
