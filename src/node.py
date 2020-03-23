# Cryptographic imports
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
import jsonpickle
from copy import deepcopy
from subprocess import Popen
import asyncio
import os
import signal


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
		self.blockchain = []
		self.current_id_count = 0
		self.host = host
		self.wallet = Wallet()
		self.current_block = ''
		self.broadcast = Broadcast(host)

		# We need to store all the transactions not in a mined block 
		# if we add them directly to the current block we have
		# a problem if while mining we get a transaction
		# We trigger the miner only when we have > BLOCK_CAPACITY pending transactions
		self.pending_transactions = []
		
		# Here we store information for every node, as its id, its address (ip:port) 
		# its public key, its balance and it's UTXOs 
		self.ring = {}   

		# The miner subprocess PID
		# If it is -1 the subprocess is not running
		self.miner_pid = -1


	def create_new_block(self):
		self.current_block = Block(len(self.blockchain), self.blockchain[-1].hash, [])


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
			self.add_transaction_to_pending(t)
			self.broadcast_transaction(t) 

			return t

		else:
			raise ValueError('Something went wrong in create transaction')
		

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

	
	def add_transaction_to_pending(self, transaction):
		self.pending_transactions.append(transaction)
		
		if len(self.pending_transactions) >= BLOCK_CAPACITY:
			self.start_miner()


	def add_block_to_chain(self, block):
		# We have aquired a new block, either by the network or by us
		self.blockchain.append(block)
		self.create_new_block()


	# Initialization Functions

	def create_genesis_block(self):
		t = Transaction(0, self.wallet.public_key, NUMBER_OF_NODES * 100, [])
		utxo = Transaction_Output(self.wallet.public_key, NUMBER_OF_NODES * 100, t.transaction_id) 
		t.set_transaction_outputs([utxo])
		t.sign_transaction(self.wallet.private_key)

		self.commit_genesis_transaction(t)

		g = Block(0, 1, [t])

		return g


	def initialize_network(self):
		g = self.create_genesis_block()
		g.setup_mined_block(0)
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
		if not self.validate_user(transaction.sender_address):
			print("I don't know the sender!")
			return False

		if not self.validate_user(transaction.receiver_address):
			print("I don't know the receiver!")
			return False

		# If we allow a user to send transactions to himself he could flood the
		# network with these transactions and prevent the other transactions from
		# finding a place into blocks, thus adding a delay to the network
		if transaction.sender_address == transaction.receiver_address:
			print("You can't send money to yourself!")
			return False

		if transaction.amount <= 0:
			print("You actually need to send some money")
			return False

		UTXOs = self.ring[transaction.sender_address].UTXOs
		for transaction_id in transaction.transaction_inputs:
			if not transaction_id in UTXOs:
				print("Invalid UTXO!!")
				return False

		in_total = sum(UTXOs[transaction_id].amount for transaction_id in transaction.transaction_inputs)
		if in_total < transaction.amount:
			print("Not enough money to commit the transaction")
			return False

		if in_total >= transaction.amount:
			out_total = sum(UTXO.amount for UTXO in transaction.transaction_outputs)

			# conservation of money
			return in_total == out_total and self.validate_signature(transaction)



	# TODO: Check the trnasactions in each block
	def validate_block(self, block, previous_block):
		if len(block.transactions) != BLOCK_CAPACITY:
			print("Invalid block capacity")
			return 'error'

		if block.hash != block.__hash__().hexdigest():
			print("Invalid hash!")
			return 'error'

		if not block.hash.startswith('0' * MINING_DIFFICULTY):
			print("Invalid nonce!")
			return 'error'

		if block.previous_hash == previous_block.hash:
			# Everything seems ok
			return 'ok'

		else:
			# The block is valid but the chaining is faulty, 
			# we probably have a fork
			return 'consensus'
			

	# Broadcast functions

	def broadcast_block(self, block):
		asyncio.run(self.broadcast.broadcast('receive_block', block, 'POST'))

	def broadcast_genesis_block(self, block):
		asyncio.run(self.broadcast.broadcast('receive_genesis_block', block, 'POST'))

	def broadcast_transaction(self, transaction):
		asyncio.run(self.broadcast.broadcast('receive_transaction', transaction, 'POST'))



	# Mining

	def start_miner(self):
		# If miner not already running			
		if self.miner_pid == -1:
			# Add transactions to the block to start mining
			self.current_block.add_transactions(self.pending_transactions[:BLOCK_CAPACITY])

			try:
				proc = Popen(['python3', 'miner.py', self.host, jsonpickle.encode({"data": self.current_block})])
				self.miner_pid = proc.pid

			except Exception as e:
				print(f'Exception while starting the miner {e.__class__.__name__}: {e}')

			# Remove transactions that got into the block from pending
			del self.pending_transactions[:BLOCK_CAPACITY]

		else:
			# If we reach this point we already run a miner process
			# and we want to start another one (?)
			# or we didn't clear up over the last one
			print("Miner already running! Wait to start another one")


	def stop_miner(self):
		# Kill the miner process, we lost the race
		if self.miner_pid != -1:
			os.kill(self.miner_pid, signal.SIGTERM)
			self.miner_pid = -1
		
		else:
			# We are trying a miner process that doesn't exist
			# or we didn't handle the miner correctly
			print("Miner already killed, what are you trying to do")


	# Concensus functions

	def valid_chain(self, chain):
		# A blockchain only with the genesis block is valid
		if len(chain) == 1:
			return True
		
		previous_block = chain[0]
		for block in chain[1:]:
			if self.validate_block(block, previous_block) != 'ok':
				return False
			
			previous_block = block

		return True


	# Asks each user for it's blockchain and keeps the longest valid one 
	def resolve_conflicts(self):
		responses = asyncio.run(self.broadcast.broadcast('get_blockchain', 'GET'))
		
		# Decode the response data into python objects 
		blockchains = map(jsonpickle.decode, responses)
		blockchains.append(self.blockchain)
		
		# Filter out all the non valid blockchains
		valid_blockchains = filter(valid_chain, blockchains)
		
		# accept the longest chain 
		self.blockchain = max(valid_blockchains, key=len)


