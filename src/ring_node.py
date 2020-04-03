class Ring_Node:
    def __init__(self, id, public_key, host, balance = 0):
        self.id = id
        self.public_key = public_key
        self.host = host 
        self.balance = balance
        self.UTXOs = {}

    def update_balance(self):
        self.balance = sum(UTXO.amount for UTXO in self.UTXOs.values())
