
"""
VoidRay Enhanced Multiplayer Manager
Advanced multiplayer system with better networking and synchronization.
"""

import socket
import threading
import json
import time
from typing import Dict, Callable, Any, Optional, List
from dataclasses import dataclass
from queue import Queue, Empty
from enum import Enum


class NetworkEvent(Enum):
    """Network event types."""
    PLAYER_JOINED = "player_joined"
    PLAYER_LEFT = "player_left"
    PLAYER_MOVED = "player_moved"
    GAME_STATE_UPDATE = "game_state_update"
    CUSTOM_MESSAGE = "custom_message"


@dataclass
class NetworkMessage:
    """Enhanced network message structure."""
    type: str
    data: Dict[str, Any]
    sender_id: Optional[str] = None
    timestamp: float = 0.0
    sequence_id: int = 0
    reliable: bool = True


@dataclass
class PlayerInfo:
    """Player information structure."""
    id: str
    name: str
    position: Dict[str, float]
    color: List[int]
    score: int = 0
    ping: float = 0.0
    last_update: float = 0.0


class MultiplayerManager:
    """
    Enhanced multiplayer manager with improved networking and game state sync.
    """
    
    def __init__(self, is_server: bool = False, max_players: int = 8):
        """
        Initialize multiplayer manager.
        
        Args:
            is_server: Whether this instance acts as a server
            max_players: Maximum number of players allowed
        """
        self.is_server = is_server
        self.max_players = max_players
        self.socket = None
        self.running = False
        
        # Player management
        self.players: Dict[str, PlayerInfo] = {}
        self.local_player_id: Optional[str] = None
        
        # Network management
        self.clients: Dict[str, socket.socket] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.incoming_messages: Queue = Queue()
        self.outgoing_messages: Queue = Queue()
        
        # Enhanced features
        self.game_state: Dict[str, Any] = {}
        self.message_sequence = 0
        self.heartbeat_interval = 5.0
        self.timeout_duration = 15.0
        
        # Network settings
        self.host = "0.0.0.0"
        self.port = 12345
        self.buffer_size = 4096
        
        # Statistics
        self.network_stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'ping_times': {}
        }
        
        # Register default handlers
        self._register_default_handlers()
        
    def _register_default_handlers(self):
        """Register default message handlers."""
        self.register_message_handler("heartbeat", self._handle_heartbeat)
        self.register_message_handler("player_update", self._handle_player_update)
        self.register_message_handler("game_state", self._handle_game_state)
        self.register_message_handler("ping", self._handle_ping)
        
    def start_server(self, host: str = "0.0.0.0", port: int = 12345) -> bool:
        """Start multiplayer server."""
        self.host = host
        self.port = port
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((host, port))
            self.socket.listen(self.max_players)
            self.running = True
            
            print(f"Multiplayer server started on {host}:{port}")
            print(f"Max players: {self.max_players}")
            
            # Start server threads
            threading.Thread(target=self._accept_connections, daemon=True).start()
            threading.Thread(target=self._process_messages, daemon=True).start()
            threading.Thread(target=self._heartbeat_loop, daemon=True).start()
            threading.Thread(target=self._cleanup_loop, daemon=True).start()
            
            return True
            
        except Exception as e:
            print(f"Failed to start multiplayer server: {e}")
            return False
    
    def connect_to_server(self, host: str, port: int = 12345, player_name: str = "Player") -> bool:
        """Connect to multiplayer server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)  # Connection timeout
            self.socket.connect((host, port))
            self.running = True
            
            # Generate local player ID
            self.local_player_id = f"player_{int(time.time() * 1000) % 10000}"
            
            # Create local player info
            self.players[self.local_player_id] = PlayerInfo(
                id=self.local_player_id,
                name=player_name,
                position={'x': 0, 'y': 0},
                color=[255, 255, 255]
            )
            
            print(f"Connected to multiplayer server {host}:{port}")
            print(f"Player ID: {self.local_player_id}")
            
            # Start client threads
            threading.Thread(target=self._receive_messages, daemon=True).start()
            threading.Thread(target=self._process_messages, daemon=True).start()
            threading.Thread(target=self._heartbeat_loop, daemon=True).start()
            
            # Send join message
            self.send_message("player_join", {
                'player_id': self.local_player_id,
                'name': player_name,
                'position': {'x': 0, 'y': 0}
            })
            
            return True
            
        except Exception as e:
            print(f"Failed to connect to multiplayer server: {e}")
            return False
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register a handler for specific message types."""
        self.message_handlers[message_type] = handler
    
    def send_message(self, message_type: str, data: Dict[str, Any], 
                    target_player: str = None, reliable: bool = True):
        """Send a message with enhanced options."""
        self.message_sequence += 1
        message = NetworkMessage(
            type=message_type,
            data=data,
            sender_id=self.local_player_id,
            timestamp=time.time(),
            sequence_id=self.message_sequence,
            reliable=reliable
        )
        
        self.outgoing_messages.put((message, target_player))
        self.network_stats['messages_sent'] += 1
    
    def update_player_position(self, player_id: str, x: float, y: float):
        """Update player position and sync with network."""
        if player_id in self.players:
            self.players[player_id].position = {'x': x, 'y': y}
            self.players[player_id].last_update = time.time()
            
            # Send update if this is the local player
            if player_id == self.local_player_id:
                self.send_message("player_update", {
                    'player_id': player_id,
                    'position': {'x': x, 'y': y},
                    'timestamp': time.time()
                })
    
    def get_players(self) -> Dict[str, PlayerInfo]:
        """Get all connected players."""
        return self.players.copy()
    
    def get_player_count(self) -> int:
        """Get number of connected players."""
        return len(self.players)
    
    def set_game_state(self, state: Dict[str, Any]):
        """Set and broadcast game state (server only)."""
        if self.is_server:
            self.game_state = state
            self.send_message("game_state", state)
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state."""
        return self.game_state.copy()
    
    def update(self):
        """Process network messages. Call this in your main game loop."""
        processed = 0
        
        try:
            while processed < 50:  # Limit processing per frame
                message = self.incoming_messages.get_nowait()
                
                if message.type in self.message_handlers:
                    try:
                        self.message_handlers[message.type](message)
                    except Exception as e:
                        print(f"Error handling message {message.type}: {e}")
                
                processed += 1
                
        except Empty:
            pass
        
        # Clean up timed out players
        self._cleanup_players()
    
    def _handle_heartbeat(self, message: NetworkMessage):
        """Handle heartbeat messages."""
        if message.sender_id in self.players:
            self.players[message.sender_id].last_update = time.time()
            
            # Respond with heartbeat if we're the server
            if self.is_server:
                self.send_message("heartbeat_response", {
                    'timestamp': time.time()
                }, message.sender_id)
    
    def _handle_player_update(self, message: NetworkMessage):
        """Handle player position updates."""
        data = message.data
        player_id = data.get('player_id')
        
        if player_id and player_id in self.players:
            position = data.get('position', {})
            self.players[player_id].position = position
            self.players[player_id].last_update = time.time()
    
    def _handle_game_state(self, message: NetworkMessage):
        """Handle game state updates."""
        self.game_state = message.data
    
    def _handle_ping(self, message: NetworkMessage):
        """Handle ping requests."""
        if message.data.get('type') == 'request':
            # Send ping response
            self.send_message("ping", {
                'type': 'response',
                'timestamp': message.data.get('timestamp'),
                'server_time': time.time()
            }, message.sender_id)
        elif message.data.get('type') == 'response':
            # Calculate ping
            original_time = message.data.get('timestamp', 0)
            ping_time = (time.time() - original_time) * 1000  # ms
            
            if message.sender_id:
                self.network_stats['ping_times'][message.sender_id] = ping_time
                if message.sender_id in self.players:
                    self.players[message.sender_id].ping = ping_time
    
    def _accept_connections(self):
        """Accept new client connections (server only)."""
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                
                if len(self.clients) >= self.max_players:
                    # Server full
                    client_socket.send(json.dumps({
                        'type': 'server_full',
                        'data': {'message': 'Server is full'}
                    }).encode())
                    client_socket.close()
                    continue
                
                client_id = f"client_{len(self.clients)}_{int(time.time())}"
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
                data = client_socket.recv(self.buffer_size)
                if not data:
                    break
                
                # Handle multiple messages in one packet
                messages = data.decode().strip().split('\n')
                
                for msg_str in messages:
                    if msg_str:
                        try:
                            message_data = json.loads(msg_str)
                            message = NetworkMessage(
                                type=message_data['type'],
                                data=message_data['data'],
                                sender_id=client_id,
                                timestamp=message_data.get('timestamp', time.time()),
                                sequence_id=message_data.get('sequence_id', 0)
                            )
                            self.incoming_messages.put(message)
                            self.network_stats['messages_received'] += 1
                            self.network_stats['bytes_received'] += len(data)
                            
                        except json.JSONDecodeError:
                            print(f"Invalid JSON from {client_id}")
                
            except Exception as e:
                print(f"Error receiving from {client_id}: {e}")
                break
        
        # Clean up disconnected client
        self._disconnect_client(client_id)
    
    def _receive_messages(self):
        """Receive messages from server (client only)."""
        while self.running:
            try:
                data = self.socket.recv(self.buffer_size)
                if not data:
                    break
                
                # Handle multiple messages
                messages = data.decode().strip().split('\n')
                
                for msg_str in messages:
                    if msg_str:
                        try:
                            message_data = json.loads(msg_str)
                            message = NetworkMessage(
                                type=message_data['type'],
                                data=message_data['data'],
                                timestamp=message_data.get('timestamp', time.time()),
                                sequence_id=message_data.get('sequence_id', 0)
                            )
                            self.incoming_messages.put(message)
                            self.network_stats['messages_received'] += 1
                            self.network_stats['bytes_received'] += len(data)
                            
                        except json.JSONDecodeError:
                            print("Invalid JSON from server")
                
            except Exception as e:
                if self.running:
                    print(f"Error receiving from server: {e}")
                break
    
    def _process_messages(self):
        """Process outgoing messages."""
        while self.running:
            try:
                message, target_player = self.outgoing_messages.get(timeout=1.0)
                
                message_data = {
                    'type': message.type,
                    'data': message.data,
                    'timestamp': message.timestamp,
                    'sequence_id': message.sequence_id
                }
                
                encoded_data = (json.dumps(message_data) + '\n').encode()
                
                if self.is_server:
                    if target_player and target_player in self.clients:
                        # Send to specific client
                        try:
                            self.clients[target_player].send(encoded_data)
                            self.network_stats['bytes_sent'] += len(encoded_data)
                        except:
                            self._disconnect_client(target_player)
                    else:
                        # Broadcast to all clients
                        disconnected_clients = []
                        for client_id, client_socket in self.clients.items():
                            try:
                                client_socket.send(encoded_data)
                                self.network_stats['bytes_sent'] += len(encoded_data)
                            except:
                                disconnected_clients.append(client_id)
                        
                        # Clean up disconnected clients
                        for client_id in disconnected_clients:
                            self._disconnect_client(client_id)
                else:
                    # Send to server
                    try:
                        self.socket.send(encoded_data)
                        self.network_stats['bytes_sent'] += len(encoded_data)
                    except Exception as e:
                        print(f"Error sending to server: {e}")
                        self.running = False
                        
            except Empty:
                continue
            except Exception as e:
                print(f"Error processing messages: {e}")
    
    def _heartbeat_loop(self):
        """Send periodic heartbeat messages."""
        while self.running:
            time.sleep(self.heartbeat_interval)
            
            if self.running:
                self.send_message("heartbeat", {
                    'timestamp': time.time(),
                    'player_count': len(self.players)
                })
    
    def _cleanup_loop(self):
        """Periodic cleanup of timed out connections."""
        while self.running:
            time.sleep(5.0)  # Check every 5 seconds
            self._cleanup_players()
    
    def _cleanup_players(self):
        """Remove timed out players."""
        current_time = time.time()
        timed_out_players = []
        
        for player_id, player in self.players.items():
            if current_time - player.last_update > self.timeout_duration:
                timed_out_players.append(player_id)
        
        for player_id in timed_out_players:
            print(f"Player {player_id} timed out")
            if player_id in self.players:
                del self.players[player_id]
            
            # Notify other players
            self.send_message("player_left", {'player_id': player_id})
    
    def _disconnect_client(self, client_id: str):
        """Disconnect a specific client."""
        if client_id in self.clients:
            try:
                self.clients[client_id].close()
            except:
                pass
            del self.clients[client_id]
        
        # Remove player if exists
        if client_id in self.players:
            print(f"Player {self.players[client_id].name} disconnected")
            del self.players[client_id]
        
        print(f"Client {client_id} disconnected")
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics."""
        return {
            'connected_players': len(self.players),
            'messages_sent': self.network_stats['messages_sent'],
            'messages_received': self.network_stats['messages_received'],
            'bytes_sent': self.network_stats['bytes_sent'],
            'bytes_received': self.network_stats['bytes_received'],
            'ping_times': self.network_stats['ping_times'].copy(),
            'server_running': self.is_server and self.running
        }
    
    def disconnect(self):
        """Disconnect and clean up."""
        print("Disconnecting from multiplayer...")
        
        # Send disconnect message
        if self.local_player_id:
            self.send_message("player_left", {'player_id': self.local_player_id})
        
        self.running = False
        
        # Close sockets
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        for client_socket in self.clients.values():
            try:
                client_socket.close()
            except:
                pass
        
        # Clear data
        self.clients.clear()
        self.players.clear()
        
        print("Multiplayer disconnected")
