# Flask imports
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

# Util imports
import requests
import json
import jsonpickle
import asyncio

# Class imports
from node import Node

# Configuration parameters
from config import *

base_url = "http://"
bootstrap_url = f'{base_url}{BOOTSTRAP}'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

app = Flask(__name__)
CORS(app)

# User Node 
node = None

'''
Params:
    host <str>: User url
Returns <bool>: 
    Returns if user is the bootstrap node
'''
def im_bootstrap(host):
    return f'{base_url}{host}' == bootstrap_url

# Added for testing purposes
@app.route('/resolve', methods=['GET'])
def resolve():
    return jsonify(node.resolve_conflicts())


@app.route('/stress_test', methods=['GET'])
def stress_test():
    file = f'../5nodes/transactions{node.host[-1]}.txt' 
    with open(file) as infile:
        for line in infile:
            inputs = line.split()
            id_num = inputs[0].split('id')[-1]
            payload = json.dumps({'id':id_num, 'amount':inputs[1]})
            response = requests.post(f'http://{node.host}/create_transaction', data=payload, headers=headers)
            
            print(response.json())

    return "hi"

# Send data
#.......................................................................................

@app.route('/create_transaction', methods=['POST'])
def create_transaction():
    data = request.get_json()
    id = int(data["id"])
    amount = int(data["amount"])

    try:
        address = ''
        for ring_node in node.ring.values():
            if ring_node.id == id:
                address = ring_node.public_key

        t = node.create_transaction(address, amount)

    except Exception as e:
        return jsonify(f'Exception while creating transaction \n{e.__class__.__name__}: {e}\n'), 403


    return jsonify("Transaction accepted!\n"), 200   


@app.route('/found_block', methods=['POST'])
def found_block():
    data = request.get_json()
    block = jsonpickle.decode(json.dumps(data["data"]))

    # Add block to chain 
    node.add_block_to_chain(block, True)
    
    # Kill the miner process
    try:    
        node.stop_miner()
                
    except Exception as e:
        return jsonify(f'Exception while killing miner in /found_block: \n{e.__class__.__name__}: {e}\n'), 403 

    if len(node.pending_transactions) >= BLOCK_CAPACITY:
        node.start_miner()

    # Broadcast block
    node.broadcast_block(block)

    # This is sent back to miner process which should be killed by now 
    return jsonify("This should never reach the miner but whatever...\n"), 200


@app.route('/get_blockchain', methods=['GET'])
def get_blockchain():
    return jsonify(jsonpickle.encode({"data": node.blockchain, "host": node.host}))


@app.route('/get_blockchain_length', methods=['GET'])
def get_blockchain_length():
    return jsonify(jsonpickle.encode({"data": len(node.blockchain), "host": node.host}))


@app.route('/get_pending_transactions', methods=['GET'])
def get_pending_transactions():
    data = [transaction.transaction_id for transaction in node.pending_transactions]
    return jsonify(jsonpickle.encode({"data": data, "host": node.host}))


@app.route('/get_pending_lengths', methods=['GET'])
def get_pending_lengths():
    data = len(node.pending_transactions)
    return jsonify(jsonpickle.encode({"data": data, "host": node.host}))


@app.route('/get_orphan_transactions', methods=['GET'])
def get_orphan_transactions():
    data = [transaction.transaction_id for transaction in node.orphan_transactions]
    return jsonify(jsonpickle.encode({"data": data, "host": node.host}))


@app.route('/get_orphan_lengths', methods=['GET'])
def get_orphan_lengths():
    data = len(node.orphan_transactions)
    return jsonify(jsonpickle.encode({"data": data, "host": node.host}))


@app.route('/balance', methods=['GET'])
def show_participants():
    # Return a list [id: public_key] for the user to see
    data = []
    for public_key, ring_node in node.ring.items():
        data.append(f'id{ring_node.id}: {ring_node.balance} NBC\n')

    data = json.dumps(''.join(data))

    return data, 200
    

@app.route('/view_transactions', methods=['GET'])
def view_transactions():
    if len(node.blockchain) == 0:
        return jsonify(f'No transactions yet\n'), 200

    if len(node.blockchain) == 1:
        return jsonify(f'id0 -> id0 {NUMBER_OF_NODES * 100} NBC\n'), 200

    transactions = node.blockchain[-1].transactions
    data = []
    for transaction in transactions:
        data.append(f'id{node.ring[transaction.sender_address].id} -> id{node.ring[transaction.receiver_address].id} {transaction.amount} NBC\n')
    
    data = json.dumps(''.join(data))

    return data, 200


@app.route('/view_all_transactions', methods=['GET'])
def view_all_transactions():
    if len(node.blockchain) == 0:
        return json.dumps(f'No transactions yet\n'), 200

    data = [f'id0 -> id0 {NUMBER_OF_NODES * 100} NBC\n']

    for block in node.blockchain[1:]:
        for transaction in block.transactions:
            data.append(f'id{node.ring[transaction.sender_address].id} -> id{node.ring[transaction.receiver_address].id} {transaction.amount} NBC\n')

    for transaction in node.pending_transactions:
        data.append(f'id{node.ring[transaction.sender_address].id} -> id{node.ring[transaction.receiver_address].id} {transaction.amount} NBC\n')

    data = json.dumps(''.join(data))

    return data, 200


# Receive data
#.......................................................................................

@app.route('/receive_genesis_block', methods=['POST'])
def receive_genesis_block():
    data = request.get_json()
    block = jsonpickle.decode(json.dumps(data["data"]))

    try:
        node.blockchain.append(block)
        node.create_new_block()
        node.commit_genesis_transaction(block.transactions[0])

    except Exception as e:
        return jsonify(f'Exception while receiving genesis block \n{e.__class__.__name__}: {e}\n'), 403

    return jsonify("Got it\n"), 200


@app.route('/receive_block', methods=['POST'])
def receive_block():
    data = request.get_json()
    block = jsonpickle.decode(json.dumps(data["data"]))

    res = node.validate_block(block, node.blockchain[-1])
    if res == 'error':
        return jsonify("Block declined\n"), 403 

    else:
        # Kill the miner process
        try:
            node.stop_miner()

        except Exception as e:
            return jsonify(f'Exception while killing miner in /receive_block: \n{e.__class__.__name__}: {e}\n'), 403

        if res == 'ok':
            node.add_block_to_chain(block, False)

            if len(node.pending_transactions) >= BLOCK_CAPACITY:
                node.start_miner()

            return jsonify("Block accepted!\n"), 200

        if res == 'consensus':
            node.resolve_conflicts()

            if len(node.pending_transactions) >= BLOCK_CAPACITY:
                node.start_miner()

            return jsonify("Had to run consensus"), 200



@app.route('/receive_transaction', methods=['POST'])
def receive_transaction():
    data = request.get_json()
    transaction = jsonpickle.decode(json.dumps(data['data']))
    remote_port = data['port']
    remote_host = f'{request.remote_addr}:{remote_port}'

    if remote_host != node.ring[transaction.sender_address].host:
        return jsonify("You sent me a transaction that wasn't yours!"), 403

    try:
        ret = node.validate_transaction(transaction)
        if ret == 'ok':
            node.commit_transaction(transaction)
            node.add_transaction_to_pending(transaction)
            node.resolve_dependencies(transaction)
        
        elif ret == 'orphan':
            node.orphan_transacions[transaction] = set(transaction.transaction_inputs)
            
        else: 
            return jsonify("Transaction declined\n"), 403

    except Exception as e:
        return jsonify(f'Exception while receiving transaction \n{e.__class__.__name__}: {e}\n'), 403


    return jsonify("Transaction accepted!\n"), 200


# Connect
#.......................................................................................

@app.route('/client_accepted', methods=['POST'])
def client_accepted():
    data = request.get_json()
    ring = jsonpickle.decode(json.dumps(data["data"]))

    for public_key, ring_node in ring.items():
        node.register_node_to_ring(public_key, ring_node.host, ring_node.id)

    return jsonify("Thanks bootstrap!\n"), 200 


@app.route('/register_client', methods=['POST'])
def register_client():
    global node

    if node == None:
        # Initialize node 
        node = Node(f'{ip}:{port}')

        #Connect with the rest of the network
        try: 
            payload = json.dumps({
                "public_key": node.wallet.public_key,
                "host": f'{ip}:{port}'
            })
            url = f'{bootstrap_url}/client_connect'
            response = requests.post(url, data=payload, headers=headers)

            if response.status_code != 200:
                return jsonify(f'Something went wrong with {url} request'), response.status_code

        except Exception as e:
            return jsonify(f'Exception while registering client \n{e.__class__.__name__}: {e}\n'), 403

        return jsonify("You have connected successfully!\n"), 200

    else: 
        # Bad request
        return jsonify("You have already connected!\n"), 400


@app.route('/client_connect', methods=['POST'])
def client_connect():
    if im_bootstrap(f'{ip}:{port}'):
        if node.current_id_count <= NUMBER_OF_NODES:
            data = request.get_json()
            public_key = data['public_key']
            remote_host = data['host']
            
            node.register_node_to_ring(public_key, remote_host) 
            
            if node.current_id_count == NUMBER_OF_NODES:
                asyncio.run(node.broadcast.broadcast("client_accepted", node.ring, 'POST'))
                node.initialize_network()


            return jsonify("Welcome to our noobcash network!\n"), 200

        else:  
            # Forbidden action
            return jsonify("Sorry, we are full...\n"), 403

        

# TODO Make it work for public IPs
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-i', '--ip', default='127.0.0.1', type=str, help='ip to listen on')
    parser.add_argument('-p', '--port', default='5000', type=str, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    ip = args.ip
    
    app.run(host=ip, port=port, threaded=True)
