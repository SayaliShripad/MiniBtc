import ecdsa
import hashlib
import base58


private_key_hex = "c03aad11c3811aaba04074ab580c8c65b42e020b3dfab83758e2bd6ccfd0884e"

private_key_bytes = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex), curve=ecdsa.SECP256k1)

verifying_key = private_key_bytes.get_verifying_key()

public_key_hex = verifying_key.to_string("compressed").hex()

#genereate wallet address

pubkey_bytes = bytes.fromhex(public_key_hex)
pubkey_hash = hashlib.sha256(pubkey_bytes).digest()
versioned_payload = b"\x00" + pubkey_hash
checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
address_bytes = versioned_payload + checksum
wallet_address = base58.b58encode(address_bytes).decode("utf-8")


print(private_key_hex)
print(public_key_hex)
print(wallet_address)