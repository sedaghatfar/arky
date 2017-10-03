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
import random
import requests
import logging
import traceback
import pytz

POST, PUT, GET = [], [], []

#################
## API methods ##
#################

def get(entrypoint, dic={}, **kw):
	"""
generic GET call using requests lib. It returns server response as dict object.
It uses default peers registered in SEEDS list.

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
	peer = args.pop("peer", False)
	args = dict([k.replace("and_", "AND:") if k.startswith("and_") else k, v] for k,v in args.items())
	try:
		text = requests.get(
			(peer if peer else random.choice(cfg.peers)) + entrypoint,
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
		if data["success"]:
			data = data[returnKey] if returnKey in data else data
	return data

def post(entrypoint, dic={}, **kw):
	# merge dic and kw values
	payload = dict(dic, **kw)
	# API response contains several fields and wanted one can be extracted using
	# a returnKey that match the field name
	returnKey = payload.pop("returnKey", False)
	peer = payload.pop("peer", False)
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
		sys.stdout.write(text + "\n")
		data = {"success":False, "error":error}
		if hasattr(error, "__traceback__"):
			data["details"] = "\n"+("".join(traceback.format_tb(error.__traceback__)).rstrip())
	return data

def put(entrypoint, dic={}, **kw):
	# merge dic and kw values
	payload = dict(dic, **kw)
	# API response contains several fields and wanted one can be extracted using
	# a returnKey that match the field name
	returnKey = payload.pop("returnKey", False)
	peer = payload.pop("peer", False)
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
		sys.stdout.write(text + "\n")
		data = {"success":False, "error":error}
		if hasattr(error, "__traceback__"):
			data["details"] = "\n"+("".join(traceback.format_tb(error.__traceback__)).rstrip())
	return data

def checkPeerLatency(peer):
	"""
	Return peer latency in seconds.
	"""
	try:
		r = requests.get(peer + '/api/blocks/getNethash', timeout=cfg.timeout)
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
		elem = path.split("/")
		end = elem[-1]
		path = "/".join(elem[:2])
		for name in elem[2:]:
			path += "/"+name
			if not hasattr(ndpt, name):
				setattr(ndpt, name, Endpoint(method, path))
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

	POST = Endpoint(post, "/api")
	for endpoint in endpoints["POST"]:
		POST.createEndpoint(POST, post, endpoint)

	PUT = Endpoint(put, "/api")
	for endpoint in endpoints["PUT"]:
		PUT.createEndpoint(PUT, put, endpoint)

	GET = Endpoint(get, "/api")
	for endpoint in endpoints["GET"]:
		GET.createEndpoint(GET, get, endpoint)

	return True

#######################
## network selection ##
#######################

def use(network, npeers=10, latency=0.5):
	networks = [os.path.splitext(name)[0] for name in os.listdir(ROOT) if name.endswith(".net")]

	if len(networks) and network in networks:
		# load json file
		in_ = open(os.path.join(ROOT, network+".net"), "r" if __PY3__ else "rb")
		data = json.load(in_)
		in_.close()
		# save json data as variables in cfg.py module
		cfg.__dict__.update(data)
		# for https uses
		cfg.verify = os.path.join(os.path.dirname(sys.executable), "cacert.pem") if __FROZEN__ else True
		# blockchain can use differents begin time
		cfg.begintime = slots.datetime.datetime(*cfg.begintime, tzinfo=slots.pytz.UTC)
		# create endpoints and load peers if seed is given

		if loadEndPoints(cfg.ndpt):
			cfg.headers["version"] = GET.peers.version(returnKey="version")
			cfg.headers["nethash"] = GET.blocks.getNethash(returnKey="nethash")
			cfg.network = network
			cfg.hotmode = True

			n, cfg.peers = 0, []
			for peer in data.get("peers", []):
				n += 1
				if checkPeerLatency(peer) < latency:
					cfg.peers.append("http://%s:%s"%(peer, cfg.port))
				if n >= npeers:
					break

	else:
		raise NetworkError("Unknown %s network properties" % network)
		cfg.network = "..."
		cfg.hotmode = False

	# update logger data so network appear on log
	logger = logging.getLogger()
	logger.handlers[0].setFormatter(logging.Formatter('[%s]'%network + '[%(asctime)s] %(message)s'))
