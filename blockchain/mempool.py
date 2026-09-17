from typing import Dict
from .Transaction_Structure import Transaction
from .tx_validation import validate_transaction
from .Blockchain import Blockchain
from .Block import Block


class Mempool:
    def __init__(self):
        # dict of transactions (key = txid, value = transaction object)
        
        self.transactions : Dict[str, Transaction] = {}

    def add_transaction(self, tx, blockchain:Blockchain) -> bool:
       
       txid = tx.calculate_txid()
       if txid in self.transactions:
           #print(f"Transaction {txid} already in mempool")
           return False  
       
       if validate_transaction(tx, blockchain):
            self.transactions[txid] = tx
            return True
       else:
            print(f"Transaction {txid} is invalid")
            return False

    def remove_confirmed_transaction(self, block: Block):
       
       # Once a block is mined remove the transaction from the mempool
        for tx in block.transactions:
            txid = tx.calculate_txid()
            if txid in self.transactions:
                del self.transactions[txid]

    def get_transactions(self):
        
        return list(self.transactions.values())
