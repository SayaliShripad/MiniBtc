import hashlib

def compute_merkle_root(txids):
    
    if not txids:
        return "0" * 64  # or some default

    current_hashes = txids[:]

    while len(current_hashes) > 1:
        new_level = []
        # Pair up
        for i in range(0, len(current_hashes), 2):
            left = current_hashes[i]
            if i + 1 < len(current_hashes):
                right = current_hashes[i + 1]
            else:
                # If odd number of hashes, reuse the last one (not exactly how Bitcoin does it, but close)
                right = left

            combined = left + right
            new_hash = hashlib.sha256(combined.encode()).hexdigest()
            new_level.append(new_hash)

        current_hashes = new_level

    return current_hashes[0]
