# Class imports
from wallet import Wallet
from transaction import Transaction
from transaction_output import Transaction_Output
from node import Node
from ring_node import Ring_Node


'''Test of node.test_create_wallet() function'''
def test_create_wallet():
    pass

'''Test of node.create_transaction() function'''
#TODO Rewrite with updated node class constructor
def test_create_transaction():
    node1 = Node()
    node2 = Node()    

    for i in range(1, 4):
        t = Transaction_Output(node1.wallet.public_key, 100 * i, 0)
        node1.wallet.add_UTXO(t)

    # print("\n\ntransaction inputs:")
    # for utxo in node1.wallet.UTXOs.values():
    #     print(utxo, "\n")
    
    # for utxo in node2.wallet.UTXOs.values():
    #     print(utxo, "\n")

    t = node1.create_transaction(node2.wallet.public_key, 600)
    print(t)

    # for tx in t.transaction_outputs:
    #     print(tx)

    # print("\n\n")
    # print("addr1: ", node1.wallet.public_key)
    # print("addr2: ", node2.wallet.public_key)


    # for utxo in node1.wallet.UTXOs.values():
    #     print(utxo, "\n")
    
    # for utxo in node2.wallet.UTXOs.values():
    #     print(utxo, "\n")


'''Test block mining'''
def test_mine_block():
    n = Node()
    n.mine_block()    


def test_verify_signature():
    n1 = Node()
    n2 = Node()

    t = Transaction(n1.wallet.public_key, n2.wallet.public_key, 100, [])
    t.sign_transaction(n1.wallet.private_key)

    if n1.validate_signature(t):
        print ("The signature is authentic.")
    else:  
        print ("The signature is not authentic.")


def test_validate_transaction():
    n1 = Node()
    n2 = Node()

    n1.register_node_to_ring(n2.wallet.public_key, 2, 2)
    n2.register_node_to_ring(n1.wallet.public_key, 1, 1)

    for i in range(1, 4):
        t = Transaction_Output(n1.wallet.public_key, 100 * i, 0)
        n1.wallet.add_UTXO(t)
        n2.ring[n1.wallet.public_key].add_UTXO(t)

    t = n1.create_transaction(n2.wallet.public_key, 500)

    if n2.validate_transaction(t):
        print("success!")
    else:
        print("failure")


# test_create_transaction()
# test_mine_block()
# test_verify_signature()
# test_validate_transaction()