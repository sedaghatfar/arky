# -*- encoding: utf8 -*-
# © Toons

from .. import __PY3__
from .. import util
from .. import rest
from .. import cfg
from .. import util

from . import crypto

import sys
import random
import threading


def selectPeers():
	version = rest.GET.api.peers.version().get("version", "0.0.0")
	height = rest.GET.api.blocks.getHeight().get("height", 0)

	peers = rest.GET.peer.list().get("peers", [])
	good_peers = []
	for peer in peers:
		if (
			peer.get("delay", 6000) <= cfg.timeout * 1000 and peer.get("version") == version and
			peer.get("height", -1) > height - 10
		):
			good_peers.append(peer)

	good_peers = sorted(good_peers, key=lambda e: e["delay"])

	selection = []
	while(len(selection) < min(cfg.broadcast, len(good_peers))):
		peer = "http://{ip}:{port}".format(**good_peers[len(selection)])
		if rest.checkPeerLatency(peer):
			selection.append(peer)

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
		threading.Thread(target=selectPeers).start()
		@util.setInterval(30)
		def rotatePeers(): selectPeers()
		DAEMON_PEERS = rotatePeers()
	else:
		sys.stdout.write(("%s\n" % resp.get("error", "...")).encode("ascii", errors="replace").decode())
		raise Exception("Initialization error with peer %s" % resp.get("peer", "???"))


def sendPayload(*payloads):
	success, msgs, ids = 0, set([]), set([])

	for peer in cfg.peers:
		resp = rest.POST.peer.transactions(peer=peer, transactions=payloads)
		success += 1 if resp["success"] else 0
		if "message" in resp: msgs.update([resp["message"]])
		if "transactionIds" in resp: ids.update(resp["transactionIds"])

	return {
		"success": "%.1f%%" % (100.*success/len(cfg.peers)),
		"transactions": list(ids),
		"messages": list(msgs)
	}


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
