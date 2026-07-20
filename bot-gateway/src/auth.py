"""Owner-only authentication filter for Telegram messages."""

import logging

from aiogram import types
from aiogram.filters import BaseFilter

from .config import config
from .logger import get_logger

logger = get_logger(__name__)

OWNER_TELEGRAM_ID: int = config.OWNER_TELEGRAM_ID


class OwnerFilter(BaseFilter):
    """Aiogram filter that passes only messages from the configured owner."""

    async def __call__(self, message: types.Message) -> bool:
        is_owner = message.from_user is not None and message.from_user.username == OWNER_TELEGRAM_ID
        if not is_owner:
            logger.debug("Ignoring message from user %s (not owner)", message.from_user)
        return is_owner