"""Bot-gateway entry point — Telegram long-polling with owner-only auth."""

import asyncio
import os
from pathlib import Path
import sys

from aiogram import Bot, Dispatcher
from watchfiles import watch

from src.config import config
from src.logger import setup_logging, get_logger
from src.process_manager import ProcessManager
from src.handlers import router


class BotApplication:
    """Main bot application class managing lifecycle and dependencies."""

    def __init__(self):
        self.logger = setup_logging(config.LOG_LEVEL)
        self.process_manager = ProcessManager(config.PID_FILE)
        self.bot: Bot = None
        self.dispatcher: Dispatcher = None

    def initialize(self) -> None:
        """Initialize bot configuration and validate settings."""
        try:
            config.validate()
            self.logger.info("Configuration validated successfully")
        except ValueError as e:
            self.logger.error(f"Configuration error: {e}")
            sys.exit(1)

    def setup_bot(self) -> None:
        """Setup bot and dispatcher with handlers."""
        self.bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
        self.dispatcher = Dispatcher()
        self.dispatcher.include_router(router)
        self.logger.info("Bot and dispatcher initialized")

    async def run(self) -> None:
        """Main bot execution loop."""
        self.initialize()
        self.process_manager.check_single_instance()
        self.setup_bot()

        self.logger.info("Starting bot-gateway long-polling...")
        try:
            await self.dispatcher.start_polling(self.bot)
        except Exception as e:
            self.logger.error(f"Bot polling error: {e}", exc_info=True)
            raise
        finally:
            self.process_manager.cleanup()

    def start(self) -> None:
        """Start the bot application."""
        try:
            asyncio.run(self.run())
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)
            sys.exit(1)


def run_with_reload() -> None:
    """Run the bot with auto-reload on file changes."""

    logger = setup_logging(config.LOG_LEVEL)
    src_path = Path(__file__).parent

    logger.info("Starting bot with auto-reload enabled...")
    logger.info(f"Watching directory: {src_path}")

    for changes in watch(src_path, recursive=True):
        logger.info(
            f"Detected changes: {len(changes)} file(s) modified, restarting..."
        )

        # Restart the current process
        os.execv(sys.executable, [sys.executable] + sys.argv)


def main() -> None:
    """Application entry point."""

    # Check if auto-reload is enabled via environment variable
    if os.environ.get("AUTO_RELOAD", "false").lower() == "true":
        run_with_reload()
        return

    app = BotApplication()
    app.start()


if __name__ == "__main__":
    main()