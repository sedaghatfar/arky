# -*- encoding: utf8 -*-
# © Toons

from .. import rest
from .. import cfg
from .. import util

from . import crypto

import sys
import threading


def selectPeers():
	selection = []
	for seed in cfg.seeds:
		if rest.checkPeerLatency(seed):
			selection.append(seed)
	if len(selection):
		cfg.peers = selection


def init():
	global DAEMON_PEERS
	resp = rest.GET.api.blocks.getNethash()
	if resp["success"]:
		cfg.headers["version"] = "%s" % rest.GET.api.peers.version(returnKey="version")
		cfg.headers["nethash"] = resp["nethash"]
		cfg.fees = rest.GET.api.blocks.getFees(returnKey="fees")
		threading.Thread(target=selectPeers).start()
		@util.setInterval(30)
		def rotatePeers(): selectPeers()
		DAEMON_PEERS = rotatePeers()
	else:
		sys.stdout.write(("%s\n" % resp.get("error", "...")).encode("ascii", errors="replace").decode())
		raise Exception("Initialization error with peer %s" % resp.get("peer", "???"))


def sendTransaction(**kw):
	tx = crypto.bakeTransaction(**dict([k,v] for k,v in kw.items() if v))
	result = rest.POST.peer.transactions(transactions=[tx])
	if result["success"]:
		result["id"] = tx["id"]
	return result


def sendPayload(*payloads):
	result = rest.POST.peer.transactions(transactions=payloads)
	if result["success"]:
		result["id"] = [tx["id"] for tx in payloads]
	return result


#######################
## basic transaction ##
#######################

def sendToken(amount, recipientId, secret, secondSecret=None):
	return sendTransaction(
		amount=amount,
		recipientId=recipientId,
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
		asset={"delegate":{"username":username, "publicKey":publicKey}}
	)

def upVoteDelegate(usernames, secret, secondSecret=None):
	keys = crypto.getKeys(secret)
	return sendTransaction(
		type=3,
		publicKey=keys["publicKey"],
		privateKey=keys["privateKey"],
		recipientId=crypto.getAddress(keys["publicKey"]),
		secondSecret=secondSecret,
		asset={"votes":["+%s"%pk for pk in util.getDelegatesPublicKeys(*usernames)]}
	)

def downVoteDelegate(usernames, secret, secondSecret=None):
	keys = crypto.getKeys(secret)
	return sendTransaction(
		type=3,
		publicKey=keys["publicKey"],
		privateKey=keys["privateKey"],
		recipientId=crypto.getAddress(keys["publicKey"]),
		secondSecret=secondSecret,
		asset={"votes":["-%s"%pk for pk in util.getDelegatesPublicKeys(*usernames)]}
	)
