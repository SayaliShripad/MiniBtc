from typing import List
from .Transaction_Structure import Transaction_Input, Transaction_Output, Transaction

import hashlib

class BlockHeader:
   

    def __init__(
        self,
        version: int,
        previous_block_header_hash: str,
        merkle_root: str,
        timestamp: int,
        target: int,
        nonce: int
    ):
        self.version = version
        self.previous_block_header_hash = previous_block_header_hash
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.target = target
        self.nonce = nonce

    def __str__(self) -> str:
        return (
            f"BlockHeader:\n"
            f"  Version: {self.version}\n"
            f"  Previous Hash: {self.previous_block_header_hash}\n"
            f"  Merkle Root: {self.merkle_root}\n"
            f"  Timestamp: {self.timestamp}\n"
            f"  Target: {self.target}\n"
            f"  Nonce: {self.nonce}"
        )
    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "previous_block_header_hash": self.previous_block_header_hash,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp,
            "target": self.target,
            "nonce": self.nonce
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            version=data["version"],
            previous_block_header_hash=data["previous_block_header_hash"],
            merkle_root=data["merkle_root"],
            timestamp=data["timestamp"],
            target=data["target"],
            nonce=data["nonce"]
        )

class Block:
    

    def __init__(
        self,
        block_header: BlockHeader,
        transactions: List[Transaction]
    ):
        self.block_header = block_header
        self.transactions = transactions

    def __str__(self) -> str:
        header_str = str(self.block_header)
        transactions_str = "\n".join(str(tx) for tx in self.transactions)
        return (
            f"{header_str}\n"
            f"Transaction Count: {len(self.transactions)}\n"
            f"Transactions:\n{transactions_str}"
        )


    def calculate_block_hash(self) -> str:
        
        header_str = (
            str(self.block_header.version) +
            self.block_header.previous_block_header_hash +
            self.block_header.merkle_root +
            str(self.block_header.timestamp) +
            str(self.block_header.target) +
            str(self.block_header.nonce)
        )
        return hashlib.sha256(header_str.encode()).hexdigest()
    
    def to_dict(self) -> dict:
        return {
            "block_header": self.block_header.to_dict(),
            "transactions": [tx.to_dict() for tx in self.transactions]
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        header_data = data["block_header"]
        block_header = BlockHeader.from_dict(header_data)

        tx_list = []
        for tx_data in data["transactions"]:
            tx_list.append(Transaction.from_dict(tx_data))

        return cls(block_header=block_header, transactions=tx_list)