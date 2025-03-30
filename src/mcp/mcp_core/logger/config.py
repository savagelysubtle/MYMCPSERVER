"""DEPRECATED: This module is deprecated and will be removed in a future version.

Configuration has been centralized at src/config.py.
Please use LoggingConfig from src/config.py instead of LogConfig from this module.
"""

import warnings

warnings.warn(
    "mcp_core.logger.config is deprecated. Use LoggingConfig from 'src/config.py' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Keeping a stub reference to not break existing imports immediately
from src.config import LoggingConfig  # type: ignore

# Backwards compatibility alias
LogConfig = LoggingConfig

# No instance creation - redirect users to central config
# log_config = LogConfig()
