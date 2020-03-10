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
	Params:
		public_key: my address known to every node
			Type <string>. Example "id0"
		private_key: my crypto key only known to me
			Type <string???>
		address: public_key in HEX #Giati yparxei?
		transactions: the transactions that i use as UTXOs to spend coins
			Type <dict>
'''
class Wallet:

	def __init__(self):
		self.public_key, self.private_key = self.keys()
		self.address = binascii.hexlify(self.public_key.exportKey(format='DER')).decode('ascii')

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

		return pub, priv


# w = Wallet()
# for i in range(10):
# 	w.transactions.append(Transaction(1, 1, 1, 1))

# print(w.balance())
w = Wallet()