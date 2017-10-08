# -*- encoding: utf8 -*-
# © Toons

from ecdsa.keys import SigningKey
from ecdsa.util import sigencode_der_canonize
from ecdsa.curves import SECP256k1
import base58

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

def compressEcdsaPublicKey(pubkey):
	first, last = pubkey[:32], pubkey[32:]
	# check if last digit of second part is even (2%2 = 0, 3%2 = 1)
	even = not bool(basint(last[-1]) % 2)
	return (b"\x02" if even else b"\x03") + first

def getKeys(secret, seed=None):
	"""
    Generate keyring containing public key, signing and checking keys as
    attribute.

    Keyword arguments:
    secret (str or bytes) -- a human pass phrase
    seed (byte)           -- a sha256 sequence bytes (private key actualy)

    Returns dict
    """
	seed = hashlib.sha256(secret.encode("utf8") if not isinstance(secret, bytes) else secret).digest() if not seed else seed
	signingKey = SigningKey.from_secret_exponent(int(binascii.hexlify(seed), 16), SECP256k1, hashlib.sha256)
	publicKey = signingKey.get_verifying_key().to_string()
	return {
		"publicKey": hexlify(compressEcdsaPublicKey(publicKey) if cfg.compressed else publicKey),
		"privateKey": hexlify(signingKey.to_string()),
		"wif": getWIF(seed)
	}

def getAddress(keys):
	"""
	Computes ARK address from keyring.

	Argument:
	keys (ArkyDict) -- keyring returned by `getKeys`

	Returns str
	"""
	ripemd160 = hashlib.new('ripemd160', unhexlify(keys["public"])).digest()[:20]
	seed = unhexlify(cfg.marker) + ripemd160
	return base58.b58encode_check(seed)

def getWIF(seed):
	"""
	Computes WIF address from seed.

	Argument:
	seed (bytes)     -- a sha256 sequence bytes

	Returns str
	"""
	seed = unhexlify(cfg.wif) + seed[:32] + (b"\x01" if cfg.compressed else b"")
	return base58.b58encode_check(seed)

def getSignature(tx, privateKey):
	signingKey = SigningKey.from_string(unhexlify(privateKey), SECP256k1, hashlib.sha256)
	return hexlify(signingKey.sign_deterministic(getBytes(tx), hashlib.sha256, sigencode=sigencode_der_canonize))

def getId(tx):
	return hexlify(hashlib.sha256(getBytes(tx)).digest())

def getBytes(tx):
	"""
	Hash transaction object into bytes data.

	Argument:
	tx (dict) -- transaction object

	Returns bytes sequence
	"""
	buf = StringIO()
	# write type and timestamp
	pack("<bi", buf, (tx["type"], int(tx["timestamp"])))
	# write senderPublicKey as bytes in buffer
	pack_bytes(buf, unhexlify(tx["senderPublicKey"]))
	# if there is a requesterPublicKey
	if "requesterPublicKey" in tx:
		pack_bytes(buf, unhexlify(tx["requesterPublicKey"]))
	# if there is a recipientId
	if tx.get("recipientId", False):
		recipientId = base58.b58decode_check(tx["recipientId"])
	else:
		recipientId = b"\x00"*21
	pack_bytes(buf, recipientId)
	# if there is a vendorField
	if tx.get("vendorField", False):
		vendorField = tx["vendorField"][:64].ljust(64, "\x00")
	else:
		vendorField = "\x00"*64
	pack_bytes(buf, vendorField.encode("utf8"))
	# write amount and fee value
	pack("<QQ", buf, (int(tx["amount"]), int(tx["fee"])))
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
		keys = {}
		keys["publicKey"] = kw["publicKey"]
		keys["privateKey"] = kw["privateKey"]
	elif "secret" in kw:
		keys = getKeys(kw["secret"])
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
	payload["senderPublicKey"] = keys["publicKey"]
	# add optional data
	for key in (k for k in ["requesterPublicKey", "recipientId", "vendorField", "asset"] if k in kw):
		payload[key] = kw[key]
	# sign payload
	payload["signature"] = getSignature(payload, keys["privateKey"])
	if kw.get("secondSecret", False):
		secondKeys = getKeys(kw["secondSecret"])
		payload["signSignature"] = getSignature(payload, secondKeys["privateKey"])
	elif kw.get("secondPrivateKey", False):
		payload["signSignature"] = getSignature(payload, kw["secondPrivateKey"])
	# identify payload
	payload["id"] = getId(payload)

	return payload
