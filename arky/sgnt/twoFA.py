# -*- coding:utf8 -*-
from arky.utils import bin
from six import PY3

import arky
import time
import json
import socket
import hashlib
import datetime
import socketserver


class TCPHandler(socketserver.BaseRequestHandler):

	publicKey = None
	check = False

	def handle(self):
		signature = bin.hexlify(self.request.recv(1024).strip())
		
		if TCPHandler.publicKey:
			try:
				TCPHandler.check = check(TCPHandler.publicKey, signature)
			except:
				pass
		else:
			TCPHandler.check = False
		if TCPHandler.check:
			self.request.sendall(b'{"granted":true}')
		else:
			self.request.sendall(b'{"granted":false}')
			

def remaining(): return 60 - time.time()%60


def elapsed(): return time.time()%60/60


def seed():
	utc_data = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M Z")
	h = hashlib.sha256(utc_data if isinstance(utc_data, bytes) else utc_data.encode()).hexdigest()
	return h.encode("utf-8") if not isinstance(h, bytes) else h


def get(privateKey):
	return arky.core.crypto.getSignatureFromBytes(seed(), privateKey)


def check(publicKey, signature):
	return arky.core.crypto.verifySignatureFromBytes(seed(), publicKey, signature)


def send(privateKey, host="localhost", port=9999):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((host, port))
	try:
		sign = get(privateKey)
	except:
		sign = bin.hexlify(b"none")
	sock.sendall(bin.unhexlify(sign))
	result = sock.recv(1024)
	sock.close()
	return json.loads(result.decode() if PY3 else result)


def wait(publicKey, host="localhost", port=9999):
	TCPHandler.publicKey = publicKey
	TCPHandler.check = False
	server = socketserver.TCPServer((host, port), TCPHandler)
	server.handle_request()
	return TCPHandler.check
