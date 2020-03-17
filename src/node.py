# Cryptographic imports
import Crypto.Random.random as rand
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

# Class imports
from wallet import Wallet
from transaction import Transaction
from transaction_output import Transaction_Output
from ring_node import Ring_Node
from block import Block
from broadcast import Broadcast

# Configuration parameters
from config import *

# Util imports
from copy import deepcopy


'''
Params:
	NBC: The coins given by bootstrap node at the initialization of the network ?
		Type <int>. Example: 100
	chain: the blockchain ?
		Type <Blockchain.class>
	current_id_count: number of nodes in the network ?
		Type <int>
	wallet: the wallet of this node
		Type <Wallet.class> 
	ring: information for every node, as its id, its address (ip:port) its public key and its balance 
		Type <list>
'''
class Node:
	def __init__(self, host):
		self.chain = []
		self.current_id_count = 0
		self.wallet = Wallet()
		self.current_block = ''
		self.broadcast = Broadcast(host)
		self.ring = {}   #here we store information for every node, as its id, its address (ip:port) its public key, its balance and it's UTXOs 

	def create_new_block(self):
		self.current_block = Block(len(self.chain), self.chain[-1].hash, [])


	# Add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
	# Bootstrap node informs all other nodes and gives the request node an id and 100 NBCs
	def register_node_to_ring(self, public_key, host, id=None):
		if id == None:
			self.ring[public_key] = Ring_Node(self.current_id_count, public_key, host) 
		
		else:
			self.ring[public_key] = Ring_Node(id, public_key, host) 

		self.current_id_count += 1
		self.broadcast.add_peer(host)

	'''
	Params:
		receiver: the address of the receiver to send coins to.
			Type <string>. Example: "id0"
		amount: the amount of NBC coins to send to receiver
			Type <int>. Example: 100
	Return:	
		create, sign and broadcast a new transaction of <amount> NBC to the address <receiver> 
	'''
	def create_transaction(self, receiver_address, amount):
		UTXOs = self.ring[self.wallet.public_key].UTXOs
		transaction_inputs = []
		transaction_outputs = []

		total = 0 
		for id, transaction in UTXOs.items(): 	
			if total < amount:
				transaction_inputs.append(id)
				total += transaction.amount

		if total < amount:
			raise ValueError('Something went wrong')

		t = Transaction(self.wallet.public_key, receiver_address, amount, deepcopy(transaction_inputs))

		UTXO = Transaction_Output(receiver_address, amount, t.transaction_id)
		transaction_outputs.append(UTXO)
		
		if total > amount:
			UTXO = Transaction_Output(self.wallet.public_key, total - amount, t.transaction_id)
			transaction_outputs.append(UTXO)

		t.set_transaction_outputs(transaction_outputs)
		t.sign_transaction(self.wallet.private_key)

		if self.validate_transaction(t):
			self.commit_transaction(t)
			self.add_transaction_to_block(t)
			self.broadcast_transaction(t)

			return t

		else:
			raise ValueError('Something went wrong')
		

	def update_balances(self):
		for ring_node in self.ring.values():
			ring_node.update_balance()


	# If a transaction is valid, then commit it
	def commit_transaction(self, transaction):
		# Remove spent UTXOs
		for transaction_id in transaction.transaction_inputs:
			del self.ring[transaction.sender_address].UTXOs[transaction_id]

		# Add new UTXOs
		for UTXO in transaction.transaction_outputs:
			self.ring[UTXO.receiver_address].UTXOs[UTXO.transaction_id] = UTXO

		self.update_balances()


	# In the genesis transaction there is no sender address
	def commit_genesis_transaction(self, transaction):
		# Add new UTXOs
		for UTXO in transaction.transaction_outputs:
			self.ring[UTXO.receiver_address].UTXOs[UTXO.transaction_id] = UTXO

		self.update_balances()

	
	def add_transaction_to_block(self, transaction):
		self.current_block.add_transaction(transaction)
		
		if len(self.current_block.transactions) == BLOCK_CAPACITY:
			self.mine_block()


	def add_block_to_chain(self, block):
		self.chain.append(block)
		self.create_new_block()


	# Initialization Functions

	def create_genesis_block(self):
		t = Transaction(0, self.wallet.public_key, NUMBER_OF_NODES * 100, [])
		utxo = Transaction_Output(self.wallet.public_key, NUMBER_OF_NODES * 100, t.transaction_id) 
		t.set_transaction_outputs([utxo])
		t.sign_transaction(self.wallet.private_key)

		self.commit_genesis_transaction(t)

		g = Block(0, 1, [t])
		g.setup_mined_block(0)

		return g


	def initialize_network(self):
		g = self.create_genesis_block()
		self.broadcast_genesis_block(g)
		self.add_block_to_chain(g)

		for peer in self.ring.values():
			if peer.public_key != self.wallet.public_key:
				t = self.create_transaction(peer.public_key, 100)


	# Validation Functions

	def validate_signature(self, transaction):
		public_key = transaction.sender_address
		public_key = RSA.importKey(public_key)

		verifier = PKCS1_v1_5.new(public_key)
		h = transaction.__hash__()

		return verifier.verify(h, transaction.signature)


	def validate_user(self, public_key):
		return public_key in self.ring


	def validate_transaction(self, transaction):
		if not self.validate_user(transaction.sender_address) or not self.validate_user(transaction.receiver_address):
			print("I don't know these people!")
			return False

		UTXOs = self.ring[transaction.sender_address].UTXOs
		for transaction_id in transaction.transaction_inputs:
			if not transaction_id in UTXOs:
				print("Invalid UTXO!! Thief!!")
				return False

		in_total = sum(UTXOs[transaction_id].amount for transaction_id in transaction.transaction_inputs)

		if in_total >= transaction.amount:
			out_total = sum(UTXO.amount for UTXO in transaction.transaction_outputs)

			# conservation of money
			return in_total == out_total and self.validate_signature(transaction)

		else:
			print("Not enough money to commit the transaction")
			return False


	def validate_block(self, block):
		return block.previous_hash == self.chain[-1].hash and block.hash == block.__hash__()



	# Broadcast functions

	def broadcast_block(self, block):
		self.broadcast.broadcast('receive_block', block)

	def broadcast_genesis_block(self, block):
		self.broadcast.broadcast('receive_genesis_block', block)

	def broadcast_transaction(self, transaction):
		self.broadcast.broadcast('receive_transaction', transaction)


	# Mining

	def mine_block(self):
		print("I started mining! Hurry!")
		counter = 1 # For statistics
		while(True):
			candidate_nonce = rand.getrandbits(256)
			self.current_block.try_nonce(candidate_nonce)
			if self.current_block.hash[:MINING_DIFFICULTY] == '0' * MINING_DIFFICULTY:
				print(f'success after {counter} tries')
				break
				# return counter
							
			else:
				counter += 1
				# print(self.current_block.hash[:MINING_DIFFICULTY]))

		self.broadcast_block(self.current_block)


	# Concensus functions

	def valid_chain(self, chain):
		pass
		#check for the longer chain accroose all nodes


	def resolve_conflicts(self):
		pass
		#resolve correct chain


