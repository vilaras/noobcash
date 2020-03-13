from wallet import Wallet
from transaction import Transaction
from transaction_output import Transaction_Output
from node import Node

'''Test of node.test_create_wallet() function'''
def test_create_wallet():
    pass

'''Test of node.create_transaction() function'''
#TODO Rewrite with updated node class constructor
def test_create_transaction():
    node1 = Node()
    node2 = Node()    

    for i in range(1, 4):
        t = Transaction_Output(node1.wallet.address, 100 * i, 0)
        node1.wallet.add_UTXO(t)

    # print("\n\ntransaction inputs:")
    # for utxo in node1.wallet.UTXOs.values():
    #     print(utxo, "\n")
    
    # for utxo in node2.wallet.UTXOs.values():
    #     print(utxo, "\n")

    t = node1.create_transaction(node2.wallet.address, 600)
    print(t)

    # for tx in t.transaction_outputs:
    #     print(tx)

    # print("\n\n")
    # print("addr1: ", node1.wallet.address)
    # print("addr2: ", node2.wallet.address)


    # for utxo in node1.wallet.UTXOs.values():
    #     print(utxo, "\n")
    
    # for utxo in node2.wallet.UTXOs.values():
    #     print(utxo, "\n")


'''Test block mining'''
def test_mine_block():
    n = Node()
    n.mine_block()    


# test_create_transaction()
# test_mine_block()