import argparse
import threading
import time
import logging
from typing import List, Tuple, Optional
from queue import Queue

import asyncio

from p2p_node import P2PNode
from colorama import init, Fore, Style

from blockchain.Blockchain import Blockchain
from blockchain.mempool import Mempool
from blockchain.Transaction_Structure import Transaction, Transaction_Input, Transaction_Output
from blockchain.miner import mine_block
from blockchain.wallet import Wallet, decode_wallet_address
from message_handler import handle_message


GENESIS_ALIAS = {
    "alice": (
        "c03aad11c3811aaba04074ab580c8c65b42e020b3dfab83758e2bd6ccfd0884e",
        "0279e790cd77e16c688d58d2f1b4ae94981cd94fbf2eba0f80d21d730942514af7",
        "1cCTpAY6DK1Kwz6LoNpuWyFXPaeaJBk858MgHcNiqkLbkMTxfy"
    )
}


class BitcoinNode:
    
    def __init__(self, host: str, port: int, known_peers: List[Tuple[str, int]]):
        self.blockchain = Blockchain()
        self.mempool = Mempool()
        self.message_queue = Queue()
        self.p2p_node = P2PNode(host, port, known_peers)
        self.p2p_node.blockchain = self.blockchain
        self.p2p_node.mempool = self.mempool
        self.running = False
        self.p2p_node.message_handler = handle_message
        self._setup_logging()
        self.loop = None
        self.aliases = dict(GENESIS_ALIAS)
        self.p2p_node.aliases = self.aliases

    def _setup_logging(self):
        self.logger = logging.getLogger('BitcoinNode')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def start(self):
        self.running = True
        self.p2p_thread = threading.Thread(target=self._run_p2p)
        self.p2p_thread.daemon = True
        self.p2p_thread.start()
        self.logger.info(f"Node started on {self.p2p_node.host}:{self.p2p_node.port}")

    def stop(self):
        
        self.running = False
        if hasattr(self, 'p2p_thread'):
            self.p2p_thread.join(timeout=1.0)
        self.logger.info("Node stopped")

    def _run_p2p(self):
        
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.p2p_node.start_server())
        self.loop.run_until_complete(self.p2p_node.start_server())

    

    def handle_block(self, miner_address: str) -> bool:
        self.logger.info("Starting to mine a block...")
        block = mine_block(self.blockchain, self.mempool, miner_address)
        if block:
            self.logger.info("Block mined successfully")

            if self.loop is not None:
                self.loop.call_soon_threadsafe(lambda: asyncio.create_task(
                    self.p2p_node.broadcast({"type": "block", "data": block.to_dict()})
                ))
            return True
        return False



class ConsoleUI:

    
    def __init__(self, node: BitcoinNode):
        self.node = node
        self.logger = logging.getLogger('ConsoleUI')


    def handle_transaction_creation(self):
        from_alias = input("From alias: ")
        if from_alias not in self.node.aliases:
            print("Sender alias not found!")
            return

        to_alias = input("To alias: ")
        if to_alias not in self.node.aliases:
            print("Recipient alias not found!")
            return

        try:
            amount = int(input("Amount: "))
        except ValueError:
            print("Invalid amount!")
            return

        from_priv, from_pub, from_addr = self.node.aliases[from_alias]

        if from_priv is None:
            print(f"{Fore.RED}Cannot create transaction: Private key not available!{Style.RESET_ALL}")
            return
       
        w = Wallet()
        w.load_from_privkey(from_priv) 
        w.address = from_addr

        _, _, to_addr = self.node.aliases[to_alias]

        tx = w.create_transaction(self.node, to_addr, amount)
        if tx:
            print(f"Transaction created and broadcast: {tx.calculate_txid()}")
        else:
            print("Transaction creation failed!")

    
    def display_banner(self):
        BANNER = f"""{Fore.YELLOW}
        .__       ._______________________________  
  _____ |__| ____ |__\______   \__    ___|_   ___ \ 
 /     \|  |/    \|  ||    |  _/ |    |  /    \  \/ 
|  Y Y  \  |   |  \  ||    |   \ |    |  \     \____
|__|_|  /__|___|  /__||______  / |____|   \______  /
      \/        \/           \/                  \/ 
{Style.RESET_ALL}"""

        print(BANNER)
        print(f"{Fore.GREEN}=== Welcome to Mini Bitcoin Node ==={Style.RESET_ALL}")





    def create_wallet(self) -> tuple:
        wallet = Wallet()
        return wallet.private_key, wallet.public_key, wallet.address
    
    def broadcast_alias(self, alias: str, address: str):
        msg = {
            "type": "alias",
            "data": {
                "alias": alias,
                "address": address
            }
        }

        if self.node.loop is not None:
            def do_broadcast():
                asyncio.create_task(self.node.p2p_node.broadcast(msg))
            self.node.loop.call_soon_threadsafe(do_broadcast)

    
    def request_aliases_from_peers(self):
        msg = {"type": "request_aliases"}

        if self.node.loop is not None:
            def do_broadcast():
                asyncio.create_task(self.node.p2p_node.broadcast(msg))
            self.node.loop.call_soon_threadsafe(do_broadcast)

    def show_status(self):
        print("\n=== Node Status ===")
        print(f"Chain Height: {self.node.blockchain.get_height()}")
        print(f"UTXO Count: {len(self.node.blockchain.utxo_set)}")
        print(f"Mempool Size: {len(self.node.mempool.transactions)}")
        print(f"Active Peers: {len(self.node.p2p_node.active_peers)}\n")

    def wallet_menu(self):
        while True:
            print(f"\n{Fore.CYAN}=== Wallet Menu ==={Style.RESET_ALL}")
            print(f"{Fore.GREEN}1.{Style.RESET_ALL} Create New Wallet")
            print(f"{Fore.GREEN}2.{Style.RESET_ALL} Show Balances")
            print(f"{Fore.GREEN}3.{Style.RESET_ALL} Create Transaction")
            print(f"{Fore.GREEN}4.{Style.RESET_ALL} Back to Main Menu")
            print(f"{Fore.GREEN}5.{Style.RESET_ALL} Fetch Aliases from peers")

            choice = input(f"{Fore.MAGENTA}Enter choice: {Style.RESET_ALL}").strip()
            
            if choice == "1":
                alias = input("Enter alias for new wallet: ")
                if alias in self.node.aliases:
                    print("Alias already exists!")
                    continue
                priv, pub, addr = self.create_wallet()
                self.node.aliases[alias] = (priv, pub, addr)
                #new_alias = ("DUMMY", "DUMMY", addr)
                self.broadcast_alias(alias, addr)
                
            elif choice == "2":
                for alias, (_, _, addr) in self.node.aliases.items():
                    utxos = self.node.blockchain.get_utxos_for_wallet(addr)
                    balance = sum(value for (_, _), value in utxos)
                    print(f"{alias}: {balance} coins")
                    
            elif choice == "3":
                self.handle_transaction_creation()
                
            elif choice == "4":
                break

            elif choice == "5":
                self.request_aliases_from_peers()


    def main_loop(self):
        init(autoreset=True)
        self.display_banner()
        while True:
            print(f"{Fore.GREEN}1.{Style.RESET_ALL} Show Node Status")
            print(f"{Fore.GREEN}2.{Style.RESET_ALL} Wallet Menu")
            print(f"{Fore.GREEN}3.{Style.RESET_ALL} Mine Block")
            print(f"{Fore.GREEN}4.{Style.RESET_ALL} Exit")

            choice = input(f"{Fore.MAGENTA}Enter choice: {Style.RESET_ALL}")
            
            if choice == "1":
                self.show_status()
                
            elif choice == "2":
                self.wallet_menu()
                
            elif choice == "3":
                if not self.node.aliases:
                    print("Create a wallet first to receive mining rewards!")
                    continue
                alias = list(self.node.aliases.keys())[0]  
                if self.node.handle_block(self.node.aliases[alias][2]):
                    print("Block mined successfully!")
                else:
                    print("Mining failed!")
                    
            elif choice == "4":
                self.node.stop()
                break

def main():
    parser = argparse.ArgumentParser(description='Mini Bitcoin Node')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8003, help='Port to bind to')
    parser.add_argument('--peers', help='Comma-separated list of peers (host:port)')
    args = parser.parse_args()

    known_peers = []
    if args.peers:
        for peer in args.peers.split(','):
            host, port = peer.split(':')
            known_peers.append((host, int(port)))

    node = BitcoinNode(args.host, args.port, known_peers)
    node.start()

    ui = ConsoleUI(node)
    try:
        ui.main_loop()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        node.stop()

if __name__ == "__main__":
    main()