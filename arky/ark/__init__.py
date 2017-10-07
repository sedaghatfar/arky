# -*- encoding: utf8 -*-
# © Toons

# __all__ = []

from .. import setInterval
from .. import rest
from .. import cfg

from . import crypto

import random

def init():
	network = rest.GET.api.loader.autoconfigure(returnKey="network")
	cfg.headers["version"] = network.pop("version")
	cfg.headers["nethash"] = network.pop("nethash")
	cfg.__dict__.update(network)
	cfg.fees = rest.GET.api.blocks.getFees(returnKey="fees")

def sendTransaction(**kw):
	tx = crypto.bakeTransaction(**kw)
	result = rest.POST.peer.transactions(peer=cfg.peers[0], transactions=[tx])
	success = 1 if result["success"] else 0
	for peer in cfg.peers[1:]:
		if rest.POST.peer.transactions(peer=peer, transactions=[tx])["success"]:
			success += 1
	result["broadcast"] = "%.1f%%" % (100.*success/len(cfg.peers))
	return result

def selectPeers():
	peers = [p for p in rest.GET.api.peers().get("peers", []) if p.get("status", "") == "OK" and p.get("delay", 0) <= cfg.timeout*1000]
	selection = []
	for i in range(min(cfg.broadcast, len(peers))):
		selection.append("http://%(ip)s:%(port)s" % random.choice(peers))
	if len(selection):
		cfg.peers = selection
selectPeers()

@setInterval(8*51)
def rotatePeers():
	selectPeers()
_daemon = rotatePeers()
