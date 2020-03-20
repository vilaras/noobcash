# Class imports
from wallet import Wallet
from transaction import Transaction
from transaction_output import Transaction_Output
from node import Node
from ring_node import Ring_Node

# Util imports
import jsonpickle   


'''Creation and validation'''
def test_transaction():
    n1 = Node('127.0.0.1', '5000')
    n2 = Node('127.0.0.1', '5001')

    n1.register_node_to_ring(n1.wallet.public_key, 1, 1)
    n1.register_node_to_ring(n2.wallet.public_key, 2, 2)

    n2.register_node_to_ring(n1.wallet.public_key, 1, 1)
    n2.register_node_to_ring(n2.wallet.public_key, 2, 2)

    for i in range(1, 4):
        t = Transaction_Output(n1.wallet.public_key, 100 * i, 0)
        n1.ring[n1.wallet.public_key].add_UTXO(t)
        n2.ring[n1.wallet.public_key].add_UTXO(t)

    t = n1.create_transaction(n2.wallet.public_key, 500)

    if n2.validate_transaction(t):
        print("success!")
    else:
        print("failure")


'''Creation and addition to chain'''
def test_block():
    n1 = Node('127.0.0.1', '5000')
    n2 = Node('127.0.0.1', '5001')

    n1.register_node_to_ring(n1.wallet.public_key, 1, 1)
    n1.register_node_to_ring(n2.wallet.public_key, 2, 2)

    n1.initialize_network()
    for block in n1.chain:
        print(block)

    print("\n\n\n\n")

    print(n1.current_block)


'''Test block mining'''
def test_mine_block():
    n = Node('127.0.0.1', '5000')
    
    n.register_node_to_ring(n.wallet.public_key, "127.0.0.1", '5000') 
    n.initialize_network()

    import numpy

    res = []
    for i in range(1000):
        res.append(n.mine_block())

    # Mean ~ 16^MINING_DIFFICULTY!!
    print(numpy.mean(res))


def test_initialization():
    n = Node('127.0.0.1', '5000')
    n2 = Node('127.0.0.1', '5001')

    n.register_node_to_ring(n.wallet.public_key, '127.0.0.1', '5000') 
    n.register_node_to_ring(n2.wallet.public_key, '127.0.0.1', '5001') 
    
    n.initialize_network()

    print(n.chain[0])
    print("\n\n\n")
    print(n.current_block)


def test_request():
    import requests
    from transaction import Transaction

    payload = Transaction(1, 1, 1, [])
    url = 'http://127.0.0.1:5000/test_endpoint'
    headerss = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.post(url, data=jsonpickle.encode({"data": payload}), headers=headerss)



# test_transaction()
# test_mine_block()
# test_block()
# test_initialization()
# test_request()

