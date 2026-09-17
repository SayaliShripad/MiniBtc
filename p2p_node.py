import asyncio
import json
from typing import List, Tuple

class P2PNode:
    

    def __init__(self, host: str, port: int, known_peers: List[Tuple[str, int]]):
        self.host = host
        self.port = port
        self.known_peers = known_peers

        
        self.active_peers = set()

        
        self.server = None

        
        self.message_handler = None

        self.blockchain = None
        self.mempool = None
        self.aliases = None

    async def start_server(self):
        """Start listening for inbound connections and connect to known peers."""
        self.server = await asyncio.start_server(
            self.handle_connection, self.host, self.port
        )
        print(f"[INFO] Node listening on {self.host}:{self.port}")

        # Attempt to connect to known peers
        for peer_host, peer_port in self.known_peers:
            asyncio.create_task(self.connect_to_peer(peer_host, peer_port))

        # Keep the server running
        async with self.server:
            await self.server.serve_forever()

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """inbound peer connection"""
        peer_name = writer.get_extra_info("peername")
        print(f"[INFO] Inbound connection from {peer_name}")
        self.active_peers.add(writer)

        try:
            while True:
                data = await reader.readline()
                if not data:
                    print(f"[WARN] Connection closed by {peer_name}")
                    break

                message_str = data.decode().strip()
                if message_str:
                    await self.process_incoming_message(message_str, writer)

        except asyncio.CancelledError:
            print(f"[INFO] Connection handler cancelled for {peer_name}")
        finally:
            # Cleanup
            self.active_peers.discard(writer)
            writer.close()
            await writer.wait_closed()

    async def connect_to_peer(self, peer_host: str, peer_port: int):
        """Establish an outbound connection to a peer."""
        try:
            reader, writer = await asyncio.open_connection(peer_host, peer_port)
            self.active_peers.add(writer)
            peer_name = writer.get_extra_info("peername")
            print(f"[INFO] Outbound connection established to {peer_name}")

            # Listen for messages from this peer
            asyncio.create_task(self.listen_to_peer(reader, writer))
        except ConnectionRefusedError:
            print(f"[ERROR] Could not connect to {peer_host}:{peer_port}")
        except Exception as e:
            print(f"[ERROR] Unexpected error connecting to {peer_host}:{peer_port} - {e}")

    async def listen_to_peer(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Listen for messages on an outbound connection."""
        peer_name = writer.get_extra_info("peername")
        while True:
            try:
                data = await reader.readline()
                if not data:
                    print(f"[WARN] Connection closed by {peer_name}")
                    break

                message_str = data.decode().strip()
                if message_str:
                    await self.process_incoming_message(message_str, writer)

            except asyncio.CancelledError:
                print(f"[INFO] Listen task cancelled for {peer_name}")
                break
            except Exception as e:
                print(f"[ERROR] Error listening to {peer_name}: {e}")
                break

        self.active_peers.discard(writer)
        writer.close()
        await writer.wait_closed()

    async def process_incoming_message(self, message_str: str, writer: asyncio.StreamWriter):
        try:
            message = json.loads(message_str)
        except json.JSONDecodeError:
            print(f"[ERROR] Invalid JSON from {writer.get_extra_info('peername')}: {message_str}")
            return

        if self.message_handler:
            await self.message_handler(message, writer, self)
        else:
            print(f"[INFO] Received message but no handler set: {message}")

    async def broadcast(self, message: dict, exclude: asyncio.StreamWriter = None):
        encoded = json.dumps(message) + "\n"
        for peer_writer in list(self.active_peers):
            if peer_writer == exclude:
                continue
            try:
                peer_writer.write(encoded.encode())
                await peer_writer.drain()
            except ConnectionError:
                print("[ERROR] Could not send to peer - removing writer.")
                self.active_peers.discard(peer_writer)
