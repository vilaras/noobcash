class Ring_Node:
    def __init__(self, id, public_key, ip, port, balance = 0):
        self.id = id
        self.public_key = public_key
        self.ip = ip
        self.port = port
        self.balance = balance