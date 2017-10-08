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

# byte as int conversion
basint = lambda e:e if __PY3__ else \
         lambda e:ord(e)
# read value as binary data from buffer
unpack =  lambda fmt, fileobj: struct.unpack(fmt, fileobj.read(struct.calcsize(fmt)))
# write value as binary data into buffer
pack = lambda fmt, fileobj, value: fileobj.write(struct.pack(fmt, *value))
# read bytes from buffer
unpack_bytes = lambda f,n: unpack("<"+"%ss"%n, f)[0]
# write bytes into buffer
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

	# write type and timestamp
	pack("<bi", buf, (tx["type"],int(tx["timestamp"])))
	# write senderPublicKey as bytes in buffer
	pack_bytes(buf, unhexlify(tx["senderPublicKey"]))
	# if there is a requesterPublicKey
	if "requesterPublicKey" in tx:
		pack_bytes(buf, unhexlify(tx["requesterPublicKey"]))
	# if there is a recipientId
	if "recipientId" in tx:
		pack(">Q", buf, (int(tx["recipientId"][:-1]),))
	else:
		pack("<Q", buf, (0,))
	# write amount
	pack("<Q", buf, (int(tx["amount"]),))
	# if there is asset data
	if tx.get("asset", False):
		asset = tx["asset"]
		typ = tx["type"]
		if typ == 1 and "signature" in asset:
			pack_bytes(buf, unhexlify(asset["signature"]["publicKey"]))
		elif typ == 2 and "delegate" in asset:
			pack_bytes(buf, asset["delegate"]["username"].encode("utf-8"))
		elif typ == 3 and "votes" in asset:
			pack_bytes(buf, "".join(asset["votes"]).encode("utf-8"))
		else:
			pass
	# if there is a signature
	if tx.get("signature", False):
		pack_bytes(buf, unhexlify(tx["signature"]))
	# if there is a second signature
	if tx.get("signSignature", False):
		pack_bytes(buf, unhexlify(tx["signSignature"]))

	result = buf.getvalue()
	buf.close()
	return result.encode() if not isinstance(result, bytes) else result

def bakeTransaction(**kw):

	if "publicKey" in kw and "privateKey" in kw:
		public, private = kw["publicKey"], kw["privateKey"]
	elif "secret" in kw:
		public, private = getKeys(kw["secret"])
	else:
		raise Exception("Can not initialize transaction (no secret or keys given)")
		
	# put mandatory data
	payload = {
		"timestamp": int(slots.getTime()),
		"type": int(kw.get("type", 0)),
		"amount": int(kw.get("amount", 0)),
		"fee": cfg.fees.get({
			0: "send",
			1: "secondsignature",
			2: "delegate",
			3: "vote",
			# 4: "multisignature",
			# 5: "dapp"
		}[kw.get("type", 0)])
	}
	payload["senderPublicKey"] = public

	# add optional data
	for key in (k for k in ["requesterPublicKey", "recipientId", "asset"] if k in kw):
		payload[key] = kw[key]

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
