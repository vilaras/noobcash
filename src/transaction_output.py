'''
    Params:
        transaction_id: ένα μοναδικό αναγνωριστικό id
        transaction_input_id: το id του transaction από το οποίο προέρχεται
        receiver_address: τον recipient του transaction
        amount: το ποσό που μεταφέρθηκε
'''
class Transaction_Output:

    def __init__(self, receiver_address, amount, transaction_input_id):

        self.transaction_id = self.__hash__()
        self.transaction_input_id = transaction_input_id
        self.receiver_address = receiver_address
        self.amount = amount

    
