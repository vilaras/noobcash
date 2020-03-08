# from block import Block
from wallet import Wallet
from transaction import Transaction
from transaction_output import Transaction_Output

from copy import deepcopy

class Node:
	def __init__(self, wallet):
		self.NBC = 100
		self.chain = []
		self.current_id_count = 0
		self.wallet = wallet

		self.ring = []   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 


	def create_new_block():
		pass

	def create_wallet():
		#create a wallet for this node, with a public key and a private key
		pass

	def register_node_to_ring():
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
		pass

	def create_transaction(self, receiver, amount):
		UTXOs = self.wallet.transactions
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
		t = Transaction(self.wallet.public_key, receiver, amount, deepcopy(transaction_inputs))
		
		
		for id in transaction_inputs:
			del UTXOs[id]


		transaction_outputs.append(
			Transaction_Output(receiver, amount, t.transaction_id)
		)

		if total > amount:
			transaction_outputs.append(
				Transaction_Output(receiver, total - amount, t.transaction_id)
			)

		t.set_transaction_outputs(transaction_outputs)
		# t.sign_transaction(self.wallet.private_key)

		#remember to broadcast it
		# broadcast_transaction(t)

		print(t.__dict__)

		for tx in transaction_inputs:
			print(tx)

		for tx in transaction_outputs:
			print(tx.__dict__)

	def broadcast_transaction(transaction):
		pass

	def validate_transaction():
		pass
		#use of signature and NBCs balance


	def add_transaction_to_block():
		pass
		#if enough transactions  mine



	def mine_block():
		pass



	def broadcast_block():
		pass


		

	# def valid_proof(.., difficulty=MINING_DIFFICULTY):
	# 	pass




	#concensus functions

	def valid_chain(self, chain):
		pass
		#check for the longer chain accroose all nodes


	def resolve_conflicts(self):
		pass
		#resolve correct chain


