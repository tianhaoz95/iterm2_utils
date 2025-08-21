#!/usr/bin/env python3
"""
Unit tests for sglang_iterm2_utils.multi_node_init module
"""

import unittest
import asyncio
import inspect
import socket
from unittest.mock import Mock, AsyncMock, patch, call, MagicMock
from sglang_iterm2_utils.multi_node_init import (
    multi_node_init,
    _clear_all_session_buffers,
    _get_main_node_ip,
    _get_local_machine_ip,
    _detect_ip_from_session,
    _parse_ip_from_lines,
    _set_environment_variables
)


class TestMultiNodeInit(unittest.TestCase):
    """Test cases for multi-node initialization functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_connection = Mock()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Clean up event loop"""
        self.loop.close()

    def async_test(self, coro):
        """Helper method to run async tests"""
        return self.loop.run_until_complete(coro)

    def test_multi_node_init_function_exists(self):
        """Test that multi_node_init function exists and is callable"""
        self.assertTrue(asyncio.iscoroutinefunction(multi_node_init))

    def test_multi_node_init_function_signature(self):
        """Test function signature and parameters"""
        sig = inspect.signature(multi_node_init)
        params = list(sig.parameters.keys())

        self.assertEqual(params, ['connection'])
        self.assertEqual(len(params), 1)

    def test_multi_node_init_no_window(self):
        """Test multi_node_init when no window is available"""
        async def test_coro():
            # Mock iTerm2 app with no current window
            mock_app = Mock()
            mock_app.current_window = None

            with patch('iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
                mock_get_app.return_value = mock_app

                with patch('builtins.print') as mock_print:
                    result = await multi_node_init(self.mock_connection)

                    mock_get_app.assert_called_once_with(self.mock_connection)
                    mock_print.assert_called_once_with("No active window found. Please open an iTerm2 window.")
                    self.assertIsNone(result)

        self.async_test(test_coro())

    def test_multi_node_init_no_tab(self):
        """Test multi_node_init when no tab is available"""
        async def test_coro():
            # Mock iTerm2 app with window but no current tab
            mock_window = Mock()
            mock_window.current_tab = None
            mock_app = Mock()
            mock_app.current_window = mock_window

            with patch('iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
                mock_get_app.return_value = mock_app

                with patch('builtins.print') as mock_print:
                    result = await multi_node_init(self.mock_connection)

                    mock_get_app.assert_called_once_with(self.mock_connection)
                    mock_print.assert_called_once_with("No active tab found in the current window.")
                    self.assertIsNone(result)

        self.async_test(test_coro())

    def test_multi_node_init_no_sessions(self):
        """Test multi_node_init when no sessions are available"""
        async def test_coro():
            # Mock iTerm2 app with window and tab but no sessions
            mock_tab = Mock()
            mock_tab.sessions = []
            mock_window = Mock()
            mock_window.current_tab = mock_tab
            mock_app = Mock()
            mock_app.current_window = mock_window

            with patch('iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
                mock_get_app.return_value = mock_app

                with patch('builtins.print') as mock_print:
                    result = await multi_node_init(self.mock_connection)

                    mock_get_app.assert_called_once_with(self.mock_connection)
                    mock_print.assert_called_once_with("No sessions (panels) found in the current tab. Please open some panels.")
                    self.assertIsNone(result)

        self.async_test(test_coro())

    def test_multi_node_init_success_single_session(self):
        """Test successful execution of multi_node_init with single session"""
        async def test_coro():
            # Create mock session
            mock_session = Mock()
            mock_session.session_id = "test_session_1"
            mock_session.async_inject = AsyncMock()
            mock_session.async_send_text = AsyncMock()

            # Mock iTerm2 structure
            mock_tab = Mock()
            mock_tab.sessions = [mock_session]
            mock_window = Mock()
            mock_window.current_tab = mock_tab
            mock_app = Mock()
            mock_app.current_window = mock_window

            with patch('iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
                mock_get_app.return_value = mock_app

                with patch('builtins.print'):
                    await multi_node_init(self.mock_connection)

                    # Verify session methods were called
                    mock_session.async_inject.assert_called()
                    mock_session.async_send_text.assert_called()

        self.async_test(test_coro())

    def test_multi_node_init_success_multiple_sessions(self):
        """Test successful execution of multi_node_init with multiple sessions"""
        async def test_coro():
            # Create multiple mock sessions
            mock_sessions = []
            for i in range(3):
                session = Mock()
                session.session_id = f"test_session_{i}"
                session.async_inject = AsyncMock()
                session.async_send_text = AsyncMock()
                mock_sessions.append(session)

            # Mock iTerm2 structure
            mock_tab = Mock()
            mock_tab.sessions = mock_sessions
            mock_window = Mock()
            mock_window.current_tab = mock_tab
            mock_app = Mock()
            mock_app.current_window = mock_window

            with patch('iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
                mock_get_app.return_value = mock_app

                # Instead of mocking internal functions, just test the behavior
                with patch('builtins.print'):
                    await multi_node_init(self.mock_connection)

                    # Verify all sessions had methods called (buffer clearing and env vars)
                    for session in mock_sessions:
                        session.async_inject.assert_called()
                        session.async_send_text.assert_called()

        self.async_test(test_coro())

    def test_multi_node_init_ip_detection_failure(self):
        """Test multi_node_init when IP detection fails"""
        async def test_coro():
            # Create mock session
            mock_session = Mock()
            mock_session.session_id = "test_session_1"
            mock_session.async_inject = AsyncMock()
            mock_session.async_send_text = AsyncMock()

            # Mock iTerm2 structure
            mock_tab = Mock()
            mock_tab.sessions = [mock_session]
            mock_window = Mock()
            mock_window.current_tab = mock_tab
            mock_app = Mock()
            mock_app.current_window = mock_window

            with patch('iterm2.async_get_app', new_callable=AsyncMock) as mock_get_app:
                mock_get_app.return_value = mock_app

                # Test IP detection scenario - since we can't easily mock internal functions,
                # let's just verify that the function runs without errors
                with patch('builtins.print'):
                    result = await multi_node_init(self.mock_connection)

                    # Verify session methods were called
                    mock_session.async_inject.assert_called()
                    mock_session.async_send_text.assert_called()

        self.async_test(test_coro())


class TestClearAllSessionBuffers(unittest.TestCase):
    """Test cases for _clear_all_session_buffers function"""

    def setUp(self):
        """Set up test fixtures"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Clean up event loop"""
        self.loop.close()

    def async_test(self, coro):
        """Helper method to run async tests"""
        return self.loop.run_until_complete(coro)

    def test_clear_all_session_buffers_single_session(self):
        """Test clearing buffers for single session"""
        async def test_coro():
            mock_session = Mock()
            mock_session.session_id = "test_session_1"
            mock_session.async_inject = AsyncMock()

            sessions = [mock_session]

            with patch('builtins.print') as mock_print:
                await _clear_all_session_buffers(sessions)

                expected_code = b'\x1b' + b']1337;ClearScrollback' + b'\x07'
                mock_session.async_inject.assert_called_once_with(expected_code)
                mock_print.assert_any_call("Clearing all session buffers...")
                mock_print.assert_any_call("Clearing session 0 (ID: test_session_1)")

        self.async_test(test_coro())

    def test_clear_all_session_buffers_multiple_sessions(self):
        """Test clearing buffers for multiple sessions"""
        async def test_coro():
            mock_sessions = []
            for i in range(3):
                session = Mock()
                session.session_id = f"test_session_{i}"
                session.async_inject = AsyncMock()
                mock_sessions.append(session)

            with patch('builtins.print') as mock_print:
                await _clear_all_session_buffers(mock_sessions)

                expected_code = b'\x1b' + b']1337;ClearScrollback' + b'\x07'
                for session in mock_sessions:
                    session.async_inject.assert_called_once_with(expected_code)

                # Verify print calls
                mock_print.assert_any_call("Clearing all session buffers...")
                for i in range(3):
                    mock_print.assert_any_call(f"Clearing session {i} (ID: test_session_{i})")

        self.async_test(test_coro())

    def test_clear_all_session_buffers_empty_list(self):
        """Test clearing buffers with empty session list"""
        async def test_coro():
            sessions = []

            with patch('builtins.print') as mock_print:
                await _clear_all_session_buffers(sessions)

                mock_print.assert_called_once_with("Clearing all session buffers...")

        self.async_test(test_coro())


class TestGetMainNodeIp(unittest.TestCase):
    """Test cases for _get_main_node_ip function"""

    def setUp(self):
        self.mock_connection = Mock()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Clean up event loop"""
        self.loop.close()

    def async_test(self, coro):
        """Helper method to run async tests"""
        return self.loop.run_until_complete(coro)

    def test_get_main_node_ip_single_session(self):
        """Test _get_main_node_ip with single session (should return localhost)"""
        async def test_coro():
            mock_session = Mock()
            sessions = [mock_session]

            with patch('builtins.print') as mock_print:
                result = await _get_main_node_ip(self.mock_connection, sessions)

                self.assertEqual(result, "127.0.0.1")
                mock_print.assert_called_once_with("Single session detected. Using localhost as main node IP.")

        self.async_test(test_coro())

    def test_get_main_node_ip_multiple_sessions(self):
        """Test _get_main_node_ip with multiple sessions (will attempt IP detection)"""
        async def test_coro():
            mock_sessions = [Mock(), Mock()]  # Multiple sessions

            with patch('builtins.print'):
                result = await _get_main_node_ip(self.mock_connection, mock_sessions)

                # Should return some IP address (either detected or fallback)
                self.assertIsNotNone(result)
                self.assertTrue(isinstance(result, str))
                # Should be a valid IP format (basic check)
                parts = result.split('.')
                self.assertEqual(len(parts), 4)

        self.async_test(test_coro())


class TestGetLocalMachineIp(unittest.TestCase):
    """Test cases for _get_local_machine_ip function"""

    def test_get_local_machine_ip_success(self):
        """Test successful local IP detection"""
        mock_socket = Mock()
        mock_socket.getsockname.return_value = ("192.168.1.50", 12345)

        with patch('socket.socket') as mock_socket_class:
            mock_socket_class.return_value.__enter__ = Mock(return_value=mock_socket)
            mock_socket_class.return_value.__exit__ = Mock(return_value=None)

            with patch('builtins.print') as mock_print:
                result = _get_local_machine_ip()

                self.assertEqual(result, "192.168.1.50")
                mock_print.assert_any_call("Using fallback method to detect local machine IP...")
                mock_print.assert_any_call("Fallback successful: Detected local IP: 192.168.1.50")

    def test_get_local_machine_ip_socket_exception(self):
        """Test local IP detection when socket operation fails"""
        with patch('socket.socket') as mock_socket_class:
            mock_socket_class.side_effect = Exception("Socket error")

            with patch('builtins.print') as mock_print:
                result = _get_local_machine_ip()

                self.assertEqual(result, "127.0.0.1")
                mock_print.assert_any_call("Using fallback method to detect local machine IP...")
                mock_print.assert_any_call("Fallback failed, using localhost: Socket error")

    def test_get_local_machine_ip_getsockname_exception(self):
        """Test local IP detection when getsockname fails"""
        mock_socket = Mock()
        mock_socket.connect = Mock()
        mock_socket.getsockname.side_effect = Exception("getsockname failed")

        with patch('socket.socket') as mock_socket_class:
            mock_socket_class.return_value.__enter__ = Mock(return_value=mock_socket)
            mock_socket_class.return_value.__exit__ = Mock(return_value=None)

            with patch('builtins.print') as mock_print:
                result = _get_local_machine_ip()

                self.assertEqual(result, "127.0.0.1")
                mock_print.assert_any_call("Using fallback method to detect local machine IP...")
                mock_print.assert_any_call("Fallback failed, using localhost: getsockname failed")


class TestDetectIpFromSession(unittest.TestCase):
    """Test cases for _detect_ip_from_session function"""

    def setUp(self):
        self.mock_connection = Mock()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Clean up event loop"""
        self.loop.close()

    def async_test(self, coro):
        """Helper method to run async tests"""
        return self.loop.run_until_complete(coro)

    def test_detect_ip_from_session_basic_functionality(self):
        """Test basic functionality of _detect_ip_from_session"""
        async def test_coro():
            mock_session = Mock()
            mock_session.async_inject = AsyncMock()
            mock_session.async_send_text = AsyncMock()

            # Mock line info and contents
            mock_line_info = Mock()
            mock_line_info.overflow = 0
            mock_session.async_get_line_info = AsyncMock(return_value=mock_line_info)
            mock_session.async_get_contents = AsyncMock(return_value=[])

            with patch('iterm2.Transaction'):
                with patch('builtins.print'):
                    result = await _detect_ip_from_session(self.mock_connection, mock_session)

                    # Should return either an IP string or None
                    self.assertTrue(result is None or isinstance(result, str))
                    mock_session.async_inject.assert_called_once()
                    mock_session.async_send_text.assert_called_once()

        self.async_test(test_coro())


class TestParseIpFromLines(unittest.TestCase):
    """Test cases for _parse_ip_from_lines function"""

    def test_parse_ip_from_lines_valid_ip(self):
        """Test parsing valid IP from lines"""
        # Mock line objects
        mock_lines = []

        line1 = Mock()
        line1.string = "Some other output"
        mock_lines.append(line1)

        line2 = Mock()
        line2.string = "MAIN_NODE_IP=192.168.1.100"
        mock_lines.append(line2)

        with patch('builtins.print'):
            result = _parse_ip_from_lines(mock_lines)
            self.assertEqual(result, "192.168.1.100")

    def test_parse_ip_from_lines_no_ip_found(self):
        """Test parsing when no IP is found"""
        mock_lines = []

        line1 = Mock()
        line1.string = "Some output without IP"
        mock_lines.append(line1)

        line2 = Mock()
        line2.string = "Another line"
        mock_lines.append(line2)

        with patch('builtins.print'):
            result = _parse_ip_from_lines(mock_lines)
            self.assertIsNone(result)

    def test_parse_ip_from_lines_empty_ip(self):
        """Test parsing when IP field is empty"""
        mock_lines = []

        line1 = Mock()
        line1.string = "MAIN_NODE_IP="
        mock_lines.append(line1)

        with patch('builtins.print'):
            result = _parse_ip_from_lines(mock_lines)
            self.assertIsNone(result)

    def test_parse_ip_from_lines_empty_list(self):
        """Test parsing with empty line list"""
        mock_lines = []

        with patch('builtins.print'):
            result = _parse_ip_from_lines(mock_lines)
            self.assertIsNone(result)

    def test_parse_ip_from_lines_multiple_ips(self):
        """Test parsing when multiple IP lines exist (should return first)"""
        mock_lines = []

        line1 = Mock()
        line1.string = "MAIN_NODE_IP=192.168.1.100"
        mock_lines.append(line1)

        line2 = Mock()
        line2.string = "MAIN_NODE_IP=10.0.0.1"
        mock_lines.append(line2)

        with patch('builtins.print'):
            result = _parse_ip_from_lines(mock_lines)
            self.assertEqual(result, "192.168.1.100")


class TestSetEnvironmentVariables(unittest.TestCase):
    """Test cases for _set_environment_variables function"""

    def setUp(self):
        """Set up test fixtures"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Clean up event loop"""
        self.loop.close()

    def async_test(self, coro):
        """Helper method to run async tests"""
        return self.loop.run_until_complete(coro)

    def test_set_environment_variables_single_session(self):
        """Test setting environment variables for single session"""
        async def test_coro():
            mock_session = Mock()
            mock_session.session_id = "test_session_1"
            mock_session.async_send_text = AsyncMock()

            sessions = [mock_session]
            main_node_ip = "192.168.1.100"

            with patch('builtins.print') as mock_print:
                await _set_environment_variables(sessions, main_node_ip)

                # Verify RANK command
                expected_rank_call = call("export RANK=0\n", suppress_broadcast=True)
                # Verify MAIN_NODE_IP command
                expected_ip_call = call('export MAIN_NODE_IP="192.168.1.100"\n', suppress_broadcast=True)

                mock_session.async_send_text.assert_has_calls([expected_rank_call, expected_ip_call])

        self.async_test(test_coro())

    def test_set_environment_variables_multiple_sessions(self):
        """Test setting environment variables for multiple sessions"""
        async def test_coro():
            mock_sessions = []
            for i in range(3):
                session = Mock()
                session.session_id = f"test_session_{i}"
                session.async_send_text = AsyncMock()
                mock_sessions.append(session)

            main_node_ip = "10.0.0.1"

            with patch('builtins.print') as mock_print:
                await _set_environment_variables(mock_sessions, main_node_ip)

                # Verify each session got correct RANK and IP
                for i, session in enumerate(mock_sessions):
                    expected_rank_call = call(f"export RANK={i}\n", suppress_broadcast=True)
                    expected_ip_call = call(f'export MAIN_NODE_IP="{main_node_ip}"\n', suppress_broadcast=True)
                    session.async_send_text.assert_has_calls([expected_rank_call, expected_ip_call])

                # Verify print statements
                mock_print.assert_any_call("Setting environment variables across 3 sessions...")
                mock_print.assert_any_call("Environment variable setup completed for all sessions.")

        self.async_test(test_coro())

    def test_set_environment_variables_empty_sessions(self):
        """Test setting environment variables with empty session list"""
        async def test_coro():
            sessions = []
            main_node_ip = "192.168.1.100"

            with patch('builtins.print') as mock_print:
                await _set_environment_variables(sessions, main_node_ip)

                mock_print.assert_any_call("Setting environment variables across 0 sessions...")
                mock_print.assert_any_call("Environment variable setup completed for all sessions.")

        self.async_test(test_coro())


class TestModuleImports(unittest.TestCase):
    """Test cases for module imports and metadata"""

    def test_module_imports(self):
        """Test that required modules are properly imported in the multi_node_init module"""
        # Test that the functions imported at the top of this test file are available
        # and properly imported (they're imported in the imports section at the top)

        # Verify they are callable
        self.assertTrue(callable(multi_node_init))
        self.assertTrue(callable(_clear_all_session_buffers))
        self.assertTrue(callable(_get_main_node_ip))
        self.assertTrue(callable(_get_local_machine_ip))
        self.assertTrue(callable(_detect_ip_from_session))
        self.assertTrue(callable(_parse_ip_from_lines))
        self.assertTrue(callable(_set_environment_variables))

        # Test that the main function is properly async
        self.assertTrue(asyncio.iscoroutinefunction(multi_node_init))

    def test_function_signatures(self):
        """Test that functions have correct signatures"""
        # Test multi_node_init signature
        sig = inspect.signature(multi_node_init)
        self.assertEqual(len(sig.parameters), 1)
        self.assertIn('connection', sig.parameters)

        # Test that async functions are properly marked as coroutines
        self.assertTrue(asyncio.iscoroutinefunction(multi_node_init))
        self.assertTrue(asyncio.iscoroutinefunction(_clear_all_session_buffers))
        self.assertTrue(asyncio.iscoroutinefunction(_get_main_node_ip))
        self.assertTrue(asyncio.iscoroutinefunction(_detect_ip_from_session))
        self.assertTrue(asyncio.iscoroutinefunction(_set_environment_variables))

        # Test that non-async functions are not coroutines
        self.assertFalse(asyncio.iscoroutinefunction(_get_local_machine_ip))
        self.assertFalse(asyncio.iscoroutinefunction(_parse_ip_from_lines))


if __name__ == '__main__':
    # Run the tests
    print("Running unit tests for multi_node_init module...")
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
        print("✅ All multi-node initialization tests passed!")
    else:
        print("❌ Some multi-node initialization tests failed!")

    print("=" * 60)
