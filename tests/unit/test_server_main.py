"""Unit tests for the main server module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from chemist_server.server import main, parse_args, run_services, start_core_service

pytestmark = pytest.mark.asyncio


class TestParseArgs:
    """Tests for the argument parser function."""

    def test_default_args(self):
        """Test parsing with no arguments returns defaults."""
        # Mock sys.argv with no additional args
        with patch("sys.argv", ["server.py"]):
            args = parse_args()
            # All should be None by default
            assert args.transport is None
            assert args.host is None
            assert args.port is None
            assert args.log_level is None
            assert args.component is None

    def test_transport_arg(self):
        """Test parsing transport argument."""
        with patch("sys.argv", ["server.py", "--transport", "stdio"]):
            args = parse_args()
            assert args.transport == "stdio"

    def test_host_arg(self):
        """Test parsing host argument."""
        with patch("sys.argv", ["server.py", "--host", "localhost"]):
            args = parse_args()
            assert args.host == "localhost"

    def test_port_arg(self):
        """Test parsing port argument."""
        with patch("sys.argv", ["server.py", "--port", "8000"]):
            args = parse_args()
            assert args.port == 8000

    def test_log_level_arg(self):
        """Test parsing log level argument."""
        with patch("sys.argv", ["server.py", "--log-level", "DEBUG"]):
            args = parse_args()
            assert args.log_level == "DEBUG"

    def test_component_arg(self):
        """Test parsing component argument."""
        with patch("sys.argv", ["server.py", "--component", "core"]):
            args = parse_args()
            assert args.component == "core"


class TestStartCoreService:
    """Tests for the start_core_service function."""

    async def test_start_core_service_stdio(self, function_default_config):
        """Test starting core service with stdio transport."""
        # Configure mock config
        config = function_default_config
        config.transport = "stdio"

        # Mock the app
        mock_app = MagicMock()
        mock_app.run_stdio_async = AsyncMock()

        with patch(
            "chemist_server.mcp_core.app.get_fastmcp_app", return_value=mock_app
        ):
            await start_core_service(config)
            # Verify the correct transport was called
            mock_app.run_stdio_async.assert_called_once()

    async def test_start_core_service_sse(self, function_default_config):
        """Test starting core service with SSE transport."""
        # Configure mock config
        config = function_default_config
        config.transport = "sse"
        config.get_core_host = MagicMock(return_value="localhost")
        config.get_core_port = MagicMock(return_value=8000)

        # Mock the app
        mock_app = MagicMock()
        mock_app.run_sse_async = AsyncMock()

        with patch(
            "chemist_server.mcp_core.app.get_fastmcp_app", return_value=mock_app
        ):
            await start_core_service(config)
            # Verify the correct transport was called
            mock_app.run_sse_async.assert_called_once()

    async def test_start_core_service_unsupported(self, function_default_config):
        """Test starting core service with unsupported transport."""
        # Configure mock config
        config = function_default_config
        config.transport = "unsupported"

        # Mock the app
        mock_app = MagicMock()

        with patch(
            "chemist_server.mcp_core.app.get_fastmcp_app", return_value=mock_app
        ):
            with pytest.raises(ValueError, match="Unsupported transport"):
                await start_core_service(config)


class TestRunServices:
    """Tests for the run_services function."""

    async def test_run_services_all(self, function_default_config):
        """Test running all services."""
        # Configure mock config
        config = function_default_config
        config.components = "all"

        # Mock the task group
        mock_tg = MagicMock()
        mock_tg.__aenter__ = AsyncMock(return_value=mock_tg)
        mock_tg.__aexit__ = AsyncMock()
        mock_tg.start_soon = MagicMock()

        with patch("anyio.create_task_group", return_value=mock_tg):
            with patch("chemist_server.server.start_core_service") as mock_core:
                await run_services(config)
                # Verify core service was started
                mock_tg.start_soon.assert_called_once_with(mock_core, config)

    async def test_run_services_core(self, function_default_config):
        """Test running core service specifically."""
        # Configure mock config
        config = function_default_config
        config.components = "core"

        # Mock the task group
        mock_tg = MagicMock()
        mock_tg.__aenter__ = AsyncMock(return_value=mock_tg)
        mock_tg.__aexit__ = AsyncMock()
        mock_tg.start_soon = MagicMock()

        with patch("anyio.create_task_group", return_value=mock_tg):
            with patch("chemist_server.server.start_core_service") as mock_core:
                await run_services(config)
                # Verify core service was started
                mock_tg.start_soon.assert_called_once_with(mock_core, config)


class TestMainFunction:
    """Tests for the main entry point function."""

    def test_main_success(self):
        """Test successful execution of main function."""
        with (
            patch("argparse.ArgumentParser.parse_args") as mock_parse_args,
            patch("chemist_server.config.load_and_get_config") as mock_load_config,
            patch(
                "chemist_server.mcp_core.logger.logger.configure_logging"
            ) as mock_configure_logging,
            patch("anyio.run") as mock_run,
        ):
            # Configure mocks
            mock_parse_args.return_value = MagicMock(
                transport=None, host=None, port=None, log_level=None, component=None
            )
            mock_config = MagicMock()
            mock_config.components = "all"
            mock_config.transport = "stdio"
            mock_config.model_dump.return_value = {}
            mock_load_config.return_value = mock_config

            # Run the function
            result = main()

            # Verify successful execution
            assert result == 0
            mock_parse_args.assert_called_once()
            mock_load_config.assert_called_once()
            mock_configure_logging.assert_called_once_with(mock_config)
            mock_run.assert_called_once()

    def test_main_keyboard_interrupt(self):
        """Test main function with KeyboardInterrupt."""
        with (
            patch("argparse.ArgumentParser.parse_args") as mock_parse_args,
            patch("chemist_server.config.load_and_get_config") as mock_load_config,
            patch(
                "chemist_server.mcp_core.logger.logger.configure_logging"
            ) as mock_configure_logging,
            patch("anyio.run", side_effect=KeyboardInterrupt) as mock_run,
        ):
            # Configure mocks
            mock_parse_args.return_value = MagicMock(
                transport=None, host=None, port=None, log_level=None, component=None
            )
            mock_config = MagicMock()
            mock_config.components = "all"
            mock_config.transport = "stdio"
            mock_config.model_dump.return_value = {}
            mock_load_config.return_value = mock_config

            # Run the function
            result = main()

            # Verify successful execution with clean exit
            assert result == 0
            mock_run.assert_called_once()

    def test_main_exception(self):
        """Test main function with exception."""
        with (
            patch("argparse.ArgumentParser.parse_args") as mock_parse_args,
            patch("chemist_server.config.load_and_get_config") as mock_load_config,
            patch(
                "chemist_server.mcp_core.logger.logger.configure_logging"
            ) as mock_configure_logging,
            patch("anyio.run", side_effect=RuntimeError("Test error")) as mock_run,
        ):
            # Configure mocks
            mock_parse_args.return_value = MagicMock(
                transport=None, host=None, port=None, log_level=None, component=None
            )
            mock_config = MagicMock()
            mock_config.components = "all"
            mock_config.transport = "stdio"
            mock_config.model_dump.return_value = {}
            mock_load_config.return_value = mock_config

            # Run the function
            result = main()

            # Verify error exit code
            assert result == 1
            mock_run.assert_called_once()
