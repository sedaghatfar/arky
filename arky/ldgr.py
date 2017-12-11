# -*- encoding: utf8 -*-
# © Toons

from ledgerblue.comm import getDongle

from . import __PY3__
from . import util

import arky
import struct

pack = (lambda f,v: struct.pack(f, v)) if __PY3__ else \
	   (lambda f,v: bytes(struct.pack(f, v)))

intasb = lambda i: util.unhexlify(hex(i)[2:])


def parse_bip32_path(path):
	if len(path) == 0:
		return b""
	result = b""
	elements = path.split('/')
	for pathElement in elements:
		element = pathElement.split("'")
		if len(element) == 1:
			result = result + pack(">I", int(element[0]))	
		else:
			result = result + pack(">I", 0x80000000 | int(element[0]))
	return result


def buildTxApdu(dongle_path, data):
	path_len = len(dongle_path)
	
	if len(data) > 255 - (path_len+1):
		data1 = data[:255-(path_len+1)]
		data2 = data[255-(path_len+1):]
		p1 = util.unhexlify("e0040040")
	else:
		data1 = data
		data2 = util.unhexlify("")
		p1 =  util.unhexlify("e0048040")

	return [
		p1 + intasb(path_len + 1 + len(data1)) + intasb(path_len//4) + dongle_path + data1,
		util.unhexlify("e0048140") + intasb(len(data2)) + data2 if len(data2) else None
	]


def buildPkeyApdu(dongle_path):
	path_len = len(dongle_path)
	return util.unhexlify("e0020040") + intasb(1 + path_len) + intasb(path_len//4) + dongle_path


# def getPublicKeyAddress(dongle_path, debug=False, selectCommand=None):
# 	apdu = buildPkeyApdu(dongle_path)
# 	dongle = getDongle(debug, selectCommand)
# 	data = bytes(dongle.exchange(apdu))
# 	dongle.close()

# 	len_pkey = util.basint(data[0])
# 	len_address = util.basint(data[len_pkey+1])
	
# 	return {
# 		"publicKey": util.hexlify(data[1:len_pkey+1]),
# 		"address": data[-len_address:].decode()
# 	}


def getPublicKey(dongle_path, debug=False, selectCommand=None):
	apdu = buildPkeyApdu(dongle_path)
	dongle = getDongle(debug, selectCommand)
	data = bytes(dongle.exchange(apdu))
	dongle.close()
	len_pkey = util.basint(data[0])
	return util.hexlify(data[1:len_pkey+1])


def signTx(tx, path, debug=False, selectCommand=None):
	dongle_path = parse_bip32_path(path)
	# update tx
	tx["senderPublicKey"] = getPublicKey(dongle_path)
	apdu1, apdu2 = buildTxApdu(dongle_path, arky.core.crypto.getBytes(tx))
	dongle = getDongle(debug, selectCommand)
	result = dongle.exchange(bytes(apdu1))
	if apdu2:
		result = dongle.exchange(bytes(apdu2))
	dongle.close()
	# update tx
	tx["signature"] = util.hexlify(result)
	tx["id"] = arky.core.crypto.getId(tx)

	return tx
