# Cryptographic imports
from Crypto.Hash import SHA256

# Util imports
import datetime
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
		return SHA256.new(
			json.dumps(
				dict(
					transactions = [tx.to_dict() for tx in self.transactions],
					previous_hash = self.previous_hash,
					nonce = self.nonce
				)
			).encode()
		).hexdigest()
		

	def __str__(self):
		tx_str = '['
		for tx in self.transactions:
			tx_str = tx_str + "\n" + str(tx)
		
		tx_str += ']\n'

		return f'index: {self.index}\nprevious_hash: {self.previous_hash}\nnonce: {self.nonce}\n\ntransactions: {tx_str}\ntimestamp: {self.timestamp}\nhash: {self.hash}\n'

	def setup_mined_block(self, nonce):
		self.nonce = nonce
		self.hash = self.__hash__()
		self.timestamp = str(datetime.datetime.now())
