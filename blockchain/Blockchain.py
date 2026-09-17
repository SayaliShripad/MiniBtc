from .genesis_block import create_genesis_block
from .Block import Block
from .Transaction_Structure import Transaction

from .wallet import decode_wallet_address

from typing import Tuple


class Blockchain:
    def __init__(self):
        self.blocks = []
        self.utxo_set = {}
        
        genesis = create_genesis_block()
        self.add_block(genesis)
        
        
    # miner calls add_block after validating the block and computing the proof of work
    #So whatever txs are included in the block are valid
    
    
    def add_block(self,block: Block):
        self.blocks.append(block)
        self.update_utxo_set(block)
        
        
    def update_utxo_set(self, block: Block):
        for tx in block.transactions:
            txid = tx.calculate_txid()
            
            for txin in tx.inputs:
                self.spend_utxo(txin.previous_txid, txin.output_index)
                
                
            
            for idx, txout in enumerate(tx.outputs):
                out_key = (txid, idx)
                #TODO pubkey_hash, value
                self.utxo_set[out_key] = (txout.pubkey_hash, txout.value)
                
    
    
    def spend_utxo(self, txid: str, output_index: int):
        key = (txid, output_index)
        if key in self.utxo_set:
            del self.utxo_set[key]
            
    def get_latest_block(self) -> Block:
        return self.blocks[-1]
    
    def get_height(self) -> int:
        return len(self.blocks)
    
    def get_utxos_for_wallet(self, wallet_address: str):
        # Decode the Base58 wallet address to get the raw public key hash
        pubkey_hash = decode_wallet_address(wallet_address)
        utxos = []
        for (txid, idx), (owner_hash, value) in self.utxo_set.items():
            if owner_hash == pubkey_hash:
                utxos.append(((txid, idx), value))
        return utxos
            
                