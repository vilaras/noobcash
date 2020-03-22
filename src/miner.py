# configuration parameters
from config import *

# Cryptographic imports
import Crypto.Random.random as rand

# Class parameters
from block import Block

# Util imports
import jsonpickle
import json
import requests
import sys
import signal

# We create miner as a separate file/class in order to execute it
# as a subprocess of the main program

# This gives us the ease to send signals to it, i.e. when we need to stop mining,
# have it not interact with other parts of the main program and handle it
# independently 


class Miner:
	def __init__(self, block, host):
		self.current_block = block
		self.host = host
		self.base_url = "http://"
		self.headers = {"Content-type": "application/json", "Accept": "text/plain"}

		signal.signal(signal.SIGTERM, self.handler)

	# Exit gracefully
	def handler(self, sig, frame):
		# print(f'The parent process terminates us, we were sent a signal {sig}')
		sys.exit(0)	


	def mine_block(self):
		counter = 1 # For statistics
		print("I started mining! Hurry!")
		while(True):
			candidate_nonce = rand.getrandbits(32)
			self.current_block.try_nonce(candidate_nonce)
			
			if self.current_block.hash.startswith('0' * MINING_DIFFICULTY):
				self.current_block.setup_mined_block(candidate_nonce)
				print(f'success after {counter} tries')

				break
						
			else:
				counter += 1
				# print(self.current_block.hash[:MINING_DIFFICULTY]))


		# We found a nonce! now we need to comunicate this to out parent process
		# We do this by sending a POST request to the /found_block endpoint
		# When the parent process gets the request, it kills out process 
		# so we don't expect to return here :(
		 
		url = f'{self.base_url}{self.host}/found_block'
		payload = jsonpickle.encode({"data": self.current_block})
		requests.post(url, data=payload, headers=self.headers)

		# This should never print
		print("Why are we still here")

# This check ensures that the code will be executed
# only when we run it as a subprocess and not when we import it
if __name__ == '__main__':
	host = sys.argv[1]
	json_block = json.loads(sys.argv[2])['data']
	block = jsonpickle.decode(json.dumps(json_block))
	miner = Miner(block, host)
	miner.mine_block()
