"""
Python path utilities for iTerm2
"""

import iterm2


async def append_python_paths(connection, python_paths):
    """
    Append Python paths to PYTHONPATH environment variable in all iTerm2 sessions.

    This function distributes Python path export commands across all existing
    iTerm2 sessions (panels) in the current tab. Each session will execute
    the export commands to append the provided paths to PYTHONPATH.

    Args:
        connection: iTerm2 connection object for communicating with iTerm2
        python_paths (list): List of Python paths to append to PYTHONPATH

    Returns:
        None: This function performs actions but doesn't return a value

    Raises:
        Exception: If there are issues with iTerm2 app, window, tab, or sessions

    Example:
        >>> import iterm2
        >>> async def main(connection):
        ...     paths = ["/home/vllm", "/opt/conda/envs/myenv/lib/python3.9/site-packages"]
        ...     await append_python_paths(connection, paths)
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

    # Send export commands to all sessions
    for session in sessions:
        for python_path in python_paths:
            export_command = f"export PYTHONPATH={python_path}:$PYTHONPATH"
            # Send export command to the session without broadcasting to other sessions
            await session.async_send_text(export_command, suppress_broadcast=True)

        # Send an empty line to execute the commands
        await session.async_send_text("", suppress_broadcast=True)

    print(f"Successfully appended {len(python_paths)} Python paths to {len(sessions)} sessions.")
