import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

from transaction import Transaction

'''
to transaktions einai ntiksioneri
'''
class Wallet:

	def __init__(self):
		self.public_key, self.private_key = self.keys()
		self.address = self.public_key

	def balance(self):
		return sum(transaction.amount for transaction in self.transactions)

	def set_transactions(self, transactions):
		self.transactions = transactions

	'''
	Returns private, public key pair in HEX form
	'''
	def keys(self):
		random_gen = Crypto.Random.new().read
		priv = RSA.generate(1024, random_gen)
		pub = priv.publickey()

		return binascii.hexlify(priv.exportKey(format='DER')).decode('ascii'), binascii.hexlify(pub.exportKey(format='DER')).decode('ascii')


# w = Wallet()
# for i in range(10):
# 	w.transactions.append(Transaction(1, 1, 1, 1))

# print(w.balance())