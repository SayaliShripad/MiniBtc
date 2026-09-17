from .mempool import Mempool
from .Block import Block, BlockHeader
from .Blockchain import Blockchain
from .Transaction_Structure import Transaction, Transaction_Input, Transaction_Output
from .merkle import compute_merkle_root
import time
import hashlib
from .process_block import process_block



    

def do_proof_of_work(block: Block, target: int) -> Block:
    
    block.block_header.nonce = 0
    while True:
        block_hash = block.calculate_block_hash()
        #print(f"Nonce: {block.block_header.nonce}, Hash: {block_hash}")
        if block_hash[:target] == "0" * target:
            return block
        block.block_header.nonce += 1


def mine_block(blockchain: Blockchain, mempool: Mempool, miner_address:str) -> Block:
    
    if len(mempool.get_transactions()) == 0:
        print("No transactions in mempool")
        return False 
    
    txns = mempool.get_transactions()
    parent_block = blockchain.get_latest_block()
    prev_hash = parent_block.calculate_block_hash()
    
    version = 1.0
    coinbase_tx = Transaction(version, inputs = [], outputs = [Transaction_Output(value = 50, pubkey_hash = miner_address)])
    #TODO miner address is the pubkey hash of the miner
    all_txns = [coinbase_tx]+ txns
    txids = [tx.calculate_txid() for tx in all_txns]
    merkle_root = compute_merkle_root(txids)
    
    new_block = Block(
        block_header = BlockHeader(
            version = 1,
            previous_block_header_hash = prev_hash,
            merkle_root = merkle_root,
            timestamp = int(time.time()),
            target = 4,
            nonce = 0
        ),
        transactions = all_txns
    )
    print("pow starting")
    mined_block = do_proof_of_work(new_block, new_block.block_header.target)
    print("pow done")
    ans = process_block(blockchain, mempool, mined_block)
    
    if ans:
        return mined_block
    else:
        return False
    
    