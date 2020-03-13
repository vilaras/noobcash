# import blockchain
import datetime
import json
from Crypto.Hash import SHA256

CAPACITY = 10

#TODO Documentation
class Block:
	def __init__(self, index, previous_hash, nonce, transactions):
		self.index = index
		self.previous_hash = previous_hash
		self.nonce = nonce
		self.transactions = transactions
		self.timestamp = str(datetime.datetime.now()) 

		self.hash = 0 #self.my_hash()
	
	def __hash__(self):
		return SHA256.new(
			json.dumps(
				dict(
					transactions = self.transactions,
					previous_hash = self.previous_hash,
					nonce = self.nonce
				)
			).encode()
		).hexdigest()
		

	def add_transaction(self, transaction):
		self.transactions.append(transaction)
