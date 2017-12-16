# -*- encoding: utf8 -*-
# © Toons

from .. import __PY3__
from .. import util
from .. import rest
from .. import cfg
from .. import util

from . import crypto

import sys, random


def selectPeers():
	version = rest.GET.api.peers.version().get("version", "0.0.0")
	peers = [p for p in rest.GET.api.peers().get("peers", []) if p.get("status", "") == "OK" \
	                                                             and p.get("delay", 6000) <= cfg.timeout*1000 \
			                                                     and p.get("version", "") == version]
	selection = []
	for i in range(min(cfg.broadcast, len(peers))):
		selection.append("http://%(ip)s:%(port)s" % random.choice(peers))
	if len(selection):
		cfg.peers = selection


def init():
	global DAEMON_PEERS
	resp = rest.GET.api.loader.autoconfigure()
	if resp["success"]:
		network = resp["network"]
		cfg.headers["version"] = "%s" % network.pop("version")
		cfg.headers["nethash"] = network.pop("nethash")
		cfg.__dict__.update(network)
		cfg.fees = rest.GET.api.blocks.getFees(returnKey="fees")
		# manage peers for tx broadcasting
		selectPeers()
		@util.setInterval(8*51)
		def rotatePeers():
			selectPeers()
		DAEMON_PEERS = rotatePeers()
	else:
		sys.stdout.write(("%s\n" % resp.get("error", "...")).encode("ascii", errors="replace").decode())
		raise Exception("Initialization error with peer %s" % resp.get("peer", "???"))


def sendPayload(*payloads):
	result = rest.POST.peer.transactions(peer=cfg.peers[0], transactions=payloads)
	success = 1 if result["success"] else 0
	for peer in cfg.peers[1:]:
		if rest.POST.peer.transactions(peer=peer, transactions=payloads)["success"]:
			success += 1
	if success > 0:
		result["success"] = True
		result.pop("error", None)
		result.pop("message", None)
	result["broadcast"] = "%.1f%%" % (100.*success/len(cfg.peers))
	return result


# This function is a high-level broadcasting for a single tx
def sendTransaction(**kw):
	tx = crypto.bakeTransaction(**dict([k,v] for k,v in kw.items() if v))
	return sendPayload(tx)


#######################
## basic transaction ##
#######################

def sendToken(amount, recipientId, secret, secondSecret=None, vendorField=None):
	return sendTransaction(
		amount=amount,
		recipientId=recipientId,
		vendorField=vendorField,
		secret=secret,
		secondSecret=secondSecret
	)

def registerSecondPublicKey(secondPublicKey, secret, secondSecret=None):
	keys = crypto.getKeys(secret)
	return sendTransaction(
		type=1,
		publicKey=keys["publicKey"],
		privateKey=keys["privateKey"],
		secondSecret=secondSecret,
		asset={"signature":{"publicKey":secondPublicKey}}
	)

def registerSecondPassphrase(secondPassphrase, secret, secondSecret=None):
	secondKeys = crypto.getKeys(secondPassphrase)
	return registerSecondPublicKey(secondKeys["publicKey"], secret, secondSecret)

def registerDelegate(username, secret, secondSecret=None):
	keys = crypto.getKeys(secret)
	return sendTransaction(
		type=2,
		publicKey=keys["publicKey"],
		privateKey=keys["privateKey"],
		secondSecret=secondSecret,
		asset={"delegate":{"username":username, "publicKey":keys["publicKey"]}}
	)

def upVoteDelegate(usernames, secret, secondSecret=None):
	keys = crypto.getKeys(secret)
	req = rest.GET.api.delegates.get(username=usernames[-1])
	if req["success"]:
		return sendTransaction(
			type=3,
			publicKey=keys["publicKey"],
			recipientId=crypto.getAddress(keys["publicKey"]),
			privateKey=keys["privateKey"],
			secondSecret=secondSecret,
			asset={"votes":["+%s"%req["delegate"]["publicKey"]]}
		)

def downVoteDelegate(usernames, secret, secondSecret=None):
	keys = crypto.getKeys(secret)
	req = rest.GET.api.delegates.get(username=usernames[-1])
	if req["success"]:
		return sendTransaction(
			type=3,
			publicKey=keys["publicKey"],
			recipientId=crypto.getAddress(keys["publicKey"]),
			privateKey=keys["privateKey"],
			secondSecret=secondSecret,
			asset={"votes":["-%s"%req["delegate"]["publicKey"]]}
		)
