#!/usr/bin/env python3
"""
Unit tests for sglang_iterm2_utils.session_management module
"""

import unittest
import asyncio
import inspect
from unittest.mock import Mock, AsyncMock, patch, call
from sglang_iterm2_utils.session_management import restart_all_sessions_in_current_tab


class TestSessionManagement(unittest.TestCase):
    """Test cases for session management functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_connection = Mock()

    def test_restart_all_sessions_function_exists(self):
        """Test that restart_all_sessions_in_current_tab function exists and is callable"""
        self.assertTrue(asyncio.iscoroutinefunction(restart_all_sessions_in_current_tab))

    def test_restart_all_sessions_function_signature(self):
        """Test function signature and parameters"""
        sig = inspect.signature(restart_all_sessions_in_current_tab)
        params = list(sig.parameters.keys())

        self.assertEqual(params, ['connection'])
        self.assertEqual(len(params), 1)

    async def test_restart_all_sessions_no_window(self):
        """Test restart_all_sessions_in_current_tab when no window is available"""
        # Mock iTerm2 app with no current window
        mock_app = Mock()
        mock_app.current_terminal_window = None

        with patch('sglang_iterm2_utils.session_management.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            with patch('builtins.print') as mock_print:
                result = await restart_all_sessions_in_current_tab(self.mock_connection)

                mock_get_app.assert_called_once_with(self.mock_connection)
                mock_print.assert_called_once_with("No active window found.")
                self.assertIsNone(result)

    async def test_restart_all_sessions_no_tab(self):
        """Test restart_all_sessions_in_current_tab when no tab is available"""
        # Mock iTerm2 app with window but no current tab
        mock_window = Mock()
        mock_window.current_tab = None
        mock_app = Mock()
        mock_app.current_terminal_window = mock_window

        with patch('sglang_iterm2_utils.session_management.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            with patch('builtins.print') as mock_print:
                result = await restart_all_sessions_in_current_tab(self.mock_connection)

                mock_get_app.assert_called_once_with(self.mock_connection)
                mock_print.assert_called_once_with("No active tab found in the current window.")
                self.assertIsNone(result)

    async def test_restart_all_sessions_empty_sessions_list(self):
        """Test restart_all_sessions_in_current_tab when there are no sessions"""
        # Mock iTerm2 structure with empty sessions
        mock_tab = Mock()
        mock_tab.tab_id = "empty_tab_456"
        mock_tab.sessions = []
        mock_window = Mock()
        mock_window.current_tab = mock_tab
        mock_app = Mock()
        mock_app.current_terminal_window = mock_window

        with patch('sglang_iterm2_utils.session_management.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            with patch('builtins.print') as mock_print:
                await restart_all_sessions_in_current_tab(self.mock_connection)

                expected_calls = [
                    call(f"Attempting to restart sessions in tab: {mock_tab.tab_id}"),
                    call("All sessions in the current tab have been prompted to restart.")
                ]
                mock_print.assert_has_calls(expected_calls)

    async def test_restart_all_sessions_single_session(self):
        """Test restart_all_sessions_in_current_tab with a single session"""
        # Create a single mock session
        mock_session = Mock()
        mock_session.async_restart = AsyncMock()

        # Mock iTerm2 structure
        mock_tab = Mock()
        mock_tab.tab_id = "single_session_tab"
        mock_tab.sessions = [mock_session]
        mock_window = Mock()
        mock_window.current_tab = mock_tab
        mock_app = Mock()
        mock_app.current_terminal_window = mock_window

        with patch('sglang_iterm2_utils.session_management.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            with patch('builtins.print') as mock_print:
                await restart_all_sessions_in_current_tab(self.mock_connection)

                # Verify the session was restarted
                mock_session.async_restart.assert_called_once()

                # Verify print statements
                expected_calls = [
                    call(f"Attempting to restart sessions in tab: {mock_tab.tab_id}"),
                    call("Restarting session 1 in tab single_session_tab..."),
                    call("All sessions in the current tab have been prompted to restart.")
                ]
                mock_print.assert_has_calls(expected_calls)

    async def test_restart_all_sessions_multiple_sessions(self):
        """Test restart_all_sessions_in_current_tab with multiple sessions"""
        # Create multiple mock sessions
        mock_sessions = []
        for i in range(5):
            session = Mock()
            session.async_restart = AsyncMock()
            mock_sessions.append(session)

        # Mock iTerm2 structure
        mock_tab = Mock()
        mock_tab.tab_id = "multi_session_tab_789"
        mock_tab.sessions = mock_sessions
        mock_window = Mock()
        mock_window.current_tab = mock_tab
        mock_app = Mock()
        mock_app.current_terminal_window = mock_window

        with patch('sglang_iterm2_utils.session_management.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            with patch('builtins.print') as mock_print:
                await restart_all_sessions_in_current_tab(self.mock_connection)

                # Verify that async_restart was called for each session
                for session in mock_sessions:
                    session.async_restart.assert_called_once()

                # Verify print statements
                expected_calls = [
                    call(f"Attempting to restart sessions in tab: {mock_tab.tab_id}"),
                    call("Restarting session 1 in tab multi_session_tab_789..."),
                    call("Restarting session 2 in tab multi_session_tab_789..."),
                    call("Restarting session 3 in tab multi_session_tab_789..."),
                    call("Restarting session 4 in tab multi_session_tab_789..."),
                    call("Restarting session 5 in tab multi_session_tab_789..."),
                    call("All sessions in the current tab have been prompted to restart.")
                ]
                mock_print.assert_has_calls(expected_calls)

    async def test_restart_all_sessions_async_get_app_exception(self):
        """Test restart_all_sessions_in_current_tab when async_get_app raises an exception"""
        with patch('sglang_iterm2_utils.session_management.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.side_effect = Exception("Failed to connect to iTerm2")

            with self.assertRaises(Exception) as context:
                await restart_all_sessions_in_current_tab(self.mock_connection)

            self.assertEqual(str(context.exception), "Failed to connect to iTerm2")
            mock_get_app.assert_called_once_with(self.mock_connection)

    async def test_restart_all_sessions_session_restart_exception(self):
        """Test restart_all_sessions_in_current_tab when session.async_restart raises an exception"""
        # Create a mock session that raises an exception on restart
        mock_session = Mock()
        mock_session.async_restart = AsyncMock(side_effect=Exception("Restart failed"))

        # Mock iTerm2 structure
        mock_tab = Mock()
        mock_tab.tab_id = "exception_tab"
        mock_tab.sessions = [mock_session]
        mock_window = Mock()
        mock_window.current_tab = mock_tab
        mock_app = Mock()
        mock_app.current_terminal_window = mock_window

        with patch('sglang_iterm2_utils.session_management.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            with self.assertRaises(Exception) as context:
                await restart_all_sessions_in_current_tab(self.mock_connection)

            self.assertEqual(str(context.exception), "Restart failed")
            mock_session.async_restart.assert_called_once()

    async def test_restart_all_sessions_with_mixed_session_states(self):
        """Test restart_all_sessions_in_current_tab with sessions having different characteristics"""
        # Create mock sessions with different properties
        mock_sessions = []
        for i in range(3):
            session = Mock()
            session.async_restart = AsyncMock()
            # Add some additional properties to make sessions more realistic
            session.session_id = f"session_{i}"
            session.name = f"Session {i+1}"
            mock_sessions.append(session)

        # Mock iTerm2 structure
        mock_tab = Mock()
        mock_tab.tab_id = "mixed_sessions_tab"
        mock_tab.sessions = mock_sessions
        mock_window = Mock()
        mock_window.current_tab = mock_tab
        mock_app = Mock()
        mock_app.current_terminal_window = mock_window

        with patch('sglang_iterm2_utils.session_management.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            with patch('builtins.print') as mock_print:
                await restart_all_sessions_in_current_tab(self.mock_connection)

                # Verify all sessions were restarted regardless of their properties
                for session in mock_sessions:
                    session.async_restart.assert_called_once()

                # Check that the correct number of session restart messages were printed
                restart_messages = [call for call in mock_print.call_args_list
                                  if "Restarting session" in str(call)]
                self.assertEqual(len(restart_messages), 3)

    def test_restart_all_sessions_module_imports(self):
        """Test that required modules are properly imported"""
        import sglang_iterm2_utils.session_management as sm

        # Check that required modules are available
        self.assertTrue(hasattr(sm, 'iterm2'))
        self.assertTrue(hasattr(sm, 'asyncio'))
        self.assertTrue(hasattr(sm, 'restart_all_sessions_in_current_tab'))

    async def test_restart_all_sessions_connection_parameter_usage(self):
        """Test that the connection parameter is properly used"""
        mock_app = Mock()
        mock_app.current_terminal_window = None

        with patch('sglang_iterm2_utils.session_management.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            # Test with different connection objects
            connections = [Mock(), "test_connection", 12345]

            for connection in connections:
                with patch('builtins.print'):
                    await restart_all_sessions_in_current_tab(connection)
                    mock_get_app.assert_called_with(connection)


class TestSessionManagementAsync(unittest.TestCase):
    """Async test cases for session management"""

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def async_test(self, coro):
        """Helper method to run async tests"""
        return self.loop.run_until_complete(coro)

    def test_restart_all_sessions_async_execution(self):
        """Test that restart_all_sessions_in_current_tab runs asynchronously"""
        async def test_coro():
            mock_connection = Mock()

            # Mock the entire iTerm2 structure
            mock_session = Mock()
            mock_session.async_restart = AsyncMock()

            mock_tab = Mock()
            mock_tab.tab_id = "async_test_tab"
            mock_tab.sessions = [mock_session]

            mock_window = Mock()
            mock_window.current_tab = mock_tab

            mock_app = Mock()
            mock_app.current_terminal_window = mock_window

            with patch('sglang_iterm2_utils.session_management.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
                mock_get_app.return_value = mock_app

                with patch('builtins.print'):
                    await restart_all_sessions_in_current_tab(mock_connection)

                    # Verify the async call was made
                    mock_session.async_restart.assert_called_once()

        self.async_test(test_coro())


if __name__ == '__main__':
    # Run the tests
    print("Running unit tests for session_management module...")
    print("=" * 60)

    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("✅ All session management tests passed!")
    else:
        print("❌ Some session management tests failed!")

    print("=" * 60)
