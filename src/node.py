import Crypto.Random.random as rand

# from block import Block
from wallet import Wallet
from transaction import Transaction
from transaction_output import Transaction_Output
from ring_node import Ring_Node
from block import Block

from copy import deepcopy

base_url = "http://"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
CAPACITY = 10
MINING_DIFFICULTY = 2

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
		self.NBC = 100
		self.chain = []
		self.current_id_count = 0
		self.wallet = self.create_wallet()
		self.current_block = self.create_new_block()

		self.ring = {}   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 


	def create_new_block(self):
		# return Block(len(self.chain), self.chain[-1].hash, "kati", [])
		return Block(1, 1, 1, [])

	def create_wallet(self):
		#create a wallet for this node, with a public key and a private key
		return Wallet()

	def register_node_to_ring(self, public_key, ip, port):
		# add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		# bootstrap node informs all other nodes and gives the request node an id and 100 NBCs

		self.current_id_count += 1
		self.ring[self.current_id_count] = Ring_Node(self.current_id_count, public_key, ip, port).__dict__ 

	'''
		Params:
			receiver: the address of the receiver to send coins to.
				Type <string>. Example: "id0"
			amount: the amount of NBC coins to send to receiver
				Type <int>. Example: 100
		Return:	
			create, sign and broadcast a new transaction of <amount> NBC to the address <receiver> 
	'''
	def create_transaction(self, receiver, amount):
		UTXOs = self.wallet.UTXOs
		transaction_inputs = []
		transaction_outputs = []

		total = 0 
		for id, transaction in UTXOs.items(): 	
			if total < amount:
				transaction_inputs.append(id)
				total += transaction.amount

		if total < amount:
			print("Se fagan oi poutanes")
			return 

		

		# TODO: Xreiazetai deepcopy?
		t = Transaction(self.wallet.address, receiver, amount, deepcopy(transaction_inputs))
		
		
		for id in transaction_inputs:
			del UTXOs[id]


		transaction_outputs.append(Transaction_Output(receiver, amount, t.transaction_id))
		if total > amount:
			transaction_outputs.append(Transaction_Output(self.wallet.address, total - amount, t.transaction_id))

		t.set_transaction_outputs(transaction_outputs)
		t.sign_transaction(self.wallet.private_key)

		# remember to broadcast it
		# self.broadcast_transaction(t)

		#DEBUG
		# print(t.__dict__['transactions'])

		# for tx in transaction_inputs:
		# 	print(tx)

		# for tx in transaction_outputs:
		# 	print(tx.__dict__)
		#DEBUG END

		return t

	def broadcast_transaction(self, transaction):
		response = json.dumps({'transaction': transaction})   
		for node in self.ring.values():
			url = base_url + node["ip"] + ":" + node["port"] + "/new_transaction"

			response = requests.post(url, data=response, headers=headers) 


	def is_valid_signature(self, transaction):
		pass		


	def validate_transaction(self, transaction):
		# TODO Check if the transactions are UTXO 
		total = sum(utxo.amount for utxo in transaction.transaction_inputs)

		return total >= transaction.amount and is_valid_signature(transaction)


	def add_transaction_to_block(self, transaction):
		if validate_transaction(transaction):
			self.current_block.add_transaction(transaction)
		
		if len(self.current_block.transactions) == CAPACITY:
			self.mine_block()


	#Start mining when a block fills up
	def mine_block(self):
		while(True):
			candidate_nonce = rand.getrandbits(256)
			self.current_block.nonce = candidate_nonce
			self.current_block.hash = self.current_block.__hash__()

			if self.current_block.hash[:MINING_DIFFICULTY] == '0' * MINING_DIFFICULTY:
				print("success")
				self.broadcast_block()
				break
			
			else:
				print("skata")
				print(self.current_block.hash[:MINING_DIFFICULTY])

				


	def broadcast_block(self):
		for node in self.ring.values():
			response = json.dumps({'block': self.current_block})   
			url = base_url + node["ip"] + ":" + node["port"] + "/new_transaction"

			response = requests.post(url, data=response, headers=headers) 


	#concensus functions

	def valid_chain(self, chain):
		pass
		#check for the longer chain accroose all nodes


	def resolve_conflicts(self):
		pass
		#resolve correct chain


