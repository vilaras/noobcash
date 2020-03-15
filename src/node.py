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
	def __init__(self):
		self.NBC = 0
		self.chain = []
		self.current_id_count = 0
		self.wallet = self.create_wallet()
		self.current_block = self.create_new_block()
		self.broadcast = Broadcast()
		self.ring = {}   #here we store information for every node, as its id, its address (ip:port) its public key, its balance and it's UTXOs 

	def create_new_block(self):
		# return Block(len(self.chain), self.chain[-1].hash, "kati", [])
		return Block(1, 1, 1, [])

	def create_wallet(self):
		#create a wallet for this node, with a public key and a private key
		return Wallet()

	def register_node_to_ring(self, public_key, ip, port):
		# add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		# bootstrap node informs all other nodes and gives the request node an id and 100 NBCs

		self.ring[public_key] = Ring_Node(self.current_id_count, public_key, ip, port) 
		self.current_id_count += 1
		self.broadcast.add_peer(ip, port)

	'''
	Params:
		receiver: the address of the receiver to send coins to.
			Type <string>. Example: "id0"
		amount: the amount of NBC coins to send to receiver
			Type <int>. Example: 100
	Return:	
		create, sign and broadcast a new transaction of <amount> NBC to the address <receiver> 
	'''
	# TODO: Add valid UTXOs in the end of transaction
	def create_transaction(self, receiver_address, amount):
		UTXOs = self.wallet.UTXOs
		transaction_inputs = []
		transaction_outputs = []

		total = 0 
		for id, transaction in UTXOs.items(): 	
			if total < amount:
				transaction_inputs.append(id)
				total += transaction.amount

		if total < amount:
			print("Den exeis fragko, eisai mpatiraki...")
			return 

		t = Transaction(self.wallet.public_key, receiver_address, amount, deepcopy(transaction_inputs))
		
		for id in transaction_inputs:
			del UTXOs[id]

		UTXO = Transaction_Output(receiver_address, amount, t.transaction_id)
		transaction_outputs.append(UTXO)
		self.ring[receiver_address].UTXOs[UTXO.transaction_id] = UTXO

		if total > amount:
			UTXO = Transaction_Output(self.wallet.public_key, total - amount, t.transaction_id)
			transaction_outputs.append(UTXO)
			self.wallet.UTXOs[UTXO.transaction_id] = UTXO

		t.set_transaction_outputs(transaction_outputs)
		t.sign_transaction(self.wallet.private_key)

		# remember to broadcast it
		# self.broadcast_transaction(t)

		return t


	#Start mining when a block fills up
	def mine_block(self):
		while(True):
			candidate_nonce = rand.getrandbits(256)
			self.current_block.nonce = candidate_nonce
			self.current_block.hash = self.current_block.__hash__()

			if self.current_block.hash[:MINING_DIFFICULTY] == '0' * MINING_DIFFICULTY:
				print("success")
				self.broadcast_block(self.current_block)
				break
			
			else:
				print("skata")
				print(self.current_block.hash[:MINING_DIFFICULTY])



	# Initialization Functions

	def create_genesis_block(self):
		t = Transaction(0, self.wallet.public_key, NUMBER_OF_NODES * 100, [])
		t.sign_transaction(self.wallet.public_key)

		return Block(0, 1, 0, [t])


	def initialize_network(self):
		g = self.create_genesis_block()
		self.broadcast_block(g)
		
		for peer in self.ring.values():
			t = self.create_transaction(peer['public_key'], 100)
			self.broadcast_transaction(t)



	def add_transaction_to_block(self, transaction):
		if self.validate_transaction(transaction):
			self.commit_transaction(transaction)
			self.current_block.add_transaction(transaction)
		
		if len(self.current_block.transactions) == BLOCK_CAPACITY:
			self.mine_block()


	# If a transaction is valid, then commit it
	def commit_transaction(self, transaction):
		# Remove spent UTXOs
		if transaction.sender_address == self.wallet.public_key:
			for transaction_id in transaction.transaction_inputs:
				del self.wallet.UTXOs[transaction_id]

		else:
			for transaction_id in transaction.transaction_inputs:
				del self.ring[transaction.sender_address].UTXOs[transaction_id]

		# Add new UTXOs
		for UTXO in transaction.transaction_outputs:
			if transaction.receiver_address == self.wallet.public_key:
				self.wallet.UTXOs[UTXO.transaction_id] = UTXO
			
			else:
				self.ring[transaction.receiver_address].UTXOs[UTXO.transaction_id] = UTXO


	# Validation Functions

	def validate_signature(self, transaction):
		public_key = transaction.sender_address
		public_key = RSA.importKey(public_key)

		verifier = PKCS1_v1_5.new(public_key)
		h = transaction.hash

		return verifier.verify(h, transaction.signature)


	def validate_user(self, public_key):
		return public_key in self.ring or public_key == self.wallet.public_key


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

			return in_total == out_total and self.validate_signature(transaction)

		else:
			print("Not enough money to commit the transaction")
			return False


	def validate_block(self):
		pass


	# Broadcast functions

	def broadcast_block(self, block):
		self.broadcast.broadcast('receive_block', {'block': block})


	def broadcast_transaction(self, transaction):
		self.broadcast.broadcast('receive_transaction', {'transaction': transaction.to_dict()})



	# Concensus functions

	def valid_chain(self, chain):
		pass
		#check for the longer chain accroose all nodes


	def resolve_conflicts(self):
		pass
		#resolve correct chain


