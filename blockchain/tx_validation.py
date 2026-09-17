from blockchain.Transaction_Structure import Transaction
from blockchain.Blockchain import Blockchain
import hashlib

#utxo_set is be a dictionary { (txid, index) : (pubkey_hash, value) }

def validate_transaction(tx:Transaction, blockchain: Blockchain) -> bool:
    
    total_input_value = 0
    total_output_value = 0
    
    
    input_index = 0
    for txin in tx.inputs:
        key = (txin.previous_txid, txin.output_index)
        if key not in blockchain.utxo_set:
            print(f"Transaction {tx.calculate_txid()} is invalid: UTXO not found")
            return False
        
        pubkey_hash, value = blockchain.utxo_set[key]


        raw_pubkey = bytes.fromhex(txin.public_key)
        if hashlib.sha256(raw_pubkey).hexdigest() != pubkey_hash:
            print(f"Transaction {tx.calculate_txid()} is invalid: Public Key doesn't match")
            return False
        
        
        
        #TODO
        # Verify the signature of the input
        if not tx.verify_input(input_index):
            print(f"Transaction {tx.calculate_txid()} is invalid: Signature is invalid")
            return False
    
        input_index += 1
        total_input_value += value
        
        
    for txout in tx.outputs:
        total_output_value += txout.value
        
    
    if total_input_value < total_output_value:
        print(f"Transaction {tx.calculate_txid()} is invalid: Insufficient funds")
        return False
    
    return True
        
        