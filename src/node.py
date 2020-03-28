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
import requests
import jsonpickle
from copy import deepcopy
from subprocess import Popen
import asyncio
import os
import signal
import threading


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
		
		# Transactions that we have not received all the inputs for
		self.orphan_transactions = {}

		# Here we store information for every node, as its id, its address (ip:port) 
		# its public key, its balance and it's UTXOs 
		self.ring = {}   

		# The miner subprocess PID
		# If it is None the subprocess is not running
		self.miner_pid = None

		# The lock prevents multiple request threads to attempt
		# starting the miner
		self.miner_lock = threading.Lock()

		# Block receiver lock
		# We have to stop receiving blocks while running consensus
		# in order not to interfere with the process
		self.block_receiver_lock = threading.Lock()

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
			raise Exception("You don't have enough money, unfortunately...")

		t = Transaction(self.wallet.public_key, receiver_address, amount, deepcopy(transaction_inputs))

		UTXO = Transaction_Output(receiver_address, amount, t.transaction_id)
		transaction_outputs.append(UTXO)
		
		if total > amount:
			UTXO = Transaction_Output(self.wallet.public_key, total - amount, t.transaction_id)
			transaction_outputs.append(UTXO)

		t.set_transaction_outputs(transaction_outputs)
		t.sign_transaction(self.wallet.private_key)

		if self.validate_transaction(t) == 'ok':
			self.commit_transaction(t)
			self.add_transaction_to_pending(t)
			self.broadcast_transaction(t) 

			return t

		# else:
		# 	raise Exception('Something went wrong in create transaction')
		

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

	def resolve_dependencies(self, transaction):
		for transaction, dependencies in self.orphan_transactions.items():
			dependencies -= {transaction.transaction_id}

			if len(dependencies) == 0:
				del self.orphan_transactions[transaction]

				if self.validate_transaction(transaction):
					self.commit_transaction(transaction)
					self.add_transaction_to_pending(transaction)
				
					self.resolve_conflicts(transaction)


	# In the genesis transaction there is no sender address
	def commit_genesis_transaction(self, transaction):
		# Add new UTXOs
		for UTXO in transaction.transaction_outputs:
			self.ring[UTXO.receiver_address].UTXOs[UTXO.transaction_id] = UTXO

		self.update_balances()

	
	def add_transaction_to_pending(self, transaction):
		self.pending_transactions.append(transaction)
		
		if len(self.pending_transactions) >= BLOCK_CAPACITY:
			if self.request_miner_access():
				self.start_miner()


	# If it is my block added to the chain we can delete the 
	# pending transactions much faster!
	def add_block_to_chain(self, block, is_my_block=False):
		self.blockchain.append(block)
		self.create_new_block()

		transaction_ids = [transaction.transaction_id for transaction in block.transactions]
		self.update_pending_transactions(transaction_ids, is_my_block)



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
		self.blockchain.append(g)
		self.create_new_block()

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
		try:
			if transaction in self.pending_transactions:
				raise Exception("Already have this")

			if not self.validate_user(transaction.sender_address):
				raise Exception("I don't know the sender!")

			if not self.validate_user(transaction.receiver_address):
				raise Exception("I don't know the receiver!")

			# If we allow a user to send transactions to himself he could flood the
			# network with these transactions and prevent the other transactions from
			# finding a place into blocks, thus adding a delay to the network
			if transaction.sender_address == transaction.receiver_address:
				raise Exception("You can't send money to yourself!")

			if transaction.amount <= 0:
				raise Exception("You actually need to send some money")

			if len(set(transaction.transaction_inputs)) != len(transaction.transaction_inputs):
				raise Exception("Duplicate transaction inputs")

			UTXOs = self.ring[transaction.sender_address].UTXOs
			for transaction_id in transaction.transaction_inputs:
				if not transaction_id in UTXOs:
					return 'orphan'

			in_total = sum(UTXOs[transaction_id].amount for transaction_id in transaction.transaction_inputs)
			if in_total < transaction.amount:
				raise Exception("Not enough money to commit the transaction")

			# conservation of money
			out_total = sum(UTXO.amount for UTXO in transaction.transaction_outputs)
			if in_total != out_total:
				raise Exception("Did you just give birth to money?")
			
			if not self.validate_signature(transaction):
				raise Exception("Invalid Signature")

			return 'ok'

		except Exception as e:
			print(f'Exception in transaction validation: \n{e.__class__.__name__}: {e}')
			return 'error'


	# TODO: Check the transactions in each block
	def validate_block(self, block, previous_block):
		try:
			if len(block.transactions) != BLOCK_CAPACITY:
				raise Exception(f'Invalid block capacity, {len(block.transactions)}')

			if block.hash != block.__hash__().hexdigest():
				raise Exception("Invalid hash!")

			if not block.hash.startswith('0' * MINING_DIFFICULTY):
				raise Exception(f'Invalid nonce!, {block.hash}')

			if len(set(transaction.transaction_id for transaction in block.transactions)) != len(block.transactions):
				raise Exception("Duplicate transaction inputs")

			if block.previous_hash == previous_block.hash:
				# Everything seems ok
				return 'ok'

			else:
				for existent_block in reversed(self.blockchain[:-1]):
					if existent_block.hash == block.previous_hash:
						# The new block doesn't increase our chain since it is 
						# a branch of an older block
						return 'redundant'

				# The block is valid but the chaining is faulty, 
				# we probably have a fork
				return 'consensus'

		except Exception as e:
			print(f'Exception in block validation: \n{e.__class__.__name__}: {e}')
			return 'error'


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
		# Add transactions to the block to start mining
		self.current_block.set_transactions(self.pending_transactions[:BLOCK_CAPACITY])

		try:
			proc = Popen(['python3', 'miner.py', self.host, jsonpickle.encode({"data": self.current_block})])
			self.miner_pid = proc.pid

		except Exception as e:
			print(f'Exception while starting the miner {e.__class__.__name__}: {e}')


	def stop_miner(self):
		# Kill the miner process, we lost the race
		try:
			os.kill(self.miner_pid, signal.SIGTERM)
			self.miner_pid = None

		except Exception as e:
			print(f'Exception in miner termination: \n{e.__class__.__name__}: {e}')


	def request_miner_access(self):
		with self.miner_lock:
			if self.miner_pid == None:
				self.miner_pid = 'placeholder'
				return True

			else:
				print("Miner already running! Wait to start another one")
				return False




	# Concensus functions

	# We have aquired a new block, either by the network or by us
	# Remove transactions that got into the block from pending
	def update_pending_transactions(self, transaction_ids, is_my_block):
		# Optimizing the deletion process for arbitrary transactions to 
		# only check the transaction ids for equality
		if is_my_block:
			del self.pending_transactions[:BLOCK_CAPACITY]

		else:
			self.pending_transactions = list(
				filter(
					lambda transaction: transaction.transaction_id not in transaction_ids, 
					self.pending_transactions
				)
			)


	# When we adopt another chain we have to reconstruct the
	# state of the network as dicatetd by this chain
	# 
	# Thus, starting from the genesis block and
	# appending each block from the chain we have to
	# recompute the UTXOs for every node
	def valid_chain(self, chain):
		# A blockchain with only the genesis block is valid
		if len(chain) == 1:
			return True
		
		previous_block = chain[0]
		for block in chain[1:]:
			if self.validate_block(block, previous_block) != 'ok':
				return False

			previous_block = block

		return True


	# Asks each user for it's blockchain and keeps the longest valid one 
	#
	# Optimization Idea: First ask every user for the length of it's blockchain
	# and then only ask the user with the longest blockchain
	# for the whole blockchain. If this blockchain is invalid greedily try
	# the next one etc...
	def resolve_conflicts(self):	
		print("CONSENSUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUS")
		responses = asyncio.run(self.broadcast.broadcast('get_blockchain_length', {}, 'GET'))

		# Decode the response data into python objects 
		blockchain_lengths = map(jsonpickle.decode, responses)
		sorted_blockchain_lengths = sorted(blockchain_lengths, key=lambda item: item['data'], reverse=True)

		for item in sorted_blockchain_lengths:
			# We are fine, we have the longest chain

			url = f'http://{item["host"]}/get_blockchain'
			headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
			response = requests.get(url, headers)
			candidate_blockchain = jsonpickle.decode(response.json())['data']

			if len(candidate_blockchain) <= len(self.blockchain):
				self.current_block.transactions = []
				return
			
			if len(candidate_blockchain) != int(item['data']):
				print("You lied to me!")
				continue

			if self.valid_chain(candidate_blockchain):
				print("We found a valid chain to replace ours!")
				
				# Find the new veryfied transactions to remove from our pending
				i = 0
				while self.blockchain[i] == candidate_blockchain[i]:
					i += 1

				his_transactions_ids = []
				for block in candidate_blockchain[i:]:
					for transaction in block.transactions:
						his_transactions_ids.append(transaction.transaction_id)

				self.blockchain = candidate_blockchain
				self.update_pending_transactions(his_transactions_ids, False)

				break
		
		# Executes only if we didn't break the for loop
		else:
			print("We didn't find a valid chain")

		
		self.create_new_block()