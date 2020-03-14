class Ring_Node:
    def __init__(self, id, public_key, ip, port, balance = 0):
        self.id = id
        self.public_key = public_key
        self.ip = ip
        self.port = port
        self.balance = balance
        self.UTXOs = {}

    def set_balance(self):
        self.balance = sum(UTXO.amount for UTXO in self.UTXOs.values())

    def add_UTXO(self, UTXO):
        self.UTXOs[UTXO.transaction_id] = UTXO

    def __str__(self):
        return f'id: {self.id} \npublic_key: {self.public_key} \nip: {self.ip} \nport: {self.port} \nbalance: {self.balance} \nUTXOs: {self.UTXOs}\n'