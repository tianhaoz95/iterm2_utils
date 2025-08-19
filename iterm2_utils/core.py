"""
Core functionality for iterm2_utils package
"""

import iterm2
import asyncio

async def connect_remote_machines(connection, remote_hosts, username):
    """
    Connect to remote machines via SSH in iTerm2 sessions.

    This function distributes SSH connections to remote hosts across existing
    iTerm2 sessions (panels) in the current tab. Each session will connect to
    a different remote host using SSH.

    Args:
        connection: iTerm2 connection object for communicating with iTerm2
        remote_hosts (list): List of remote host addresses/IPs to connect to
        username (str): Username to use for SSH connections

    Returns:
        None: This function performs actions but doesn't return a value

    Raises:
        Exception: If there are issues with iTerm2 app, window, tab, or sessions

    Example:
        >>> import iterm2
        >>> async def main(connection):
        ...     hosts = ["192.168.1.100", "192.168.1.101", "192.168.1.102"]
        ...     await connect_remote_machines(connection, hosts, "admin")
        >>> iterm2.run_until_complete(main)
    """
    app = await iterm2.async_get_app(connection)
    window = app.current_terminal_window
    if not window:
        print("No active window found. Please open an iTerm2 window.")
        return

    tab = window.current_tab
    if not tab:
        print("No active tab found in the current window.")
        return
    
    sessions = tab.sessions
    if not sessions:
        print("No sessions (panels) found in the current tab. Please open some panels.")
        return
    
    remote_hosts_cnt = len(remote_hosts)
    for index, session in enumerate(sessions):
        # Distribute hosts across sessions, with offset to vary the starting point
        activate_remote_host_index = (index + 5) % remote_hosts_cnt
        activate_remote_host = remote_hosts[activate_remote_host_index]
        ssh_command = f"ssh {username}@{activate_remote_host}"
        # Send SSH command to the session without broadcasting to other sessions
        await session.async_send_text(ssh_command, suppress_broadcast=True)

async def restart_all_sessions_in_current_tab(connection):
    """
    Restart all shell sessions within the currently active tab.

    This function restarts each session (pane) in the current tab by calling
    the async_restart() method, which effectively creates a fresh shell instance.

    Args:
        connection: iTerm2 connection object for communicating with iTerm2

    Returns:
        None: This function performs actions but doesn't return a value

    Raises:
        Exception: If there are issues accessing iTerm2 app, window, or tab
    """
    app = await iterm2.async_get_app(connection)
    # Get the current active terminal window
    window = app.current_terminal_window
    if not window:
        print("No active window found.")
        return

    # Get the current active tab within that window
    tab = window.current_tab
    if not tab:
        print("No active tab found in the current window.")
        return

    print(f"Attempting to restart sessions in tab: {tab.tab_id}")

    # Iterate through all sessions (panes) in the current tab
    for i, session in enumerate(tab.sessions):
        print(f"Restarting session {i+1} in tab {tab.tab_id}...")
        # Restart the session, creating a fresh shell instance
        await session.async_restart()
        # Optional: Add a small delay if you encounter issues with rapid restarts
        # await asyncio.sleep(0.1)
    print("All sessions in the current tab have been prompted to restart.")