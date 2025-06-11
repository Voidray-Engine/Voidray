"""
VoidRay Networking Module
Handles multiplayer networking and communication.
"""

from .network_manager import NetworkManager
from .message_system import MessageSystem

try:
    from .multiplayer_manager import MultiplayerManager
    __all__ = ['NetworkManager', 'MessageSystem', 'MultiplayerManager']
except ImportError:
    __all__ = ['NetworkManager', 'MessageSystem']