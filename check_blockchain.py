from src.broadcast import Broadcast
from src.block import Block

import jsonpickle
import json
import asyncio

from argparse import ArgumentParser

def all_the_same(blockchains):
    return all(elem == blockchains[0] for elem in blockchains)


parser = ArgumentParser()
parser.add_argument('-n', '--nodes', default=5, type=int, help='number of nodes running')
parser.add_argument('-v', '--verbose', action='store_true', default=False, help='show the actual blockchains?')
args = parser.parse_args()
n = args.nodes
verbose = args.verbose
 
b = Broadcast('test')
for i in range(n):
    b.add_peer(f'127.0.0.1:500{i}')


responses = asyncio.run(b.broadcast('get_blockchain', {}, 'GET'))
responses = list(map(jsonpickle.decode, responses))
blockchains_data = list(map(lambda item: item['data'], responses))
blockchains_host = list(map(lambda item: item['host'], responses))

blockchains = []
for blockchain in blockchains_data:
    block_id_list = []
    for block in blockchain:
        block_id_list.append(block['hash'])

    blockchains.append(block_id_list)

if all_the_same(blockchains):
    print("They are the same!")

else: 
    print("Something went wrong")

if verbose:
    print("printing the hash for each block for readability purposes\n")
    for blockchain in blockchains:
        print(blockchain)
