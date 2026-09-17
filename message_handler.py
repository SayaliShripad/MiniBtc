
import asyncio
import json
import logging

from blockchain.Transaction_Structure import Transaction
from blockchain.Block import Block
from blockchain.Blockchain import Blockchain
from blockchain.mempool import Mempool
from blockchain.tx_validation import validate_transaction
from blockchain.process_block import process_block

logger = logging.getLogger('BitcoinNode')

async def handle_message(message: dict, writer: asyncio.StreamWriter, node):

    msg_type = message.get("type")
    peer_info = writer.get_extra_info("peername")
    


    if msg_type == "tx":
        tx_data = message.get("data")
        try:
            tx = Transaction.from_dict(tx_data)
            logger.info(f"[Node-{node.port}] Received TX from {peer_info}, TXID={tx.calculate_txid()[:8]}")
        except Exception as e:
            logging.error(f"Could not parse transaction: {e}")
        if validate_transaction(tx, node.blockchain):
            added = node.mempool.add_transaction(tx, node.blockchain)
            if added:
                logger.info(f"[Node-{node.port}] Added TX to mempool: {tx.calculate_txid()[:8]}")
                await node.broadcast(message, exclude= writer)
            else:
                logger.warning(f"[Node-{node.port}] TX already in mempool: {tx.calculate_txid()[:8]}")
        else:
            logger.warning(f"[Node-{node.port}] Invalid TX received from {peer_info}. Ignoring.")

    elif msg_type == "block":
        block_data = message.get("data")
        try:
            block = Block.from_dict(block_data)
            logger.info(f"[Node-{node.port}] Received Block from {peer_info}, BlockHash={block.calculate_block_hash()[:8]}")
        except Exception as e:
            logging.error(f"Could not parse block: {e}")
        
        if process_block(node.blockchain, node.mempool, block):
            logger.info(f"[Node-{node.port}] Added Block to blockchain: {block.calculate_block_hash()[:8]}")
            logger.info(
                f"[Node-{node.port}] Chain height: {node.blockchain.get_height()}, "
                f"UTXO count: {len(node.blockchain.utxo_set)}, "
                f"Mempool: {len(node.mempool.transactions)}"
                )

            await node.broadcast(message, exclude= writer)
        else:
            logger.warning(f"[Node-{node.port}] Invalid Block/ Block already existing received from {peer_info}. Ignoring.")
        
    elif msg_type == "alias":
        alias_data = message.get("data")
        alias_str = alias_data.get("alias")
        public_key = alias_data.get("public_key")
        private_key = alias_data.get("private_key")
        address = alias_data.get("address")

        if alias_str and address:
            if alias_str not in node.aliases:
                node.aliases[alias_str] = (private_key, public_key, address)
                logger.info(f"[Node-{node.port}] Added alias {alias_str} -> {address}")

                await node.broadcast(message, exclude= writer)
            else:
                logger.warning(f"[Node-{node.port}] Alias {alias_str} already exists. Ignoring.")
        else:
            logger.warning(f"[Node-{node.port}] Invalid alias data received from {peer_info}. Ignoring.")

    elif msg_type == "request_aliases":
        logger.info(f"[Node-{node.port}] Received request for aliases from {peer_info}")

        all_aliases_dict = node.aliases
        msg = {
            "type": "aliases",
            "data": all_aliases_dict
        }
        msg_str = json.dumps(msg) + "\n"
        writer.write(msg_str.encode())
        await writer.drain()

    elif msg_type == "aliases":
        logger.info(f"[Node-{node.port}] Received aliases from {peer_info}")
        all_aliases_dict = message.get("data")
        for alias, address in all_aliases_dict.items():
            if alias not in node.aliases:
                node.aliases[alias] = address
                logger.info(f"[Node-{node.port}] Added alias {alias} -> {address}")
