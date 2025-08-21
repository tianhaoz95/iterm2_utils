"""
Multi-node initialization utilities for iTerm2
"""

import asyncio
import socket
import iterm2


async def multi_node_init(connection):
    """
    Initialize multi-node environment by setting RANK and MAIN_NODE_IP variables.

    This function initializes a multi-node distributed computing environment by:
    1. Clearing all session scrollback buffers
    2. Detecting the main node IP address from the first session
    3. Setting environment variables (RANK and MAIN_NODE_IP) across all sessions

    Each session (panel) receives a unique RANK starting from 0, and all sessions
    receive the same MAIN_NODE_IP for distributed computing coordination.

    Args:
        connection: iTerm2 connection object for communicating with iTerm2

    Returns:
        None: This function performs initialization but doesn't return a value

    Raises:
        Exception: If there are issues accessing iTerm2 app, window, tab, or sessions

    Note:
        This function assumes multiple sessions (panels) are already open in the
        current tab. For single-session setups, the IP detection will be skipped.
    """
    # Get iTerm2 application interface
    app = await iterm2.async_get_app(connection)

    # Validate iTerm2 window exists
    window = app.current_window
    if not window:
        print("No active window found. Please open an iTerm2 window.")
        return

    # Validate iTerm2 tab exists
    tab = window.current_tab
    if not tab:
        print("No active tab found in the current window.")
        return
    
    # Validate sessions (panels) exist
    sessions = tab.sessions
    if not sessions:
        print("No sessions (panels) found in the current tab. Please open some panels.")
        return
    
    print(f"Found {len(sessions)} sessions (panels) in the current tab.")

    # Step 1: Clear all session buffers to ensure clean environment
    await _clear_all_session_buffers(sessions)

    # Step 2: Determine main node IP address
    main_node_ip = await _get_main_node_ip(connection, sessions)
    if not main_node_ip:
        print("Could not determine main node IP. Exiting.")
        return

    # Step 3: Set environment variables across all sessions
    await _set_environment_variables(sessions, main_node_ip)


async def _clear_all_session_buffers(sessions):
    """
    Clear scrollback buffers for all sessions to ensure clean environment.

    Args:
        sessions: List of iTerm2 session objects
    """
    print("Clearing all session buffers...")

    # iTerm2 escape sequence to clear scrollback buffer
    clear_scrollback_code = b'\x1b' + b']1337;ClearScrollback' + b'\x07'

    for session_index, session in enumerate(sessions):
        print(f"Clearing session {session_index} (ID: {session.session_id})")
        await session.async_inject(clear_scrollback_code)
        await asyncio.sleep(0.5)  # Allow time for buffer clearing


async def _get_main_node_ip(connection, sessions):
    """
    Determine the main node IP address from the first session.

    This function attempts to get the IP address by executing a command in the
    first session and parsing the output. If this fails, it falls back to
    detecting the local machine's IP address.

    Args:
        connection: iTerm2 connection object
        sessions: List of iTerm2 session objects

    Returns:
        str: IP address of the main node, or None if detection fails
    """
    # Skip IP detection for single-session setups
    if len(sessions) <= 1:
        print("Single session detected. Using localhost as main node IP.")
        return "127.0.0.1"

    main_node_ip = None
    first_session = sessions[0]

    print(f"Attempting to detect IP from session 0 (ID: {first_session.session_id})...")

    try:
        # Method 1: Try to get IP from first session output
        main_node_ip = await _detect_ip_from_session(connection, first_session)

        if main_node_ip:
            print(f"Successfully detected IP from session 0: {main_node_ip}")
        else:
            print("Could not parse IP from session output. Trying fallback method...")

    except Exception as e:
        print(f"Error detecting IP from session 0: {e}")

    # Method 2: Fallback to local machine IP detection
    if not main_node_ip:
        main_node_ip = _get_local_machine_ip()
    
    return main_node_ip


def _get_local_machine_ip():
    """
    Get the local machine's IP address as fallback.

    Returns:
        str: Local machine IP address, defaults to localhost if detection fails
    """
    print("Using fallback method to detect local machine IP...")

    try:
        # Create socket to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # Connect to non-routable address to find local IP
            sock.connect(('10.255.255.255', 1))
            local_ip = sock.getsockname()[0]

        print(f"Fallback successful: Detected local IP: {local_ip}")
        return local_ip

    except Exception as ex:
        print(f"Fallback failed, using localhost: {ex}")
        return "127.0.0.1"


async def _detect_ip_from_session(connection, session):
    """
    Detect IP address by executing command in session and parsing output.

    Args:
        connection: iTerm2 connection object
        session: iTerm2 session object to execute command in

    Returns:
        str: Detected IP address, or None if detection fails
    """
    # Clear session buffer for clean output
    clear_scrollback_code = b'\x1b' + b']1337;ClearScrollback' + b'\x07'
    await session.async_inject(clear_scrollback_code)
    await asyncio.sleep(0.5)

    # Send IP detection command
    ip_command = "echo MAIN_NODE_IP=$(hostname -I | awk '{print $1}')"
    print(f"Executing IP detection command: '{ip_command}'")
    await session.async_send_text(ip_command + "\n", suppress_broadcast=True)

    # Wait for command execution and output
    wait_time = 4.0
    print(f"Waiting {wait_time} seconds for command output...")
    await asyncio.sleep(wait_time)

    # Retrieve session contents
    lines = []
    async with iterm2.Transaction(connection):
        line_info = await session.async_get_line_info()
        lines = await session.async_get_contents(line_info.overflow, 10)

    print(f"Retrieved {len(lines)} lines from session buffer")

    # Parse IP address from output
    return _parse_ip_from_lines(lines)


def _parse_ip_from_lines(lines):
    """
    Parse IP address from session output lines.

    Args:
        lines: List of iTerm2 line objects from session buffer

    Returns:
        str: Parsed IP address, or None if not found
    """
    for line in lines:
        line_content = line.string.strip()
        print(f"Parsing line: {line_content}")

        # Look for our IP command output pattern
        if line_content.startswith("MAIN_NODE_IP="):
            ip_address = line_content.replace("MAIN_NODE_IP=", "").strip()
            if ip_address and ip_address != "":
                return ip_address

    return None


async def _set_environment_variables(sessions, main_node_ip):
    """
    Set RANK and MAIN_NODE_IP environment variables across all sessions.

    Args:
        sessions: List of iTerm2 session objects
        main_node_ip (str): IP address of the main node
    """
    print(f"Setting environment variables across {len(sessions)} sessions...")

    for index, session in enumerate(sessions):
        # Set RANK environment variable (unique per session)
        rank_command = f"export RANK={index}"
        print(f"Setting RANK={index} in session {index} (ID: {session.session_id})")
        await session.async_send_text(rank_command + "\n", suppress_broadcast=True)

        # Set MAIN_NODE_IP environment variable (same across all sessions)
        ip_command = f'export MAIN_NODE_IP="{main_node_ip}"'
        print(f"Setting MAIN_NODE_IP={main_node_ip} in session {index}")
        await session.async_send_text(ip_command + "\n", suppress_broadcast=True)

        # Small delay to prevent overwhelming the sessions
        await asyncio.sleep(0.1)
    print("Environment variable setup completed for all sessions.")
