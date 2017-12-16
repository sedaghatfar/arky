# -*- encoding: utf8 -*-
# © Toons

"""
Usage: 
    ledger link [-i <index> -r <rank>]
    ledger unlink
    ledger status
    ledger send <amount> <address> [<message>]
    ledger vote [-ud] [<delegates>]

Options:
-i <index> --account-index <index>  ledger account index  [default: 0]
-r <rank> --address-rank <rank>     ledger address rank   [default: 0]
-u --up                             up vote delegate name folowing
-d --down                           down vote delegate name folowing

Subcommands:
    link     : link to ledger account.
    status   : show information about linked account.
    send     : send token amount to <address>. You can set a 64-char message.
    vote     : up or down vote delegate(s). <delegates> can be a coma-separated list
               or a valid new-line-separated file list conaining delegate names.
"""

from .. import rest
from .. import cfg
from .. import util
from .. import ldgr
from .. import slots

from . import __PY3__
from . import PROMPT
from . import DATA
from . import parse
from . import __name__ as __root_name__
from . import floatAmount

from .account import _send
from .account import _getVoteList

import arky
import sys


def _sign(tx):
	try:
		tx = ldgr.signTx(tx, DATA.ledger["path"])
	except Exception as e:
		if not len(e.__dict__):
			sys.stdout.write("%r\n" % e)
		elif e.sw == 28416:
			sys.stdout.write("Ledger key is not ready, try again...\n")
		elif e.sw == 27013:
			sys.stdout.write("Transaction canceled\n")
	else:
		return tx

	return False


def _return():
	sys.stdout.write("Ledger not available on %s network\n" % cfg.network)
	PROMPT.module = sys.modules[__root_name__]
	parse(["ledger", ".."])


def _whereami():
	if hasattr(cfg, "slip44"):
		if DATA.ledger:
			return "ledger[%s]" % util.shortAddress(DATA.ledger["address"])
		else:
			return "ledger"
	else:
		_return()
		return ""


def link(param):
	if hasattr(cfg, "slip44"):
		ledger_dpath = "44'/"+cfg.slip44+"'/%(--account-index)s'/0/%(--address-rank)s" % param
		try:
			publicKey = ldgr.getPublicKey(ldgr.parse_bip32_path(ledger_dpath))
			address = arky.core.crypto.getAddress(publicKey)
			DATA.ledger = rest.GET.api.accounts(address=address).get("account", {})
		except:
			sys.stdout.write("Ledger key is not ready, try again...\n")
			# unlink(param)
		else:
			if not DATA.ledger:
				sys.stdout.write("    %s account does not exixts in %s blockchain...\n" % (address, cfg.network))
				# unlink(param)
			else:
				DATA.ledger["path"] = ledger_dpath
	else:
		_return()


def status(param):
	if DATA.ledger:
		data = rest.GET.api.accounts(address=DATA.ledger["address"], returnKey="account")
		data["derivationPAth"] = DATA.ledger["path"]
		util.prettyPrint(data)


def unlink(param):
	DATA.ledger.clear()


def send(param):

	if DATA.ledger:
		amount = floatAmount(param["<amount>"])
		if amount:
			sys.stdout.write("Use ledger key to confirm or or cancel :\n")
			sys.stdout.write("    Send %(amount).8f %(token)s to %(recipientId)s ?\n" % \
		                    {"token": cfg.token, "amount": amount, "recipientId": param["<address>"]})
			tx = dict(
				type=0,
				timestamp=int(slots.getTime()),
				fee=cfg.fees["send"],
				amount=amount*100000000,
				recipientId=param["<address>"],
				vendorField=param["<message>"],
			)
			
			if _sign(tx): _send(tx)


def vote(param):

	lst, verb, to_vote = _getVoteList(param)

	if len(lst):
		sys.stdout.write("Use ledger key to confirm or or cancel :\n")
		sys.stdout.write("    %s %s ?\n" % (verb, ", ".join(to_vote)))
		tx = dict(
			type=3,
			timestamp=int(slots.getTime()),
			fee=cfg.fees["vote"],
			amount=0,
			recipientId=DATA.ledger["address"],
			asset={"votes": lst}
		)

		if _sign(tx): _send(tx)
