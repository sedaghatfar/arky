# -*- encoding: utf8 -*-
# © Toons

from .. import rest
from .. import cfg

from . import crypto

def init():
	cfg.headers["version"] = rest.GET.api.peers.version(returnKey="version")
	cfg.headers["nethash"] = rest.GET.api.blocks.getNethash(returnKey="nethash")
	cfg.fees = rest.GET.api.blocks.getFees(returnKey="fees")

def sendTransaction(**kw):
	tx = crypto.bakeTransaction(**dict([k,v] for k,v in kw.items() if v))
	result = rest.POST.peer.transactions(transactions=[tx])
	if result["success"]:
		result["id"] = tx["id"]
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
	publicKey, privateKey = crypto.getKeys(secret)
	return sendTransaction(
		type=1,
		publicKey=publicKey,
		privateKey=privateKey,
		secondSecret=secondSecret,
		asset={"signature":{"publicKey":secondPublicKey}}
	)

def registerSecondPassphrase(secondPassphrase, secret, secondSecret=None):
	secondPublicKey, secondPrivateKey = crypto.getKeys(secondPassphrase)
	return registerSecondPublicKey(secondPublicKey, secret, secondSecret)

def registerDelegate(username, secret, secondSecret=None):
	publicKey, privateKey = crypto.getKeys(secret)
	return sendTransaction(
		type=2,
		publicKey=publicKey,
		privateKey=privateKey,
		secondSecret=secondSecret,
		asset={"delegate":{"username":username, "publicKey":publicKey}}
	)

def getDelegatesPublicKeys(*usernames):
	candidates = {}
	req = rest.GET.api.delegates(offset=len(candidates), limit=cfg.delegate).get("delegates", [])
	while not len(req) < cfg.delegate:
		candidates.update(dict([c["username"],c["publicKey"]] for c in req))
		req = rest.GET.api.delegates(offset=len(candidates), limit=cfg.delegate).get("delegates", [])
	return [p for u,p in candidates.items() if u in usernames]

def upVoteDelegate(usernames, secret, secondSecret=None):
	publicKey, privateKey = crypto.getKeys(secret)
	return sendTransaction(
		type=3,
		publicKey=publicKey,
		recipientId=crypto.getAddress(publicKey),
		privateKey=privateKey,
		secondSecret=secondSecret,
		asset={"votes":["+%s"%pk for pk in getDelegatesPublicKeys(*usernames)]}
	)

def downVoteDelegate(usernames, secret, secondSecret=None):
	publicKey, privateKey = crypto.getKeys(secret)
	return sendTransaction(
		type=3,
		publicKey=publicKey,
		recipientId=crypto.getAddress(publicKey),
		privateKey=privateKey,
		secondSecret=secondSecret,
		asset={"votes":["-%s"%pk for pk in getDelegatesPublicKeys(*usernames)]}
	)
