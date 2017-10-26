# -*- encoding: utf8 -*-
# © Toons

"""
Usage: delegate link [<secret> <2ndSecret>]
	   delegate unlink
	   delegate status
	   delegate voters

Subcommands:
	link   : link to delegate using secret passphrases. If secret passphrases
			 contains spaces, it must be enclosed within double quotes
			 ("secret with spaces"). If no secret given, it tries to link
			 with saved account(s).
	unlink : unlink delegate.
	status : show information about linked delegate.
	voters : show voters contributions ([address - vote] pairs).
"""

import arky

from .. import cfg
from .. import rest
from .. import util

from . import DATA
from . import input
from . import checkSecondKeys
from . import checkRegisteredTx

from .account import link as _link
from .account import unlink as _unlink

import io
import os
import sys
import collections

def _whereami():
	if DATA.account and not DATA.delegate:
		_loadDelegate()
	if DATA.delegate:
		return "delegate[%s]" % DATA.delegate["username"]
	else:
		return "delegate"


def _loadDelegate():
	if DATA.account:
		resp = rest.GET.api.delegates.get(publicKey=DATA.account["publicKey"])
		if resp["success"]:
			DATA.delegate = resp["delegate"]
			return True
		else:
			return False


def link(param):
	_link(param)
	if not _loadDelegate():
		sys.stdout.write("Not a delegate\n")
	# if any registry.... launch a check in bg ?


def unlink(param):
	_unlink(param)
	DATA.delegate.clear()


def status(param):
	if DATA.delegate:
		util.prettyPrint(dict(DATA.account, **DATA.delegate))


def voters(param):
	if DATA.delegate:
		accounts = rest.GET.api.delegates.voters(publicKey=DATA.delegate["publicKey"]).get("accounts", [])
		sum_ = 0.
		log = collections.OrderedDict()
		for addr, vote in sorted([[c["address"], float(c["balance"]) / 100000000] for c in accounts], key=lambda e:e[-1]):
			log[addr] = "%.3f" % vote
			sum_ += vote
		log["%d voters"%len(accounts)] = "%.3f" % sum_
		util.prettyPrint(log)
