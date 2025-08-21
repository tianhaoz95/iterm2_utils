"""
iterm2_utils - Utilities for iTerm2 automation and remote machine management
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .ssh_connections import connect_remote_machines
from .session_management import restart_all_sessions_in_current_tab
from .multi_node_init import multi_node_init

__all__ = ["connect_remote_machines", "restart_all_sessions_in_current_tab", "multi_node_init"]
