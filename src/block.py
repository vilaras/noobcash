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
		# In order to not include the hash attribute in hash calculation
        # Please find a better way to do this
		temp_hash, temp_timestamp = self.hash, self.timestamp
		self.hash, self.timestamp = -1, ''
		h = SHA256.new(jsonpickle.encode(self).encode())
		self.hash, self.timestamp = temp_hash, temp_timestamp

		return h

	def __str__(self):
		tx_str = '['
		for tx in self.transactions:
			tx_str = tx_str + "\n" + str(tx)
		
		tx_str += ']\n'

		return f'index: {self.index}\nprevious_hash: {self.previous_hash}\nnonce: {self.nonce}\n\ntransactions: {tx_str}\ntimestamp: {self.timestamp}\nhash: {self.hash}\n'

	def setup_mined_block(self, nonce):
		self.nonce = nonce
		self.hash = self.__hash__().hexdigest()
		self.timestamp = str(datetime.datetime.now())

	def try_nonce(self, nonce):
		self.nonce = nonce
		self.hash = self.__hash__().hexdigest()

	def add_transaction(self, transaction):
		self.transactions.append(transaction)