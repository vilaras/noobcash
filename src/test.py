from wallet import Wallet
from transaction import Transaction
from node import Node


def test_create_wallet():
    pass

def test_create_transaction():
    w = Wallet()

    txs = {}
    for i in range(3):
        t = Transaction(w.address, 1, 100 * i + 1, ["peos_inputs"])
        t.set_transaction_outputs("peos")
        txs[t.transaction_id] = t

    for key, tx in txs.items():
        print (tx)

    n = Node(w)
    w.set_transactions(txs)
    # print(w.__dict__)

    n.create_transaction(2, 10)