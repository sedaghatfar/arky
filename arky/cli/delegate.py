# -*- encoding: utf8 -*-
# © Toons

"""
Usage: delegate link [<secret> <2ndSecret>]
	   delegate unlink
	   delegate status
	   delegate voters
	   delegate share <amount> [-b <blacklist> -d <delay> -l <lowest> -h <highest> <message>]

Options:
-b <blacklist> --blacklist <blacklist> ark addresses to exclude (comma-separated list or pathfile)
-h <highest> --highest <hihgest>       maximum payout in ARK
-l <lowest> --lowest <lowest>          minimum payout in ARK
-d <delay> --delay <delay>             number of fidelity-day

Subcommands:
	link   : link to delegate using secret passphrases. If secret passphrases
			 contains spaces, it must be enclosed within double quotes
			 ("secret with spaces"). If no secret given, it tries to link
			 with saved account(s).
	unlink : unlink delegate.
	status : show information about linked delegate.
	voters : show voters contributions ([address - vote] pairs).
	share  : share ARK amount with voters (if any) according to their
			 weight (there are mandatory fees). You can set a 64-char message.
"""

import arky

from .. import cfg
from .. import rest
from .. import util

from . import DATA
from . import input
from . import checkSecondKeys

from .account import link as _link
from .account import unlink as _unlink

import io
import os
import sys
import collections

try:
	version_info = sys.version_info[:2]
	if version_info == (2, 7): from . import pshare27 as pshare
	elif version_info == (3, 5): from . import pshare35 as pshare
	elif version_info == (3, 6): from . import pshare36 as pshare
	SHARE = True
except ImportError:
	SHARE = False


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


def share(param):
	
	if DATA.delegate and SHARE:
		# get blacklisted addresses
		if param["--blacklist"]:
			if os.path.exists(param["--blacklist"]):
				with io.open(param["--blacklist"], "r") as in_:
					blacklist = [e for e in in_.read().split() if e != ""]
			else:
				blacklist = param["--blacklist"].split(",")
		else:
			blacklist = []

		# separate fees from rewards
		forged_json = "%s-%s.forged" % (DATA.delegate["username"], cfg.network)
		forged_details = rest.GET.api.delegates.forging.getForgedByAccount(generatorPublicKey=DATA.delegate["publicKey"])
		rewards = int(forged_details["rewards"])
		last = util.loadJson(forged_json)
		if "rewards" in last:
			rewards -= int(last["rewards"])
		else:
			blockreward = int(rest.GET.api.blocks.getReward(returnKey="reward"))
			rewards = int(DATA.account["balance"]) * rewards/float(forged_details["forged"])
			rewards = (rewards//blockreward)*blockreward
		forged_details.pop("success", False)

		# computes amount to share using reward
		if param["<amount>"].endswith("%"):
			amount = int(float(param["<amount>"][:-1])/100 * rewards)
		elif param["<amount>"][0] in ["$", "€", "£", "¥"]:
			price = util.getTokenPrice(cfg.token, {"$":"usd", "EUR":"eur", "€":"eur", "£":"gbp", "¥":"cny"}[amount[0]])
			result = float(param["<amount>"][1:])/price
			if util.askYesOrNo("%s=%f %s (%s/%s=%f) - Validate ?" % (amount, result, cfg.token, cfg.token, amount[0], price)):
				amount = int(min(rewards, result*100000000))
			else:
				sys.stdout.write("    Share command canceled\n")
				return
		else:
			amount = int(min(rewards, float(param["<amount>"])*100000000))

		# define treshold and ceiling
		if param["--lowest"]:
			minimum = int(float(param["--lowest"])*100000000 + cfg.fees["send"])
		else:
			minimum = int(cfg.fees["send"])
		if param["--highest"]:
			maximum = int(float(param["--highest"])*100000000 + cfg.fees["send"])
		else:
			maximum = amount

		if amount > 100000000:
			# get voter contributions
			voters = rest.GET.api.delegates.voters(publicKey=DATA.delegate["publicKey"]).get("accounts", []) 
			contributions = dict([v["address"], int(v["balance"])] for v in voters if v["address"] not in blacklist)
			k = 1.0 / max(1, sum(contributions.values()))
			contributions = dict((a, b*k) for a,b in contributions.items())

			payroll_json = "%s-%s.waiting" % (DATA.delegate["username"], cfg.network)
			saved_payroll = util.loadJson(payroll_json)
			tosave_payroll = {}
			complement = {}
			payroll = collections.OrderedDict()

			for address, ratio in contributions.items():
				share = amount*ratio + saved_payroll.pop(address, 0)
				if share >= maximum:
					payroll[address] = maximum
				elif share < minimum:
					tosave_payroll[address] = share
				else:
					complement[address] = share
			
			pairs = list(pshare.applyContribution(**complement).items())
			mandatory = dict([pairs.pop(0)])
			for address, share in pairs:
				if share < minimum:
					tosave_payroll[address] = share
				else:
					payroll[address] = share
			
			util.prettyPrint(mandatory)
			util.prettyPrint(payroll)
			util.prettyPrint(tosave_payroll)

			util.dumpJson(tosave_payroll.update(saved_payroll), payroll_json)
			util.dumpJson(payroll.update(mandatory), "%s-%s.payroll" % (DATA.delegate["username"], cfg.network))
			util.dumpJson(forged_details, forged_json)

	else:
		sys.stdout.write("    Share feature not available\n")
