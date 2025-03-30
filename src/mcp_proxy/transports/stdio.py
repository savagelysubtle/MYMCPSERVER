"""Standard I/O transport for MCP Proxy.

This module implements the StdioHandler which is responsible for spawning
and communicating with the Core Layer process.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, TextIO

from .base_transport import BaseTransport

# Configure logging
logger = logging.getLogger(__name__)


class StdioHandler(BaseTransport):
    """Handles stdio communication with processes.

    This transport is designed for subprocess communication where
    the client is a child process communicating via stdin/stdout.
    """

    def __init__(
        self,
        command: str | None = None,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        input_stream: TextIO | None = None,
        output_stream: TextIO | None = None,
    ):
        """Initialize stdio handler.

        Args:
            command: Command to execute (if None, use existing streams)
            args: Command arguments
            env: Environment variables
            input_stream: Input stream (defaults to sys.stdin if command is None)
            output_stream: Output stream (defaults to sys.stdout if command is None)
        """
        self.command = command
        self.args = args or []
        self.env = env or {}
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.process: asyncio.subprocess.Process | None = None
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self.reader_task = None
        self.writer_task = None
        self.process_id = None
        self.message_router = None

    async def initialize(self) -> None:
        """Initialize the transport."""
        self.running = True

        if self.command:
            # Spawn process
            await self._spawn_process()
        else:
            # Use existing streams
            self.input_stream = self.input_stream or sys.stdin
            self.output_stream = self.output_stream or sys.stdout

        # Start reader and writer tasks
        self.reader_task = asyncio.create_task(self._reader())
        self.writer_task = asyncio.create_task(self._writer())

        logger.info("StdioHandler initialized")

    async def shutdown(self) -> None:
        """Shutdown the transport."""
        self.running = False

        # Cancel tasks
        if self.reader_task:
            self.reader_task.cancel()

        if self.writer_task:
            await self.message_queue.put(None)  # Signal writer to exit
            await self.writer_task

        # Terminate process if we spawned it
        if self.process:
            try:
                self.process.terminate()
                await self.process.wait()
            except ProcessLookupError:
                pass  # Process already terminated

        logger.info("StdioHandler shutdown")

    async def _spawn_process(self) -> None:
        """Spawn a new process."""
        if not self.command:
            logger.error("Cannot spawn process: no command specified")
            return

        process_env = os.environ.copy()
        process_env.update(self.env)

        logger.info(f"Spawning process: {self.command} {' '.join(self.args)}")

        self.process = await asyncio.create_subprocess_exec(
            self.command,
            *self.args,
            env=process_env,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        self.process_id = str(self.process.pid)
        logger.info(f"Process spawned with PID: {self.process_id}")

        # Start stderr reader
        asyncio.create_task(self._read_stderr())

    async def _read_stderr(self) -> None:
        """Read and log from process stderr."""
        if not self.process or not self.process.stderr:
            return

        while self.running:
            try:
                line = await self.process.stderr.readline()
                if not line:
                    break

                stderr_line = line.decode().strip()
                logger.warning(f"Process stderr: {stderr_line}")

                # Route stderr message if router is available
                if self.message_router:
                    await self.message_router.route_message(
                        {
                            "type": "process_stderr",
                            "process_id": self.process_id,
                            "data": stderr_line,
                        }
                    )
            except Exception as e:
                logger.error(f"Error reading stderr: {e}")
                if not self.running:
                    break

    async def _reader(self) -> None:
        """Read messages from input stream or process stdout."""
        try:
            if self.process and self.process.stdout:
                # Read from process stdout
                while self.running:
                    line = await self.process.stdout.readline()
                    if not line:
                        logger.info("Process stdout closed")
                        break

                    await self._process_input_line(line)
            else:
                # Read from input_stream
                if not self.input_stream:
                    logger.error("Cannot read: no input stream available")
                    return

                loop = asyncio.get_event_loop()
                while self.running:
                    line = await loop.run_in_executor(None, self.input_stream.readline)
                    if not line:
                        logger.info("Input stream closed")
                        break

                    await self._process_input_line(line.encode())
        except Exception as e:
            logger.error(f"Reader error: {e}")
        finally:
            if self.running:
                logger.warning("Reader task exited unexpectedly")

    async def _process_input_line(self, line: bytes) -> None:
        """Process an input line."""
        try:
            # Parse JSON message
            message = json.loads(line.decode().strip())

            # Route message if router is available
            if self.message_router:
                await self.message_router.route_message(message)

            # Also handle message locally
            await self.message_queue.put(message)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON: {line.decode().strip()}")
        except Exception as e:
            logger.error(f"Error processing input: {e}")

    async def _writer(self) -> None:
        """Write messages to output stream or process stdin."""
        try:
            while self.running:
                # Get message from queue
                message = await self.message_queue.get()

                if message is None:
                    # Exit signal
                    break

                # Serialize message to JSON
                json_str = json.dumps(message)

                if self.process and self.process.stdin:
                    # Write to process stdin
                    self.process.stdin.write(f"{json_str}\n".encode())
                    await self.process.stdin.drain()
                elif self.output_stream:
                    # Write to output_stream
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(
                        None, lambda: self.output_stream.write(json_str + "\n")
                    )
                    await loop.run_in_executor(None, self.output_stream.flush)
                else:
                    logger.error("Cannot write: no output stream available")

                self.message_queue.task_done()
        except Exception as e:
            logger.error(f"Writer error: {e}")
        finally:
            if self.running:
                logger.warning("Writer task exited unexpectedly")

    async def send_message(
        self, message: dict[str, Any], client_id: str | None = None
    ) -> None:
        """Send a message to the process.

        Args:
            message: Message to send
            client_id: Target client ID (ignored for stdio)
        """
        await self.message_queue.put(message)

    async def receive_message(
        self, client_id: str, timeout: float | None = None
    ) -> dict[str, Any] | None:
        """Receive a message from the process.

        Args:
            client_id: Client ID (ignored for stdio)
            timeout: Receive timeout in seconds

        Returns:
            Optional[Dict[str, Any]]: Received message or None if timeout
        """
        # Not implemented for stdio transport
        # Messages are handled by the reader task
        return None

    def set_message_router(self, router) -> None:
        """Set the message router for this transport.

        Args:
            router: The message router instance
        """
        self.message_router = router
