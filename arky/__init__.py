# -*- encoding: utf8 -*-
# © Toons
__version__ = "1.0a"

import os
import imp
import sys
import logging
import requests
import threading

__PY3__ = True if sys.version_info[0] >= 3 else False
__FROZEN__ = hasattr(sys, "frozen") or hasattr(sys, "importers") or imp.is_frozen("__main__")

# ROOT is the folder containing the __inti__.py file or the frozen executable
ROOT = os.path.normpath(os.path.abspath(os.path.dirname(sys.executable if __FROZEN__ else __file__)))
#
try:
	HOME = os.path.join(os.environ["HOMEDRIVE"], os.environ["HOMEPATH"])
except:
	HOME = os.environ.get("HOME", ROOT)

logging.getLogger('requests').setLevel(logging.CRITICAL)
logging.basicConfig(
	filename  = os.path.normpath(
		os.path.join(ROOT, __name__+".log")) if __FROZEN__ else \
		os.path.normpath(os.path.join(HOME, "."+__name__)
	),
	format = '[...][%(asctime)s] %(message)s',
	level = logging.INFO,
)

def setInterval(interval):
	""" threaded decorator
	>>> @setInterval(10)
	... def tick(): print("Tick")
	>>> stop = tick() # print 'Tick' every 10 sec
	>>> type(stop)
	<class 'threading.Event'>
	>>> stop.set() # stop printing 'Tick' every 10 sec
	"""
	def decorator(function):
		def wrapper(*args, **kwargs):
			stopped = threading.Event()
			def loop(): # executed in another thread
				while not stopped.wait(interval): # until stopped
					function(*args, **kwargs)
			t = threading.Thread(target=loop)
			t.daemon = True # stop if the program exits
			t.start()
			return stopped
		return wrapper
	return decorator
