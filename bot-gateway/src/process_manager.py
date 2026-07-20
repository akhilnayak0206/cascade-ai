"""Process management module for single instance enforcement and cleanup."""

import atexit
import os
import sys
import signal
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class ProcessManager:
    """Manages process lifecycle including single instance enforcement."""

    def __init__(self, pid_file: str):
        self.pid_file = pid_file
        atexit.register(self.cleanup)

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self._signal_handler)

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals by cleaning up PID file."""
        logger.info(f"Received signal {signum}, cleaning up...")
        self.cleanup()
        sys.exit(0)

    def check_single_instance(self) -> None:
        """Ensure only one instance is running using PID file."""
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, "r") as f:
                    pid = int(f.read().strip())

                # Check if process is still running - kill it so we can replace it
                # (e.g. watchfiles reload)
                os.kill(pid, 0)

                logger.info(f"Killing previous instance (PID {pid}) for reload...")
                os.kill(pid, signal.SIGTERM)

                # Give it a moment to terminate
                for _ in range(20):
                    time.sleep(0.1)
                    try:
                        os.kill(pid, 0)
                    except (ProcessLookupError, OSError):
                        break
                else:
                    # Force kill if still alive
                    logger.warning(
                        f"Force-killing previous instance (PID {pid})"
                    )
                    os.kill(pid, signal.SIGKILL)

                self.cleanup()

            except (ProcessLookupError, ValueError, OSError):
                # Process not running, or invalid PID, clean up stale file
                logger.info("Removing stale PID file")
                self.cleanup()

        # Write current PID
        self._write_pid()
        
    def _write_pid(self) -> None:
        """Write current process ID to PID file."""
        with open(self.pid_file, "w") as f:
            f.write(str(os.getpid()))
        logger.debug(f"PID file created: {self.pid_file}")

    def cleanup(self) -> None:
        """Clean up PID file on exit."""
        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)
            logger.debug(f"PID file removed: {self.pid_file}")

    def get_pid(self) -> Optional[int]:
        """Get the PID from the PID file if it exists."""
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, "r") as f:
                    return int(f.read().strip())
            except (ValueError, OSError):
                return None
        return None