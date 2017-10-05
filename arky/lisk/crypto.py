# -*- encoding: utf8 -*-
# © Toons

from nacl.bindings.crypto_sign import crypto_sign_seed_keypair, crypto_sign
from nacl.bindings import crypto_sign_BYTES
from .. import __PY3__, __FROZEN__
from .. import cfg, slots

if not __PY3__:
	from StringIO import StringIO
else:
	from io import BytesIO as StringIO

import struct
import hashlib
import binascii

unpack =     lambda fmt, fileobj: struct.unpack(fmt, fileobj.read(struct.calcsize(fmt)))
pack =       lambda fmt, fileobj, value: fileobj.write(struct.pack(fmt, *value))
pack_bytes = lambda f,v: pack("!"+"%ss"%len(v), f, (v,)) if __PY3__ else \
             lambda f,v: pack("!"+"c"*len(v), f, v)

def hexlify(data):
	result = binascii.hexlify(data)
	return str(result.decode() if isinstance(result, bytes) else result)

def unhexlify(data):
	result = binascii.unhexlify(data)
	return result if isinstance(result, bytes) else result.encode()

def getKeys(secret, seed=None):
	seed = hashlib.sha256(secret.encode("utf8") if not isinstance(secret, bytes) else secret).digest() if not seed else seed
	return list(hexlify(e) for e in crypto_sign_seed_keypair(seed))

def getAddress(public):
	seed = hashlib.sha256(unhexlify(public)).digest()
	return "%s%s" % (struct.unpack("<Q", seed[:8])+(cfg.marker,))

def getSignature(tx, private):
	return hexlify(crypto_sign(hashlib.sha256(getBytes(tx)).digest(), unhexlify(private))[:crypto_sign_BYTES])

def getId(tx):
	seed = hashlib.sha256(getBytes(tx)).digest()
	return "%s" % struct.unpack("<Q", seed[:8])

def getBytes(tx):
	buf = StringIO()

	pack("<b", buf, (tx["type"],))
	pack("<i", buf, (int(tx["timestamp"]),))
	pack_bytes(buf, unhexlify(tx["senderPublicKey"]))

	# if there is a requesterPublicKey
	if "requesterPublicKey" in tx:
		pack_bytes(buf, unhexlify(tx["requesterPublicKey"]))

	# if there is a recipientId
	if "recipientId" in tx:
		pack(">Q", buf, (int(tx["recipientId"][:-1]),))
	else:
		pack("<Q", buf, (0,))

	pack("<Q", buf, (int(tx["amount"]),))

	# if there is a signature
	if "signature" in tx:
		pack_bytes(buf, unhexlify(tx["signature"]))
	
	# if there is a second signature
	if tx.get("signSignature", None):
		pack_bytes(buf, unhexlify(tx["signSignature"]))

	result = buf.getvalue()
	buf.close()
	return result.encode() if not isinstance(result, bytes) else result

def bakeTransaction(**kw):

	if "publicKey" in kw and "privateKey" in kw: public, private = kw["publicKey"], kw["privateKey"]
	elif "secret" in kw: public, private = getKeys(kw["secret"])
	else: raise Exception("Can not initialize transaction (no secret or keys given)")
		
	# put mandatory data
	payload = {
		"signSignature": None,
		"timestamp": int(slots.getTime()),
		"type": int(kw.get("type", 0)),
		"amount": int(kw.get("amount", 0)),
		"fee": cfg.fees.get({
			0: "send",
			# 1: "delegate",
			# 2: "secondsignature",
			# 3: "vote",
			# 4: "multisignature",
			# 5: "dapp"
		}[kw.get("type", 0)])
	}
	payload["senderPublicKey"] = public

	# add optional data
	if "requesterPublicKey" in kw:
		payload["senderPublicKey"] = kw["requesterPublicKey"]
	if "recipientId" in kw:
		payload["recipientId"] = kw["recipientId"]

	# sign payload
	payload["signature"] = getSignature(payload, private)
	if kw.get("secondSecret", None):
		secondPublic, secondPrivate = getKeys(kw["secondSecret"])
		payload["signSignature"] = getSignature(payload, secondPrivate)
	elif kw.get("secondPrivateKey", None):
		payload["signSignature"] = getSignature(payload, kw["secondPrivateKey"])

	# identify payload
	payload["id"] = getId(payload)

	return payload
