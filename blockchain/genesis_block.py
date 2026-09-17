from .Block import Block, BlockHeader
import ecdsa
from .Transaction_Structure import Transaction, Transaction_Output
import hashlib

def create_genesis_block() -> Block:

    pubkey_hash = hashlib.sha256(bytes.fromhex("0279e790cd77e16c688d58d2f1b4ae94981cd94fbf2eba0f80d21d730942514af7")).hexdigest()
    genesis_tx = Transaction(
        version = 1.0,
        inputs = [],
        outputs = [Transaction_Output(value = 50, pubkey_hash = pubkey_hash)] 
    )
    
    genesis_header = BlockHeader(
        version = 1,
        previous_block_header_hash = "0"*64,
        merkle_root = genesis_tx.calculate_txid(),
        timestamp = 0,
        target = 4,
        nonce = 0
    )
    genesis_block = Block(
        block_header = genesis_header,
        transactions = [genesis_tx]
    )
    return genesis_block

