
"""
VoidRay Network Manager
Handles client-server communication for multiplayer games.
"""

import socket
import threading
import json
from typing import Dict, Callable, Any, Optional
from dataclasses import dataclass
from queue import Queue, Empty

@dataclass
class NetworkMessage:
    """Network message structure."""
    type: str
    data: Dict[str, Any]
    sender_id: Optional[str] = None
    timestamp: float = 0.0

class NetworkManager:
    """
    Basic networking manager for multiplayer games.
    Supports both client and server modes.
    """
    
    def __init__(self, is_server: bool = False):
        """
        Initialize network manager.
        
        Args:
            is_server: Whether this instance acts as a server
        """
        self.is_server = is_server
        self.socket = None
        self.running = False
        self.clients: Dict[str, socket.socket] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.incoming_messages: Queue = Queue()
        self.outgoing_messages: Queue = Queue()
        
        self.host = "0.0.0.0"
        self.port = 12345
        
    def start_server(self, host: str = "0.0.0.0", port: int = 12345):
        """Start as server."""
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket.bind((host, port))
            self.socket.listen(5)
            self.running = True
            
            print(f"Server started on {host}:{port}")
            
            # Start accepting connections
            threading.Thread(target=self._accept_connections, daemon=True).start()
            threading.Thread(target=self._process_messages, daemon=True).start()
            
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
        
        return True
    
    def connect_to_server(self, host: str, port: int = 12345) -> bool:
        """Connect as client."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.socket.connect((host, port))
            self.running = True
            
            print(f"Connected to server {host}:{port}")
            
            # Start message processing
            threading.Thread(target=self._receive_messages, daemon=True).start()
            threading.Thread(target=self._process_messages, daemon=True).start()
            
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False
        
        return True
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register a handler for specific message types."""
        self.message_handlers[message_type] = handler
    
    def send_message(self, message_type: str, data: Dict[str, Any], target_client: str = None):
        """Send a message."""
        message = NetworkMessage(message_type, data)
        self.outgoing_messages.put((message, target_client))
    
    def update(self):
        """Process incoming messages. Call this in your main game loop."""
        try:
            while True:
                message = self.incoming_messages.get_nowait()
                if message.type in self.message_handlers:
                    self.message_handlers[message.type](message)
        except Empty:
            pass
    
    def _accept_connections(self):
        """Accept new client connections (server only)."""
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                client_id = f"client_{len(self.clients)}"
                self.clients[client_id] = client_socket
                
                print(f"Client {client_id} connected from {address}")
                
                # Start receiving messages from this client
                threading.Thread(
                    target=self._receive_client_messages, 
                    args=(client_socket, client_id),
                    daemon=True
                ).start()
                
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
    
    def _receive_client_messages(self, client_socket: socket.socket, client_id: str):
        """Receive messages from a specific client."""
        while self.running:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                message_data = json.loads(data.decode())
                message = NetworkMessage(
                    message_data['type'],
                    message_data['data'],
                    client_id
                )
                self.incoming_messages.put(message)
                
            except Exception as e:
                print(f"Error receiving from {client_id}: {e}")
                break
        
        # Clean up disconnected client
        if client_id in self.clients:
            del self.clients[client_id]
        client_socket.close()
    
    def _receive_messages(self):
        """Receive messages (client only)."""
        while self.running:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                
                message_data = json.loads(data.decode())
                message = NetworkMessage(
                    message_data['type'],
                    message_data['data']
                )
                self.incoming_messages.put(message)
                
            except Exception as e:
                if self.running:
                    print(f"Error receiving message: {e}")
                break
    
    def _process_messages(self):
        """Process outgoing messages."""
        while self.running:
            try:
                message, target_client = self.outgoing_messages.get(timeout=1.0)
                message_data = {
                    'type': message.type,
                    'data': message.data
                }
                encoded_data = json.dumps(message_data).encode()
                
                if self.is_server:
                    if target_client and target_client in self.clients:
                        # Send to specific client
                        self.clients[target_client].send(encoded_data)
                    else:
                        # Broadcast to all clients
                        for client_socket in self.clients.values():
                            try:
                                client_socket.send(encoded_data)
                            except:
                                pass  # Client may have disconnected
                else:
                    # Send to server
                    self.socket.send(encoded_data)
                    
            except Empty:
                continue
            except Exception as e:
                print(f"Error sending message: {e}")
    
    def disconnect(self):
        """Disconnect and clean up."""
        self.running = False
        
        if self.socket:
            self.socket.close()
        
        for client_socket in self.clients.values():
            client_socket.close()
        
        self.clients.clear()
        print("Network manager disconnected")
