# -*- encoding: utf8 -*-
# © Toons

# __all__ = ["crypto"]

from .. import rest
from .. import cfg

from . import crypto

def init():
    cfg.headers["version"] = rest.GET.api.peers.version(returnKey="version")
    cfg.headers["nethash"] = rest.GET.api.blocks.getNethash(returnKey="nethash")
    cfg.fees = rest.GET.api.blocks.getFees(returnKey="fees")

def sendTransaction(**kw):
    tx = crypto.bakeTransaction(**kw)
    result = rest.POST.peer.transactions(transactions=[tx])
    if result["success"]:
        result["id"] = tx["id"]
    return result
