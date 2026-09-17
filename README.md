# Mini Bitcoin

A Python course project that simulates a small Bitcoin-style blockchain. It includes transactions, wallets, a mempool, block mining, and peer-to-peer node messaging. This is an educational simulation; its coins and addresses are not Bitcoin.

## Run a node

Use Python 3.8 or newer:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py --host 127.0.0.1 --port 8003
```

To connect another local node, start it in a second terminal:

```bash
python main.py --host 127.0.0.1 --port 8004 --peers 127.0.0.1:8003
```

The console menu lets you inspect node status, create wallets and transactions, and mine blocks. `blockchain_test.py` is a standalone demonstration script; `test.py` prints an example key and address.

## Public demo key

The hardcoded `alice` private key in the source and demonstration scripts is deliberately shared so anyone can spend the genesis coins in this simulation. It is public test data. Never send real cryptocurrency to an address derived from it or reuse it in a real wallet.
# MiniBtc
