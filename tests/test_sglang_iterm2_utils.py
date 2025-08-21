#!/usr/bin/env python3
"""
Unit tests for sglang_iterm2_utils package
"""

import unittest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from sglang_iterm2_utils import connect_remote_machines, restart_all_sessions_in_current_tab


class TestSglangIterm2Utils(unittest.TestCase):
    """Test cases for sglang_iterm2_utils package"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_connection = Mock()
        self.remote_hosts = ["192.168.1.100", "192.168.1.101", "192.168.1.102"]
        self.username = "testuser"

    def test_package_imports(self):
        """Test that the package can be imported correctly"""
        import sglang_iterm2_utils

        # Test that we can import the functions
        from sglang_iterm2_utils import connect_remote_machines, restart_all_sessions_in_current_tab

        # Test metadata
        self.assertEqual(sglang_iterm2_utils.__version__, "0.1.0")
        self.assertEqual(sglang_iterm2_utils.__author__, "Your Name")
        self.assertIn("connect_remote_machines", sglang_iterm2_utils.__all__)
        self.assertIn("restart_all_sessions_in_current_tab", sglang_iterm2_utils.__all__)

    def test_connect_remote_machines_function_exists(self):
        """Test that connect_remote_machines function exists and is callable"""
        from sglang_iterm2_utils.ssh_connections import connect_remote_machines
        self.assertTrue(asyncio.iscoroutinefunction(connect_remote_machines))

    async def test_connect_remote_machines_no_window(self):
        """Test connect_remote_machines when no window is available"""
        # Mock iTerm2 app with no current window
        mock_app = Mock()
        mock_app.current_terminal_window = None

        with patch('sglang_iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            with patch('builtins.print') as mock_print:
                result = await connect_remote_machines(
                    self.mock_connection,
                    self.remote_hosts,
                    self.username
                )

                mock_print.assert_called_once_with("No active window found. Please open an iTerm2 window.")
                self.assertIsNone(result)

    async def test_connect_remote_machines_no_tab(self):
        """Test connect_remote_machines when no tab is available"""
        # Mock iTerm2 app with window but no current tab
        mock_window = Mock()
        mock_window.current_tab = None
        mock_app = Mock()
        mock_app.current_terminal_window = mock_window

        with patch('sglang_iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            with patch('builtins.print') as mock_print:
                result = await connect_remote_machines(
                    self.mock_connection,
                    self.remote_hosts,
                    self.username
                )

                mock_print.assert_called_once_with("No active tab found in the current window.")
                self.assertIsNone(result)

    async def test_connect_remote_machines_no_sessions(self):
        """Test connect_remote_machines when no sessions are available"""
        # Mock iTerm2 app with window and tab but no sessions
        mock_tab = Mock()
        mock_tab.sessions = []
        mock_window = Mock()
        mock_window.current_tab = mock_tab
        mock_app = Mock()
        mock_app.current_terminal_window = mock_window

        with patch('sglang_iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            with patch('builtins.print') as mock_print:
                result = await connect_remote_machines(
                    self.mock_connection,
                    self.remote_hosts,
                    self.username
                )

                mock_print.assert_called_once_with("No sessions (panels) found in the current tab. Please open some panels.")
                self.assertIsNone(result)

    async def test_connect_remote_machines_success(self):
        """Test successful execution of connect_remote_machines"""
        # Create mock sessions
        mock_sessions = []
        for i in range(3):
            session = Mock()
            session.async_send_text = AsyncMock()
            mock_sessions.append(session)

        # Mock iTerm2 structure
        mock_tab = Mock()
        mock_tab.sessions = mock_sessions
        mock_window = Mock()
        mock_window.current_tab = mock_tab
        mock_app = Mock()
        mock_app.current_terminal_window = mock_window

        with patch('sglang_iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            await connect_remote_machines(
                self.mock_connection,
                self.remote_hosts,
                self.username
            )

            # Verify that async_send_text was called for each session
            for i, session in enumerate(mock_sessions):
                # Calculate expected host index: (i + 5) % len(remote_hosts)
                expected_host_index = (i + 5) % len(self.remote_hosts)
                expected_host = self.remote_hosts[expected_host_index]
                expected_command = f"ssh {self.username}@{expected_host}"

                session.async_send_text.assert_called_once_with(
                    expected_command,
                    suppress_broadcast=True
                )

    async def test_connect_remote_machines_more_sessions_than_hosts(self):
        """Test connect_remote_machines when there are more sessions than hosts"""
        # Create more sessions than hosts
        mock_sessions = []
        for i in range(5):  # More sessions than hosts (3)
            session = Mock()
            session.async_send_text = AsyncMock()
            mock_sessions.append(session)

        # Mock iTerm2 structure
        mock_tab = Mock()
        mock_tab.sessions = mock_sessions
        mock_window = Mock()
        mock_window.current_tab = mock_tab
        mock_app = Mock()
        mock_app.current_terminal_window = mock_window

        with patch('sglang_iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            await connect_remote_machines(
                self.mock_connection,
                self.remote_hosts,
                self.username
            )

            # Verify that async_send_text was called for each session with cycling hosts
            for i, session in enumerate(mock_sessions):
                expected_host_index = (i + 5) % len(self.remote_hosts)
                expected_host = self.remote_hosts[expected_host_index]
                expected_command = f"ssh {self.username}@{expected_host}"

                session.async_send_text.assert_called_once_with(
                    expected_command,
                    suppress_broadcast=True
                )

    def test_function_signature(self):
        """Test function signature and parameters"""
        import inspect
        from sglang_iterm2_utils.ssh_connections import connect_remote_machines

        sig = inspect.signature(connect_remote_machines)
        params = list(sig.parameters.keys())

        self.assertEqual(params, ['connection', 'remote_hosts', 'username'])
        self.assertTrue(asyncio.iscoroutinefunction(connect_remote_machines))

    def test_restart_all_sessions_function_exists(self):
        """Test that restart_all_sessions_in_current_tab function exists and is callable"""
        from sglang_iterm2_utils.session_management import restart_all_sessions_in_current_tab
        self.assertTrue(asyncio.iscoroutinefunction(restart_all_sessions_in_current_tab))

    async def test_restart_all_sessions_no_window(self):
        """Test restart_all_sessions_in_current_tab when no window is available"""
        # Mock iTerm2 app with no current window
        mock_app = Mock()
        mock_app.current_terminal_window = None

        with patch('sglang_iterm2_utils.session_management.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            with patch('builtins.print') as mock_print:
                result = await restart_all_sessions_in_current_tab(self.mock_connection)

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

                mock_print.assert_called_once_with("No active tab found in the current window.")
                self.assertIsNone(result)

    async def test_restart_all_sessions_success(self):
        """Test successful execution of restart_all_sessions_in_current_tab"""
        # Create mock sessions
        mock_sessions = []
        for i in range(3):
            session = Mock()
            session.async_restart = AsyncMock()
            mock_sessions.append(session)

        # Mock iTerm2 structure
        mock_tab = Mock()
        mock_tab.tab_id = "test_tab_123"
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
                    unittest.mock.call(f"Attempting to restart sessions in tab: {mock_tab.tab_id}"),
                    unittest.mock.call("Restarting session 1 in tab test_tab_123..."),
                    unittest.mock.call("Restarting session 2 in tab test_tab_123..."),
                    unittest.mock.call("Restarting session 3 in tab test_tab_123..."),
                    unittest.mock.call("All sessions in the current tab have been prompted to restart.")
                ]
                mock_print.assert_has_calls(expected_calls)


class AsyncTestCase(unittest.TestCase):
    """Base class for async test cases"""

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def async_test(self, coro):
        """Helper method to run async tests"""
        return self.loop.run_until_complete(coro)


class TestAsync(AsyncTestCase):
    """Test cases that require async execution"""

    def test_connect_remote_machines_async_execution(self):
        """Test that connect_remote_machines runs asynchronously"""
        async def test_coro():
            mock_connection = Mock()
            remote_hosts = ["host1", "host2"]
            username = "testuser"

            # Mock the entire iTerm2 structure
            mock_session = Mock()
            mock_session.async_send_text = AsyncMock()

            mock_tab = Mock()
            mock_tab.sessions = [mock_session]

            mock_window = Mock()
            mock_window.current_tab = mock_tab

            mock_app = Mock()
            mock_app.current_terminal_window = mock_window

            with patch('sglang_iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
                mock_get_app.return_value = mock_app

                await connect_remote_machines(mock_connection, remote_hosts, username)

                # Verify the async call was made
                mock_session.async_send_text.assert_called_once()

        self.async_test(test_coro())


if __name__ == '__main__':
    # Run the tests
    print("Running unit tests for sglang_iterm2_utils package...")
    print("=" * 50)

    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")

    print("=" * 50)
