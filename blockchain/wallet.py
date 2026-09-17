import ecdsa
import hashlib
import base58
import logging
import asyncio

from blockchain.Transaction_Structure import Transaction, Transaction_Input, Transaction_Output

logger = logging.getLogger('BitcoinNode')

class Wallet:
    def __init__(self):
        self.signing_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        self.private_key = self.signing_key.to_string().hex()
        self.verifying_key = self.signing_key.get_verifying_key()
        self.public_key = self.verifying_key.to_string("compressed").hex()
        self.address = self.generate_address()

    def generate_address(self) ->str:

        pubkey_bytes = bytes.fromhex(self.public_key)
        
        pubkey_hash = hashlib.sha256(pubkey_bytes).digest()
        versioned_payload = b"\x00" + pubkey_hash
        checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
        address_bytes = versioned_payload + checksum

        wallet_address = base58.b58encode(address_bytes).decode("utf-8")
        return wallet_address
    

    def create_transaction(self, node, to_addr: str, amount: int):
        utxos = node.blockchain.get_utxos_for_wallet(self.address)
        if not utxos:
            node.logger.error("No UTXOs found for sender")
            return None

        (ref_txid, ref_index), ref_value = utxos[0]
        if ref_value < amount:
            node.logger.error("Insufficient funds")
            return None

        input_tx = Transaction_Input(
            previous_txid=ref_txid,
            output_index=ref_index,
            signature="",
            public_key="",
            sequence=0
        )

        outputs = [Transaction_Output(value=amount, pubkey_hash=decode_wallet_address(to_addr))]
        if ref_value > amount:
            outputs.append(Transaction_Output(
                value=ref_value - amount,
                pubkey_hash=decode_wallet_address(self.address)
            ))

        version = 1.0
        tx = Transaction(version, inputs=[input_tx], outputs=outputs)

        tx.sign_input(0, self.private_key)

        if node.mempool.add_transaction(tx, node.blockchain):
            node.logger.info("Transaction added to mempool. Broadcasting.")
            if node.loop is not None:
                node.loop.call_soon_threadsafe(lambda: asyncio.create_task(
                    node.p2p_node.broadcast({"type": "tx", "data": tx.to_dict()})
                ))
            return tx

        return None
    
    def load_from_privkey(self, private_key_hex: str):

        self.signing_key = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex), curve=ecdsa.SECP256k1)
        self.private_key = private_key_hex
        self.verifying_key = self.signing_key.get_verifying_key()
        self.public_key = self.verifying_key.to_string("compressed").hex()
        self.address = self.generate_address() 



    
def decode_wallet_address(address: str) -> bytes:
    address_bytes = base58.b58decode(address)
    return address_bytes[1:-4].hex()
