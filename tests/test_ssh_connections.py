#!/usr/bin/env python3
"""
Unit tests for iterm2_utils.ssh_connections module
"""

import unittest
import asyncio
import inspect
from unittest.mock import Mock, AsyncMock, patch, call
from iterm2_utils.ssh_connections import connect_remote_machines


class TestSSHConnections(unittest.TestCase):
    """Test cases for SSH connection functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_connection = Mock()
        self.remote_hosts = ["192.168.1.100", "192.168.1.101", "192.168.1.102"]
        self.username = "testuser"

    def test_connect_remote_machines_function_exists(self):
        """Test that connect_remote_machines function exists and is callable"""
        self.assertTrue(asyncio.iscoroutinefunction(connect_remote_machines))

    def test_connect_remote_machines_function_signature(self):
        """Test function signature and parameters"""
        sig = inspect.signature(connect_remote_machines)
        params = list(sig.parameters.keys())

        self.assertEqual(params, ['connection', 'remote_hosts', 'username'])
        self.assertEqual(len(params), 3)

    async def test_connect_remote_machines_no_window(self):
        """Test connect_remote_machines when no window is available"""
        # Mock iTerm2 app with no current window
        mock_app = Mock()
        mock_app.current_terminal_window = None

        with patch('iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            with patch('builtins.print') as mock_print:
                result = await connect_remote_machines(
                    self.mock_connection,
                    self.remote_hosts,
                    self.username
                )

                mock_get_app.assert_called_once_with(self.mock_connection)
                mock_print.assert_called_once_with("No active window found. Please open an iTerm2 window.")
                self.assertIsNone(result)

    async def test_connect_remote_machines_no_tab(self):
        """Test connect_remote_machines when no tab is available"""
        # Mock iTerm2 app with window but no current tab
        mock_window = Mock()
        mock_window.current_tab = None
        mock_app = Mock()
        mock_app.current_terminal_window = mock_window

        with patch('iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            with patch('builtins.print') as mock_print:
                result = await connect_remote_machines(
                    self.mock_connection,
                    self.remote_hosts,
                    self.username
                )

                mock_get_app.assert_called_once_with(self.mock_connection)
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

        with patch('iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            with patch('builtins.print') as mock_print:
                result = await connect_remote_machines(
                    self.mock_connection,
                    self.remote_hosts,
                    self.username
                )

                mock_get_app.assert_called_once_with(self.mock_connection)
                mock_print.assert_called_once_with("No sessions (panels) found in the current tab. Please open some panels.")
                self.assertIsNone(result)

    async def test_connect_remote_machines_single_host_single_session(self):
        """Test connect_remote_machines with single host and single session"""
        # Create a single mock session
        mock_session = Mock()
        mock_session.async_send_text = AsyncMock()

        # Mock iTerm2 structure
        mock_tab = Mock()
        mock_tab.sessions = [mock_session]
        mock_window = Mock()
        mock_window.current_tab = mock_tab
        mock_app = Mock()
        mock_app.current_terminal_window = mock_window

        single_host = ["192.168.1.100"]

        with patch('iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            await connect_remote_machines(
                self.mock_connection,
                single_host,
                self.username
            )

            # Verify SSH command was sent
            expected_command = f"ssh {self.username}@{single_host[0]}"
            mock_session.async_send_text.assert_called_once_with(
                expected_command,
                suppress_broadcast=True
            )

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

        with patch('iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
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
        for i in range(7):  # More sessions than hosts (3)
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

        with patch('iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
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

    async def test_connect_remote_machines_more_hosts_than_sessions(self):
        """Test connect_remote_machines when there are more hosts than sessions"""
        # Create fewer sessions than hosts
        mock_sessions = []
        for i in range(2):  # Fewer sessions than hosts (3)
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

        with patch('iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            await connect_remote_machines(
                self.mock_connection,
                self.remote_hosts,
                self.username
            )

            # Verify that only the available sessions get commands
            for i, session in enumerate(mock_sessions):
                expected_host_index = (i + 5) % len(self.remote_hosts)
                expected_host = self.remote_hosts[expected_host_index]
                expected_command = f"ssh {self.username}@{expected_host}"

                session.async_send_text.assert_called_once_with(
                    expected_command,
                    suppress_broadcast=True
                )

    async def test_connect_remote_machines_different_usernames(self):
        """Test connect_remote_machines with different username formats"""
        usernames = ["admin", "root", "user123", "test-user", "user_name"]

        for username in usernames:
            mock_session = Mock()
            mock_session.async_send_text = AsyncMock()

            mock_tab = Mock()
            mock_tab.sessions = [mock_session]
            mock_window = Mock()
            mock_window.current_tab = mock_tab
            mock_app = Mock()
            mock_app.current_terminal_window = mock_window

            with patch('iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
                mock_get_app.return_value = mock_app

                await connect_remote_machines(
                    self.mock_connection,
                    ["test.host.com"],
                    username
                )

                expected_command = f"ssh {username}@test.host.com"
                mock_session.async_send_text.assert_called_once_with(
                    expected_command,
                    suppress_broadcast=True
                )

    async def test_connect_remote_machines_different_host_formats(self):
        """Test connect_remote_machines with different host formats"""
        hosts = [
            ["192.168.1.100"],              # IP address
            ["example.com"],                # Domain name
            ["server01.local"],             # Local domain
            ["10.0.0.1"],                  # Different IP
            ["my-server.example.org"]       # Complex domain
        ]

        for host_list in hosts:
            mock_session = Mock()
            mock_session.async_send_text = AsyncMock()

            mock_tab = Mock()
            mock_tab.sessions = [mock_session]
            mock_window = Mock()
            mock_window.current_tab = mock_tab
            mock_app = Mock()
            mock_app.current_terminal_window = mock_window

            with patch('iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
                mock_get_app.return_value = mock_app

                await connect_remote_machines(
                    self.mock_connection,
                    host_list,
                    "testuser"
                )

                expected_command = f"ssh testuser@{host_list[0]}"
                mock_session.async_send_text.assert_called_once_with(
                    expected_command,
                    suppress_broadcast=True
                )

    async def test_connect_remote_machines_async_get_app_exception(self):
        """Test connect_remote_machines when async_get_app raises an exception"""
        with patch('iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.side_effect = Exception("Failed to connect to iTerm2")

            with self.assertRaises(Exception) as context:
                await connect_remote_machines(
                    self.mock_connection,
                    self.remote_hosts,
                    self.username
                )

            self.assertEqual(str(context.exception), "Failed to connect to iTerm2")
            mock_get_app.assert_called_once_with(self.mock_connection)

    async def test_connect_remote_machines_async_send_text_exception(self):
        """Test connect_remote_machines when async_send_text raises an exception"""
        mock_session = Mock()
        mock_session.async_send_text = AsyncMock(side_effect=Exception("Send text failed"))

        mock_tab = Mock()
        mock_tab.sessions = [mock_session]
        mock_window = Mock()
        mock_window.current_tab = mock_tab
        mock_app = Mock()
        mock_app.current_terminal_window = mock_window

        with patch('iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            with self.assertRaises(Exception) as context:
                await connect_remote_machines(
                    self.mock_connection,
                    self.remote_hosts,
                    self.username
                )

            self.assertEqual(str(context.exception), "Send text failed")

    async def test_connect_remote_machines_empty_host_list(self):
        """Test connect_remote_machines with empty host list"""
        mock_session = Mock()
        mock_session.async_send_text = AsyncMock()

        mock_tab = Mock()
        mock_tab.sessions = [mock_session]
        mock_window = Mock()
        mock_window.current_tab = mock_tab
        mock_app = Mock()
        mock_app.current_terminal_window = mock_window

        with patch('iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            # This should raise a ZeroDivisionError due to modulo operation
            with self.assertRaises(ZeroDivisionError):
                await connect_remote_machines(
                    self.mock_connection,
                    [],  # Empty host list
                    self.username
                )

    def test_connect_remote_machines_module_imports(self):
        """Test that required modules are properly imported"""
        import iterm2_utils.ssh_connections as ssh

        # Check that required modules are available
        self.assertTrue(hasattr(ssh, 'iterm2'))
        self.assertTrue(hasattr(ssh, 'connect_remote_machines'))

    async def test_connect_remote_machines_parameter_validation(self):
        """Test connect_remote_machines with various parameter types"""
        mock_session = Mock()
        mock_session.async_send_text = AsyncMock()

        mock_tab = Mock()
        mock_tab.sessions = [mock_session]
        mock_window = Mock()
        mock_window.current_tab = mock_tab
        mock_app = Mock()
        mock_app.current_terminal_window = mock_window

        with patch('iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
            mock_get_app.return_value = mock_app

            # Test with different connection types
            for connection in [Mock(), "test_connection"]:
                await connect_remote_machines(
                    connection,
                    ["test.host"],
                    "user"
                )
                mock_get_app.assert_called_with(connection)

    def test_connect_remote_machines_host_cycling_logic(self):
        """Test the host cycling logic with various combinations"""
        # Test the mathematical logic behind host distribution
        test_cases = [
            {"sessions": 1, "hosts": 3, "expected_hosts": [2]},  # (0+5) % 3 = 2
            {"sessions": 2, "hosts": 3, "expected_hosts": [2, 0]},  # (0+5)%3=2, (1+5)%3=0
            {"sessions": 3, "hosts": 3, "expected_hosts": [2, 0, 1]},  # (0+5)%3=2, (1+5)%3=0, (2+5)%3=1
            {"sessions": 4, "hosts": 2, "expected_hosts": [1, 0, 1, 0]},  # cycling through 2 hosts
        ]

        for case in test_cases:
            hosts = [f"host{i}" for i in range(case["hosts"])]
            expected_indices = case["expected_hosts"]

            for session_count in [case["sessions"]]:
                actual_indices = []
                for i in range(session_count):
                    host_index = (i + 5) % len(hosts)
                    actual_indices.append(host_index)

                self.assertEqual(actual_indices, expected_indices,
                               f"Failed for {session_count} sessions and {len(hosts)} hosts")


class TestSSHConnectionsAsync(unittest.TestCase):
    """Async test cases for SSH connections"""

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def async_test(self, coro):
        """Helper method to run async tests"""
        return self.loop.run_until_complete(coro)

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

            with patch('iterm2_utils.ssh_connections.iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
                mock_get_app.return_value = mock_app

                await connect_remote_machines(mock_connection, remote_hosts, username)

                # Verify the async call was made
                mock_session.async_send_text.assert_called_once()

        self.async_test(test_coro())


if __name__ == '__main__':
    # Run the tests
    print("Running unit tests for ssh_connections module...")
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
        print("✅ All SSH connection tests passed!")
    else:
        print("❌ Some SSH connection tests failed!")

    print("=" * 60)
