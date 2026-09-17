import ecdsa
from typing import List

import hashlib
import copy

class Transaction_Input:
    def __init__(
        self,
        previous_txid: str,
        output_index: int,
        signature: str,
        public_key: str,
        sequence: int
    ):
        self.previous_txid = previous_txid
        self.output_index = output_index
        self.signature = signature
        self.public_key = public_key
        self.sequence = sequence
        
    def __str__(self) -> str:
        return (
            f"TransactionInput:\n"
            f"  Previous TXID: {self.previous_txid}\n"
            f"  Output Index: {self.output_index}\n"
            f"  Script Signature: {self.signature}\n"
            f" Public Key: {self.public_key}\n"
            f"  Sequence: {self.sequence}"
        )
        
        
        
    def to_dict(self) -> dict:
        return {
            "previous_txid": self.previous_txid,
            "output_index": self.output_index,
            "signature": self.signature,
            "public_key": self.public_key,
            "sequence": self.sequence
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            previous_txid=data["previous_txid"],
            output_index=data["output_index"],
            signature=data["signature"],
            public_key=data["public_key"],
            sequence=data["sequence"]
        )
    
class Transaction_Output:
    def __init__(self, value: int, pubkey_hash: str):
        self.value = value
        self.pubkey_hash = pubkey_hash

    def __str__(self) -> str:
        return (
            f"TransactionOutput:\n"
            f"  Value: {self.value}\n"
            f"  pubkey_hash: {self.pubkey_hash}"
        )
        
    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "pubkey_hash": self.pubkey_hash,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            value=data["value"],
            pubkey_hash=data["pubkey_hash"]
        )
    
    
class Transaction:
    def __init__(
        self,
        version: float,
        inputs: List[Transaction_Input],
        outputs: List[Transaction_Output],
    ):
        self.version = 1.0
        self.inputs = inputs
        self.outputs = outputs

    def __str__(self) -> str:
        inputs_str = "\n".join(str(i) for i in self.inputs)
        outputs_str = "\n".join(str(o) for o in self.outputs)

        return (
            f"Transaction:\n"
            f"  # of Inputs: {len(self.inputs)}\n"
            f"  Inputs:\n{inputs_str}\n"
            f"  # of Outputs: {len(self.outputs)}\n"
            f"  Outputs:\n{outputs_str}\n"
        )

    
    
    def to_dict(self) -> dict:
        """
        Convert the transaction into a dictionary for serialization.
        """
        return {
            "version": self.version,
            "inputs": [inp.to_dict() for inp in self.inputs],
            "outputs": [out.to_dict() for out in self.outputs],
        }
    
    @classmethod
    def from_dict(cls, data: dict) : 
        
        inputs = [Transaction_Input.from_dict(i) for i in data["inputs"]]
        outputs = [Transaction_Output.from_dict(o) for o in data["outputs"]]
        
        
        
        return cls(
            version=data["version"],
            inputs=inputs,
            outputs=outputs,
        )
    
    
    def calculate_txid(self) -> str:
        
        raw_string = str(self.to_dict()).encode()
        
        return hashlib.sha256(raw_string).hexdigest()
    
    def calculate_txid_for_signing(self) -> str:
        tx_copy = copy.deepcopy(self)
        for tx_input in tx_copy.inputs:
            tx_input.signature = ""
            tx_input.public_key = ""

        raw_string = str(tx_copy.to_dict()).encode()
        return hashlib.sha256(raw_string).hexdigest()



    def sign_input(self, input_index, private_key_hex):

        tx_input = self.inputs[input_index]
        private_key_bytes = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex), curve = ecdsa.SECP256k1)
        txid_for_signing = self.calculate_txid_for_signing().encode()
        signature_obj = private_key_bytes.sign(txid_for_signing)
        tx_input.signature = signature_obj.hex()
        verifying_key = private_key_bytes.get_verifying_key()
        tx_input.public_key = verifying_key.to_string("compressed").hex()
        self.inputs[input_index] = tx_input


    def verify_input(self, input_index) -> bool:
        tx_input = self.inputs[input_index]
        
        try:
            public_key_bytes = ecdsa.VerifyingKey.from_string(bytes.fromhex(tx_input.public_key), curve = ecdsa.SECP256k1)

        except Exception as e:
            print("Public key is invalid")
        txhash_bytes = self.calculate_txid_for_signing().encode()
        signature_bytes = bytes.fromhex(tx_input.signature)
        try:
            return public_key_bytes.verify(signature_bytes, txhash_bytes)
        except ecdsa.BadSignatureError:
            return False

