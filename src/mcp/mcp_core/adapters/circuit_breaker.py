"""Circuit breaker pattern for MCP tool adapters."""

import asyncio
import time
from enum import Enum
from typing import Any, Callable, Dict, TypeVar, cast

from ..errors import CircuitBreakerError
from ..logger import logger

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation, requests pass through
    OPEN = "open"  # Failing, requests are blocked
    HALF_OPEN = "half-open"  # Testing if service is recovered


class CircuitBreaker:
    """Circuit breaker for protecting adapter calls."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 1,
    ):
        """Initialize circuit breaker.

        Args:
            name: Circuit breaker name
            failure_threshold: Number of failures before opening
            recovery_timeout: Seconds to wait before trying recovery
            half_open_max_calls: Max calls allowed in half-open state
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.half_open_calls = 0

        logger.info(
            f"Circuit breaker {name} initialized",
            circuit=name,
            state=self.state.value,
            threshold=failure_threshold,
        )

    async def execute(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute a function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Function positional arguments
            **kwargs: Function keyword arguments

        Returns:
            T: Function result

        Raises:
            CircuitBreakerError: If circuit is open or function fails
        """
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                # Try recovery
                logger.info(
                    f"Circuit {self.name} attempting recovery",
                    circuit=self.name,
                    prev_state=self.state.value,
                    new_state=CircuitState.HALF_OPEN.value,
                )
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
            else:
                # Circuit still open
                raise CircuitBreakerError(
                    f"Circuit {self.name} is open",
                    details={
                        "circuit": self.name,
                        "state": self.state.value,
                        "retry_after": self.recovery_timeout
                        - (time.time() - self.last_failure_time),
                    },
                )

        if (
            self.state == CircuitState.HALF_OPEN
            and self.half_open_calls >= self.half_open_max_calls
        ):
            # Too many calls in half-open state
            raise CircuitBreakerError(
                f"Circuit {self.name} is half-open and at capacity",
                details={
                    "circuit": self.name,
                    "state": self.state.value,
                    "max_calls": self.half_open_max_calls,
                },
            )

        # Increment half-open call counter if needed
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1

        try:
            # Execute the function
            result = (
                await func(*args, **kwargs)
                if asyncio.iscoroutinefunction(func)
                else func(*args, **kwargs)
            )

            # Success handling
            if self.state == CircuitState.HALF_OPEN:
                # Recovery successful
                logger.info(
                    f"Circuit {self.name} recovered",
                    circuit=self.name,
                    prev_state=self.state.value,
                    new_state=CircuitState.CLOSED.value,
                )
                self.state = CircuitState.CLOSED
                self.failure_count = 0

            return cast(T, result)
        except Exception as e:
            # Failure handling
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == CircuitState.HALF_OPEN or (
                self.state == CircuitState.CLOSED
                and self.failure_count >= self.failure_threshold
            ):
                # Open the circuit
                prev_state = self.state
                self.state = CircuitState.OPEN
                logger.warning(
                    f"Circuit {self.name} opened",
                    circuit=self.name,
                    prev_state=prev_state.value,
                    new_state=self.state.value,
                    failures=self.failure_count,
                    recovery_timeout=self.recovery_timeout,
                )

            # Re-raise the exception
            raise CircuitBreakerError(
                f"Circuit {self.name} operation failed: {str(e)}",
                details={
                    "circuit": self.name,
                    "state": self.state.value,
                    "failure_count": self.failure_count,
                    "original_error": str(e),
                },
            ) from e

    def reset(self) -> None:
        """Reset the circuit breaker to closed state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.half_open_calls = 0

        logger.info(
            f"Circuit {self.name} reset", circuit=self.name, state=self.state.value
        )

    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state information.

        Returns:
            Dict[str, Any]: State information
        """
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
            "half_open_calls": self.half_open_calls,
            "half_open_max_calls": self.half_open_max_calls,
        }
