# -*- encoding: utf8 -*-
# © Toons

from .. import __PY3__
from .. import crypto
from .. import slots
from .. import init
from .. import cfg

import struct

C = 0.0001*100000000

class Payload:

	@staticmethod
	def get(typ, **kw):
		return crypto.hexlify(getattr(Payload, "type%d"%typ)(**kw))

	@staticmethod
	def type0(**kw):
		return struct.pack("<QI21s" if __PY3__ else ("<QI"+21*"c"),
			kw.get("amount", 0),
			kw.get("fees", 0),
			crypto.base58.b58decode_check(kw["recipientId"])
		)

	@staticmethod
	def type1(**kw):
		if "secondSecret" in kw:
			secondPublicKey = crypto.getKeys(kw["secondSecret"])["publicKey"]
		elif "secondPublicKey" in kw:
			secondPublicKey = kw["secondPublicKey"]
		return struct.pack("<33s", crypto.unhexlify(secondPublicKey)) if __PY3__ else \
	           struct.pack(33*"c", secondPublicKey)

	@staticmethod
	def type2(**kw):
		username = kw.get("username", False)
		if username:
			length = len(username)
			if 3 <= length <= 255:
				return struct.pack("<B%ds"%length, length, username.encode()) if __PY3__ else \
				       struct.pack("<B" + length*"c", length, username)

	@staticmethod
	def type3(**kw):
		pass


def getHeaders(**kw):
	if "secret" in kw:
		publicKey = crypto.getKeys(kw["secret"])["publicKey"]
	elif "publicKey" in kw:
		publicKey = kw["publicKey"]
	else:
		raise Exception("Can not initialize transaction (no secret or publicKey given)")

	header = struct.pack("<BBBBI",
		kw.get("head", 0xff),
		kw.get("version", 0),
		kw.get("network", int(cfg.marker, base=16)),
		kw.get("type", 0),
		int(slots.getTime())
	)

	header += struct.pack("<33s", crypto.unhexlify(publicKey)) if __PY3__ else \
	          struct.pack(33*"c", publicKey)

	header += struct.pack("<Q", kw.get("fees", 0))

	vendorField = kw.get("vendorField", "")
	n = min(255, len(vendorField))
	header += struct.pack("<B", n)
	if n > 0:
		header += struct.pack("<%ss"%n, crypto.unhexlify(publicKey[:n])) if __PY3__ else \
		          struct.pack(n*"c", publicKey[:n])

	return crypto.hexlify(header)


def bakeTransaction(**kw):
	payload = Payload.get(kw.get("type", 0), **kw)
	kw["fees"] = int((kw.get("type", 0) + len(payload) + 47) * C)
	header = getHeaders(**kw)
	return header + payload
