import requests
import json
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

from node import Node
from time import sleep

import sys
#import block
#import blockchain
#import wallet
#import transaction


NUMBER_OF_NODES = 3
BOOTSTRAP = {
    'ip': '127.0.0.1',
    'port': '5000'
}

base_url = "http://"
bootstrap_url = f'{base_url}{BOOTSTRAP["ip"]}:{BOOTSTRAP["port"]}'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

app = Flask(__name__)
CORS(app)

node = None
#blockchain = Blockchain()
    

def im_bootstrap(ip, my_port):
    return ip == BOOTSTRAP["ip"] and my_port == BOOTSTRAP["port"]


def broadcast(endpoint, payload):
    for peer in node.ring.values():
        try:
            url = f'{base_url}{peer["ip"]}:{peer["port"]}/{endpoint}'
            response = requests.post(url, data=json.dumps(payload), headers=headers)
        
        except requests.exceptions.Timeout:
            print(f'broadcast: Request "{ulr}" timed out')


# Send data
#.......................................................................................

# get all transactions in the blockchain
@app.route('/view_transactions', methods=['GET'])
def view_transactions():
    transactions = blockchain.transactions

    response = {'transactions': transactions}

    return jsonify(response), 200

# get all transactions in the blockchain
# @app.route('/show balance', methods=['GET'])
# def view_transactions():
#     transactions = blockchain.transactions

#     response = {'transactions': transactions}
#     return jsonify(response), 200


# @app.route('/show balance', methods=['GET'])
# def view_transactions():
#     transactions = blockchain.transactions

#     response = {'transactions': transactions}
#     return jsonify(response), 200


# Receive data
#.......................................................................................




# Connect
#.......................................................................................
@app.route('/register_client', methods=['POST'])
def register_client():
    global node

    if node == None:
        # Initialize node 
        node = Node()
        
        #Connect with the rest of the network
        try: 
            data = json.dumps({
                "public_key": str(node.wallet.public_key.exportKey('PEM')),
                "remote_port": port
            })

            # if not im_bootstrap(host, port):
            # print(response.json())
            response = requests.post(f'{bootstrap_url}/client_connect', data=data, headers=headers)

        except requests.exceptions.Timeout:
            return jsonify(f'connect_client: Request "{bootstrap_url}/connect_client" timed out'), 408


        return jsonify("You have connected successfully!"), 200

    else: 
        # Bad request
        return jsonify("You have already connected!"), 400


@app.route('/client_accepted', methods=['POST'])
def client_accepted():
    data = request.get_json()
    ring = data["ring"]
    
    print(ring)

    return jsonify("Thanks bootstrap!"), 200 


@app.route('/client_connect', methods=['POST'])
def client_connect():
    if im_bootstrap(ip, port):
        # Register bootstrap node
        # if node.current_id_count == 0:
        #     node.register_node_to_ring(node.wallet.public_key, BOOTSTRAP["ip"], BOOTSTRAP["port"])

        if node.current_id_count <= NUMBER_OF_NODES:
            data = request.get_json()
            public_key = data['public_key']
            remote_ip = request.remote_addr
            remote_port = data['remote_port']
            
            node.register_node_to_ring(public_key, remote_ip, remote_port) 
            
            if node.current_id_count == NUMBER_OF_NODES:
                broadcast("client_accepted", {"ring": node.ring})

            return jsonify("Welcome to our noobcash network!"), 200

        else:  
            # Forbidden action
            return jsonify("Sorry, we are full..."), 403

        

# TODO Make it work for public IPs
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = str(args.port)
    ip = '127.0.0.1'
    
    app.run(host=ip, port=port)
