from blockchain.Blockchain import Blockchain
from blockchain.Block import Block
from blockchain.Transaction_Structure import (
    Transaction_Input, Transaction_Output, Transaction
)
from blockchain.mempool import Mempool
from blockchain.merkle import compute_merkle_root
from blockchain.miner import mine_block
from blockchain.tx_validation import validate_transaction
import hashlib
import base58


# If you have a create_genesis_block function:
from blockchain.genesis_block import create_genesis_block

def main():

    
    private_key = "c03aad11c3811aaba04074ab580c8c65b42e020b3dfab83758e2bd6ccfd0884e"
    public_key_hex = "0279e790cd77e16c688d58d2f1b4ae94981cd94fbf2eba0f80d21d730942514af7"

    # Assign our custom message handler
    blockchain = Blockchain()
    genesis_block = blockchain.get_latest_block()
    mempool = Mempool()

    print(f"Genesis block hash: {genesis_block.calculate_block_hash()}")
    mempool = Mempool()

    print(f"  UTXO set count: {len(blockchain.utxo_set)}")

    for (utxid, idx), (owner_hash, value) in blockchain.utxo_set.items():
        print(f"  UTXO: (tx={utxid}, out={idx}) belongs to {owner_hash} with value={value}")
    

    genesis_txid = list(blockchain.utxo_set.keys())[0][0] 
    genesis_out_index = list(blockchain.utxo_set.keys())[0][1]

    (owner_hash, utxo_value) = blockchain.utxo_set[(genesis_txid, genesis_out_index)]

    tx_input = Transaction_Input(
        previous_txid=genesis_txid,
        output_index=genesis_out_index,
        signature="FAKE_SIGNATURE",  # for testing, or sign it properly
        public_key="njnk",
        sequence=0
    )


    tx_out_1 = Transaction_Output(value=20, pubkey_hash="RecipientPubKeyHash123")
    tx_out_2 = Transaction_Output(value=30, pubkey_hash=owner_hash)

    new_tx = Transaction(
        inputs=[tx_input],
        outputs=[tx_out_1, tx_out_2],
    )

    new_tx.sign_input(0, private_key)
    #print(new_tx.inputs[0].public_key)
    #print(new_tx.inputs[0].signature)


    is_valid = validate_transaction(new_tx, blockchain)
    print("Transaction validation result:" , is_valid)

    if is_valid:
        result = mempool.add_transaction(new_tx,blockchain)
        if result:
            print("Transaction added to mempool")
        else:
            print("Transaction not added to mempool")

    pubkey_bytes = bytes.fromhex(public_key_hex)
    pubkey_hash = hashlib.sha256(pubkey_bytes).digest()  
    versioned_payload = b"\x00" + pubkey_hash
    checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
    address_bytes = versioned_payload + checksum

    wallet_address = base58.b58encode(address_bytes).decode("utf-8")

    #UTXO for a given wallet address
    utxos = blockchain.get_utxos_for_wallet(wallet_address)
    print(f"UTXOs for wallet {utxos}:")
    
    miner_address = "shivambtc022"
    mined_block = mine_block(blockchain, mempool, miner_address)

    if mined_block:
        print("Block mined successfully")
    else:
        print("Block mining failed")

    latest_block = blockchain.get_latest_block()

    if latest_block!=mined_block:
        print("Block not added to blockchain")
    else:
        print("Block added to blockchain")

    print(f"  UTXO set count: {len(blockchain.utxo_set)}")
    print(f"  Block count: {blockchain.get_height()}")
    for i, block in enumerate(blockchain.blocks):
        print(f"  Block #{i+1} hash: {block.calculate_block_hash()} - TX count: {len(block.transactions)}")  
  
main()