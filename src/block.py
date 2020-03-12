# import blockchain
import datetime
import json
from Crypto.Hash import SHA256

CAPACITY = 10

class Block:
	def __init__(self, index, previous_hash, nonce, transactions):
		self.index = index
		self.previous_hash = previous_hash
		self.nonce = nonce
		self.transactions = transactions
		self.timestamp = str(datetime.datetime.now()) 

		self.hash = 0 #self.my_hash()
	
	def my_hash(self):
		return SHA256.new(
			json.dumps(
				dict(
					# index = self.index,
					transactions = self.transactions,
					nonce = self.nonce
					# previous_hash = self.previous_hash,
					# timestamp = self.timestamp
				)
			).encode()
		)
		

	def add_transaction(self, transaction):
		self.transactions.append(transaction)
		self.hash = my_hash()

		