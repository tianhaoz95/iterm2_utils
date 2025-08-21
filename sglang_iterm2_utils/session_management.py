"""
Session management utilities for iTerm2
"""

import iterm2
import asyncio


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
