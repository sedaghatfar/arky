# -*- encoding: utf8 -*-
# © Toons

import arky

__all__ = ["network", "account", "delegate"] # , "escrow"]

from .. import __version__
from .. import __FROZEN__
from .. import __PY3__
from .. import rest
from .. import util
from .. import cfg

rest.use("dark")

import sys
import shlex
import docopt
import logging
import traceback

input = raw_input if not __PY3__ else input


class _Prompt(object):
	enable = True

	def __setattr__(self, attr, value):
		object.__setattr__(self, attr, value)

	def __repr__(self):
		return "%(hoc)s@%(net)s/%(wai)s> " % {
			"hoc": "hot" if cfg.hotmode else "cold",
			"net": cfg.network,
			"wai": self.module._whereami()
		}

	def state(self, state=True):
		_Prompt.enable = state

PROMPT = _Prompt()
PROMPT.module = sys.modules[__name__]


def _whereami():
	return ""


class Data(object):

	daemon_registry = None
	daemon_share = None

	def __init__(self):
		self.delegate = {}
		self.account = {}
		self.firstkeys = {}
		self.secondkeys = {}

DATA = Data()


def parse(argv):
	if argv[0] in __all__:
		module = getattr(sys.modules[__name__], argv[0])
		if hasattr(module, "_whereami"):
			PROMPT.module = module
			if len(argv) > 1:
				return parse(argv[1:])
		else:
			PROMPT.module = sys.modules[__name__]

	elif argv[0] in ["exit", ".."]:
		if PROMPT.module == sys.modules[__name__]:
			return False, False
		else:
			PROMPT.module = sys.modules[__name__]

	elif argv[0] in ["help", "?"]:
		sys.stdout.write("%s\n" % PROMPT.module.__doc__.strip())

	elif hasattr(PROMPT.module, argv[0]):
		try:
			arguments = docopt.docopt(PROMPT.module.__doc__, argv=argv)
		except:
			arguments = False
			sys.stdout.write("%s\n" % PROMPT.module.__doc__.strip())
		finally:
			return getattr(PROMPT.module, argv[0]), arguments

	else:
		sys.stdout.write("Command %s does not exist\n" % argv[0])

	return True, False


def start():
	sys.stdout.write(__doc__+"\n")
	_xit = False
	while not _xit:
		command = input(PROMPT)
		argv = shlex.split(command)

		if len(argv) and _Prompt.enable:
			cmd, arg = parse(argv)
			if not cmd:
				_xit = True
			elif arg:
				if "link" not in argv:
					logging.info(command)
				else:
					logging.info(" ".join(argv[:2]+["x" * len(e) for e in ([] if len(argv) <= 2 else argv[2:])]))
				try:
					cmd(arg)
				except Exception as error:
					if hasattr(error, "__traceback__"):
						sys.stdout.write("".join(traceback.format_tb(error.__traceback__)).rstrip() + "\n")
					sys.stdout.write("%s\n" % error)


# def execute(*lines):
# 	common.EXECUTEMODE = True

# 	for line in lines:
# 		sys.stdout.write("%s%s\n" % (PROMPT, line))
# 		argv = shlex.split(line)
# 		if len(argv):
# 			cmd, arg = parse(argv)
# 			if cmd and arg:
# 				if "link" not in argv:
# 					logging.info(line)
# 				else:
# 					logging.info(" ".join(argv[:2]+["x" * len(e) for e in ([] if len(argv) <= 2 else argv[2:])]))
# 				try:
# 					cmd(arg)
# 				except Exception as error:
# 					if hasattr(error, "__traceback__"):
# 						sys.stdout.write("".join(traceback.format_tb(error.__traceback__)).rstrip() + "\n")
# 					sys.stdout.write("%s\n" % error)

# 	common.EXECUTEMODE = False


# def launch(script):
# 	if os.path.exists(script):
# 		in_ = io.open(script, "r")
# 		execute(*[l.strip() for l in in_.readlines()])
# 		in_.close()


def checkSecondKeys():
	secondPublicKey = DATA.account.get("secondPublicKey", False)
	if secondPublicKey and not DATA.secondkeys:
		secondKeys = arky.core.crypto.getKeys(input("Enter second passphrase> "))
		if secondKeys["publicKey"] == secondPublicKey:
			DATA.secondkeys = secondKeys
			return True
		else:
			sys.stdout.write("    Second public key missmatch...\n    Broadcast canceled\n")
			return False
	else:
		return True


def floatAmount(amount):
	if amount.endswith("%"):
		return (float(amount[:-1])/100 * float(DATA.account.get("balance", 0.)) - cfg.fees["send"])/100000000.
	elif amount[0] in ["$", "€", "£", "¥"]:
		price = getTokenPrice(cfg.token, {"$":"usd", "EUR":"eur", "€":"eur", "£":"gbp", "¥":"cny"}[amount[0]])
		result = float(amount[1:])/price
		if askYesOrNo("%s=%s%f (%s/%s=%f) - Validate ?" % (amount, cfg.token, result, cfg.token, amount[0], price)):
			return result
		else:
			return False
	else:
		return float(amount)


def checkRegisteredTx(registry, quiet=False):
	LOCK = None

	@util.setInterval(2*cfg.blocktime)
	def _checkRegisteredTx(registry):
		registered = util.loadJson(registry)

		if not quiet:
			sys.stdout.write("\n---\nTransaction registry check, please wait...\n")
		for tx_id, payload in list(registered.items()):
			if rest.GET.api.transactions.get(id=tx_id).get("success", False):
				registered.pop(tx_id)
			else:
				if not quiet:
					sys.stdout.write("Resending transaction #%s:\n    %.8f %s to %s\n" % (
						tx_id,
						payload["amount"]/100000000,
						cfg.token, payload["recipientId"]
					))
				result = arky.core.sendPayload(payload)
				if not quiet:
					util.prettyPrint(result, log=False)
		
		util.dumpJson(registered, registry)
		remaining = len(registered)
		if not remaining:
			if not quiet:
				sys.stdout.write("\nCheck finished, all transactiosn broadcasted\n")
			LOCK.set()
		elif not quiet:
			sys.stdout.write("\n%d transaction%s went missing in blockchain\nWaiting two blocks (%ds) for another check...\n" % (remaining, "s" if remaining>1 else "", 2*cfg.blocktime))

	if not quiet:
		sys.stdout.write("Transaction check will be run soon, please wait...\n")
	LOCK = _checkRegisteredTx(registry)
	return LOCK


from . import network
from . import account
from . import delegate #, escrow

__doc__ = """Welcome to arky-cli [Python %(python)s / arky %(arky)s]
Available commands: %(sets)s""" % {"python": sys.version.split()[0], "arky":__version__, "sets": ", ".join(__all__)}
