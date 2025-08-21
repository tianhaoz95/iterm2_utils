"""
Unit tests for append_python_path module using pytest
"""

from unittest.mock import AsyncMock, MagicMock, patch, call
import pytest

from sglang_iterm2_utils.append_python_path import append_python_paths


@pytest.fixture
def mock_connection():
    """Mock connection fixture"""
    return MagicMock()


@pytest.fixture
def mock_iterm2_objects():
    """Mock iTerm2 objects fixture"""
    mock_app = AsyncMock()
    mock_window = MagicMock()
    mock_tab = MagicMock()
    mock_session1 = AsyncMock()
    mock_session2 = AsyncMock()

    return {
        'app': mock_app,
        'window': mock_window,
        'tab': mock_tab,
        'session1': mock_session1,
        'session2': mock_session2
    }


@pytest.mark.asyncio
@patch('sglang_iterm2_utils.append_python_path.iterm2.async_get_app')
@patch('builtins.print')
async def test_append_python_paths_success(mock_print, mock_get_app, mock_connection, mock_iterm2_objects):
    """Test successful execution with multiple paths and sessions"""
    # Setup mocks
    mock_get_app.return_value = mock_iterm2_objects['app']
    mock_iterm2_objects['app'].current_terminal_window = mock_iterm2_objects['window']
    mock_iterm2_objects['window'].current_tab = mock_iterm2_objects['tab']
    mock_iterm2_objects['tab'].sessions = [mock_iterm2_objects['session1'], mock_iterm2_objects['session2']]

    # Test data
    python_paths = ["/home/vllm", "/opt/conda/lib/python3.9"]

    # Execute
    await append_python_paths(mock_connection, python_paths)

    # Verify iterm2.async_get_app was called
    mock_get_app.assert_called_once_with(mock_connection)

    # Verify export commands were sent to each session
    expected_calls = [
        call("export PYTHONPATH=/home/vllm:$PYTHONPATH", suppress_broadcast=True),
        call("export PYTHONPATH=/opt/conda/lib/python3.9:$PYTHONPATH", suppress_broadcast=True),
        call("", suppress_broadcast=True)
    ]

    mock_iterm2_objects['session1'].async_send_text.assert_has_calls(expected_calls)
    mock_iterm2_objects['session2'].async_send_text.assert_has_calls(expected_calls)

    # Verify success message
    mock_print.assert_called_once_with("Successfully appended 2 Python paths to 2 sessions.")


@pytest.mark.asyncio
@patch('sglang_iterm2_utils.append_python_path.iterm2.async_get_app')
@patch('builtins.print')
async def test_no_active_window(mock_print, mock_get_app, mock_connection, mock_iterm2_objects):
    """Test behavior when no active window is found"""
    # Setup mocks
    mock_get_app.return_value = mock_iterm2_objects['app']
    mock_iterm2_objects['app'].current_terminal_window = None

    # Test data
    python_paths = ["/home/vllm"]

    # Execute
    await append_python_paths(mock_connection, python_paths)

    # Verify error message and early return
    mock_print.assert_called_once_with("No active window found. Please open an iTerm2 window.")


@pytest.mark.asyncio
@patch('sglang_iterm2_utils.append_python_path.iterm2.async_get_app')
@patch('builtins.print')
async def test_no_active_tab(mock_print, mock_get_app, mock_connection, mock_iterm2_objects):
    """Test behavior when no active tab is found"""
    # Setup mocks
    mock_get_app.return_value = mock_iterm2_objects['app']
    mock_iterm2_objects['app'].current_terminal_window = mock_iterm2_objects['window']
    mock_iterm2_objects['window'].current_tab = None

    # Test data
    python_paths = ["/home/vllm"]

    # Execute
    await append_python_paths(mock_connection, python_paths)

    # Verify error message and early return
    mock_print.assert_called_once_with("No active tab found in the current window.")


@pytest.mark.asyncio
@patch('sglang_iterm2_utils.append_python_path.iterm2.async_get_app')
@patch('builtins.print')
async def test_no_sessions(mock_print, mock_get_app, mock_connection, mock_iterm2_objects):
    """Test behavior when no sessions are found"""
    # Setup mocks
    mock_get_app.return_value = mock_iterm2_objects['app']
    mock_iterm2_objects['app'].current_terminal_window = mock_iterm2_objects['window']
    mock_iterm2_objects['window'].current_tab = mock_iterm2_objects['tab']
    mock_iterm2_objects['tab'].sessions = []

    # Test data
    python_paths = ["/home/vllm"]

    # Execute
    await append_python_paths(mock_connection, python_paths)

    # Verify error message and early return
    mock_print.assert_called_once_with("No sessions (panels) found in the current tab. Please open some panels.")


@pytest.mark.asyncio
@patch('sglang_iterm2_utils.append_python_path.iterm2.async_get_app')
@patch('builtins.print')
async def test_empty_python_paths(mock_print, mock_get_app, mock_connection, mock_iterm2_objects):
    """Test behavior with empty python_paths list"""
    # Setup mocks
    mock_get_app.return_value = mock_iterm2_objects['app']
    mock_iterm2_objects['app'].current_terminal_window = mock_iterm2_objects['window']
    mock_iterm2_objects['window'].current_tab = mock_iterm2_objects['tab']
    mock_iterm2_objects['tab'].sessions = [mock_iterm2_objects['session1']]

    # Test data
    python_paths = []

    # Execute
    await append_python_paths(mock_connection, python_paths)

    # Verify only empty line was sent (to execute commands)
    expected_calls = [call("", suppress_broadcast=True)]
    mock_iterm2_objects['session1'].async_send_text.assert_has_calls(expected_calls)

    # Verify success message with 0 paths
    mock_print.assert_called_once_with("Successfully appended 0 Python paths to 1 sessions.")


@pytest.mark.asyncio
@patch('sglang_iterm2_utils.append_python_path.iterm2.async_get_app')
@patch('builtins.print')
async def test_single_path_single_session(mock_print, mock_get_app, mock_connection, mock_iterm2_objects):
    """Test with single path and single session"""
    # Setup mocks
    mock_get_app.return_value = mock_iterm2_objects['app']
    mock_iterm2_objects['app'].current_terminal_window = mock_iterm2_objects['window']
    mock_iterm2_objects['window'].current_tab = mock_iterm2_objects['tab']
    mock_iterm2_objects['tab'].sessions = [mock_iterm2_objects['session1']]

    # Test data
    python_paths = ["/usr/local/lib/python3.9"]

    # Execute
    await append_python_paths(mock_connection, python_paths)

    # Verify export command was sent
    expected_calls = [
        call("export PYTHONPATH=/usr/local/lib/python3.9:$PYTHONPATH", suppress_broadcast=True),
        call("", suppress_broadcast=True)
    ]
    mock_iterm2_objects['session1'].async_send_text.assert_has_calls(expected_calls)

    # Verify success message
    mock_print.assert_called_once_with("Successfully appended 1 Python paths to 1 sessions.")


@pytest.mark.asyncio
@patch('sglang_iterm2_utils.append_python_path.iterm2.async_get_app')
async def test_export_command_format(mock_get_app, mock_connection, mock_iterm2_objects):
    """Test that export commands are formatted correctly"""
    # Setup mocks
    mock_get_app.return_value = mock_iterm2_objects['app']
    mock_iterm2_objects['app'].current_terminal_window = mock_iterm2_objects['window']
    mock_iterm2_objects['window'].current_tab = mock_iterm2_objects['tab']
    mock_iterm2_objects['tab'].sessions = [mock_iterm2_objects['session1']]

    # Test data with special characters
    python_paths = ["/path/with spaces", "/path-with-dashes", "/path_with_underscores"]

    # Execute
    await append_python_paths(mock_connection, python_paths)

    # Verify exact command format
    expected_calls = [
        call("export PYTHONPATH=/path/with spaces:$PYTHONPATH", suppress_broadcast=True),
        call("export PYTHONPATH=/path-with-dashes:$PYTHONPATH", suppress_broadcast=True),
        call("export PYTHONPATH=/path_with_underscores:$PYTHONPATH", suppress_broadcast=True),
        call("", suppress_broadcast=True)
    ]
    mock_iterm2_objects['session1'].async_send_text.assert_has_calls(expected_calls)


@pytest.mark.asyncio
@patch('sglang_iterm2_utils.append_python_path.iterm2.async_get_app')
async def test_multiple_sessions_distribution(mock_get_app, mock_connection):
    """Test that commands are sent to all sessions correctly"""
    # Setup mocks
    app = AsyncMock()
    window = MagicMock()
    tab = MagicMock()
    sessions = [AsyncMock() for _ in range(3)]  # 3 sessions

    mock_get_app.return_value = app
    app.current_terminal_window = window
    window.current_tab = tab
    tab.sessions = sessions

    # Test data
    python_paths = ["/path1", "/path2"]

    # Execute
    await append_python_paths(mock_connection, python_paths)

    # Verify all sessions received the same commands
    for session in sessions:
        expected_calls = [
            call("export PYTHONPATH=/path1:$PYTHONPATH", suppress_broadcast=True),
            call("export PYTHONPATH=/path2:$PYTHONPATH", suppress_broadcast=True),
            call("", suppress_broadcast=True)
        ]
        session.async_send_text.assert_has_calls(expected_calls)
