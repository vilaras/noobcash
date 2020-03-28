# Cryptographic imports
from Crypto.Hash import SHA256

# Util imports
import datetime
import jsonpickle
import json


'''
Attributes:
    index: Block's unique index
        Type <int>. 
    previous_hash: Hash of the previous block, serves as a pointer in the blockchain
        Type <int>. 
    nonce: A number cartifying proof of work
        Type <int>. 
    transactions: Transactions in this block
        Type <list Transaction>
    timestamp: The time this block was mined 
        Type <>
'''
class Block:
	def __init__(self, index, previous_hash, transactions):
		self.index = index
		self.previous_hash = previous_hash
		self.nonce = -1
		self.transactions = transactions
		self.timestamp = ''
		self.hash = -1
	
	def __hash__(self):
		toJSON = self.dumps()

		return SHA256.new(jsonpickle.encode(toJSON).encode())

	def __eq__(self, other):
	 return self.hash == other.hash

	def dumps(self):
		json_transactions = [transaction.dumps() for transaction in self.transactions]

		return json.dumps(
			dict(
				index = self.index,
				previous_hash = self.previous_hash,
				nonce = self.nonce,
				transactions = json_transactions,
			), sort_keys=True
		)

	def setup_mined_block(self, nonce):
		self.nonce = nonce
		self.hash = self.__hash__().hexdigest()
		self.timestamp = str(datetime.datetime.now())

	def try_nonce(self, nonce):
		self.nonce = nonce
		self.hash = self.__hash__().hexdigest()

	def set_transactions(self, transactions):
		self.transactions = transactions