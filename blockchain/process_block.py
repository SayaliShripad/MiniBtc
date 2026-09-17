from .mempool import Mempool
from .Block import Block, BlockHeader
from .Blockchain import Blockchain
from .Transaction_Structure import Transaction, Transaction_Input, Transaction_Output
from .tx_validation import validate_transaction
from .merkle import compute_merkle_root


def process_block(blockchain: Blockchain, mempool: Mempool, block: Block):
    #TODO Verify Block Header

    #compute merkle root
    #add block 
    #remove utxos

    #compute merkle root
    #check if prev header hash is correct
    #check pow requirements
    #Validate each transaciotn or ??

#remove confirmed utxo from utxo set

    #then add block to blockchain

    latest_block = blockchain.get_latest_block()
    if block.block_header.previous_block_header_hash != latest_block.calculate_block_hash():
        print("Block's previous hash is incorrect")
        return False
    
    target = block.block_header.target
    block_hash = block.calculate_block_hash()
    if not block_hash.startswith("0"*target):
        print("Block does not meet proof of work requirements")
        return False
    
    tx_index = 0
    for tx in block.transactions:
        if tx_index != 0 and (not validate_transaction(tx, blockchain)):
            print(f"Transaction {tx.calculate_txid()} is invalid")
            return False
        tx_index += 1
    
    txids = [tx.calculate_txid() for tx in block.transactions]
    computed_merkle_root = compute_merkle_root(txids)
    
    coinbase_txs = [tx for tx in block.transactions if len(tx.inputs) == 0]
    if len(coinbase_txs) != 1:
        print("Block must contain exactly one coinbase transaction")
        return False
    


    if block.block_header.merkle_root != computed_merkle_root:
        print("Merkle root is incorrect")
        return False
    
    blockchain.add_block(block)
    mempool.remove_confirmed_transaction(block)
    return True