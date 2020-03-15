# Class imports
from wallet import Wallet
from transaction import Transaction
from transaction_output import Transaction_Output
from node import Node
from ring_node import Ring_Node


'''Test block mining'''
def test_mine_block():
    n = Node()
    n.mine_block()    


'''Creation and validation'''
def test_transaction():
    n1 = Node()
    n2 = Node()

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


# test_transaction()
test_mine_block()
