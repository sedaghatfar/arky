# -*- encoding: utf8 -*-
# © Toons

from . import __PY3__
from . import __FROZEN__
from . import ROOT
from . import HOME

if not __PY3__:
	import cfg
	import slots
else:
	from . import cfg
	from . import slots

import io
import os
import sys
import json
import pytz
import random
import logging
import requests
import traceback

#################
## API methods ##
#################

def get(entrypoint, dic={}, **kw):
	"""
generic GET call using requests lib. It returns server response as dict object.
It uses default peers registered in cfg.peers list.

Argument:
entrypoint (str) -- entrypoint url path

Keyword argument:
dic (dict) -- api parameters as dict type
**kw       -- api parameters as keyword argument (overwriting dic ones)

Returns dict
"""
	# merge dic and kw values
	args = dict(dic, **kw)
	# API response contains several fields and wanted one can be extracted using
	# a returnKey that match the field name
	returnKey = args.pop("returnKey", False)
	args = dict([k.replace("and_", "AND:") if k.startswith("and_") else k, v] for k,v in args.items())
	try:
		text = requests.get(
			random.choice(cfg.peers) + entrypoint,
			params=args,
			headers=cfg.headers,
			verify=cfg.verify,
			timeout=cfg.timeout
		).text
		data = json.loads(text)
	except Exception as error:
		data = {"success":False, "error":error}
		if hasattr(error, "__traceback__"):
			data["details"] = "\n"+("".join(traceback.format_tb(error.__traceback__)).rstrip())
	else:
		if data.get("success", False):
			data = data[returnKey] if returnKey in data else data
	return data

def post(entrypoint, dic={}, **kw):
	# merge dic and kw values
	peer = kw.pop("peer", False)
	payload = dict(dic, **kw)
	try:
		text = requests.post(
			(peer if peer else random.choice(cfg.peers)) + entrypoint,
			data=json.dumps(payload),
			headers=cfg.headers,
			verify=cfg.verify,
			timeout=cfg.timeout
		).text
		data = json.loads(text)
	except Exception as error:
		data = {"success":False, "error":error}
		if hasattr(error, "__traceback__"):
			data["details"] = "\n"+("".join(traceback.format_tb(error.__traceback__)).rstrip())
	return data

def put(entrypoint, dic={}, **kw):
	# merge dic and kw values
	peer = kw.pop("peer", False)
	payload = dict(dic, **kw)
	try:
		text = requests.put(
			(peer if peer else random.choice(cfg.peers)) + entrypoint,
			data=json.dumps(payload),
			headers=cfg.headers,
			verify=cfg.verify,
			timeout=cfg.timeout
		).text
		data = json.loads(text)
	except Exception as error:
		data = {"success":False, "error":error}
		if hasattr(error, "__traceback__"):
			data["details"] = "\n"+("".join(traceback.format_tb(error.__traceback__)).rstrip())
	return data

def checkPeerLatency(peer):
	"""
	Return peer latency in seconds.
	"""
	try:
		r = requests.get(peer, timeout=cfg.timeout)
	except:
		return False
	else:
		return r.elapsed.total_seconds()

#################
## API wrapper ##
#################

class Endpoint:
	
	def __init__(self, method, endpoint):
		self.method = method
		self.endpoint = endpoint

	def __call__(self, dic={}, **kw):
		return self.method(self.endpoint, dic, **kw)

	@staticmethod
	def createEndpoint(ndpt, method, path):
		newpath = ""
		for name in [e for e in path.split("/") if e != ""]:
			newpath += "/"+name
			if not hasattr(ndpt, name):
				setattr(ndpt, name, Endpoint(method, newpath))
			ndpt = getattr(ndpt, name)

def loadEndPoints(network):
	global POST, PUT, GET

	try:
		in_ = io.open(os.path.join(ROOT, "ndpt", "%s.ndpt"%network), "r" if __PY3__ else "rb")
		endpoints = json.load(in_)
		in_.close()
	except FileNotFoundError:
		sys.stdout.write("No endpoints file found\n")
		return False

	POST = Endpoint(post, "")
	for endpoint in endpoints["POST"]:
		POST.createEndpoint(POST, post, endpoint)

	PUT = Endpoint(put, "")
	for endpoint in endpoints["PUT"]:
		PUT.createEndpoint(PUT, put, endpoint)

	GET = Endpoint(get, "")
	for endpoint in endpoints["GET"]:
		GET.createEndpoint(GET, get, endpoint)

	return True

#######################
## network selection ##
#######################

def load(name):
	# try to stop _daemon from a previous use of ark blockchain familly
	try:
		sys.modules[__package__].core._daemon.set()
		# print("%r set"%sys.modules[__package__].core._daemon)
	except:
		pass
		# print("error :(")
	# loads blockchain familly package into as arky core
	sys.modules[__package__].core = __import__("%s.%s"%(__package__, name), globals(), locals(), ["*"], 0)
	# initialize blockchain familly package
	try:
		sys.modules[__package__].core.init()
	except AttributeError:
		raise Exception("%s package is not a valid blockchain familly" % name)
	# delete real package name loaded (to keep namespace clear)
	try:
		sys.modules[__package__].__delattr__(name)
	except AttributeError:
		pass

def use(network):
	networks = [os.path.splitext(name)[0] for name in os.listdir(ROOT) if name.endswith(".net")]

	if len(networks) and network in networks:
		# load json file
		with open(os.path.join(ROOT, network+".net"), "r" if __PY3__ else "rb") as _in:
			data = json.load(_in)
		# save json data as variables in cfg.py module
		cfg.__dict__.update(data)
		# for https uses
		cfg.verify = os.path.join(os.path.dirname(sys.executable), "cacert.pem") if __FROZEN__ else True
		# blockchain can use differents begin time
		cfg.begintime = slots.datetime.datetime(*cfg.begintime, tzinfo=slots.pytz.UTC)
		# build peers
		if data.get("seeds", []):
			cfg.peers = cfg.seeds
		else:
			n, cfg.peers = 0, []
			for peer in data.get("peers", []):
				n += 1
				peer = "http://%s:%s"%(peer, data.get("port", 22))
				if checkPeerLatency(peer) < cfg.timeout:
					cfg.peers.append(peer)
				if n >= cfg.broadcast:
					break
		# if endpoints found, create them and update network
		if loadEndPoints(cfg.endpoints):
			load(cfg.familly)
			cfg.network = network
			cfg.hotmode = True
	else:
		cfg.network = "..."
		cfg.hotmode = False
		try:
			sys.modules[__package__].__delattr__(name)
		except AttributeError:
			pass
		raise NetworkError("Unknown %s network properties" % network)

	# update logger data so network appear on log
	logger = logging.getLogger()
	logger.handlers[0].setFormatter(logging.Formatter('[%s]'%network + '[%(asctime)s] %(message)s'))
