"""Message handlers — forwards owner messages to agent-core via HTTP and echoes
the response."""

import logging

import httpx
from aiogram import Router, types

from .auth import OwnerFilter
from .config import config
from .logger import get_logger

logger = get_logger(__name__)

router = Router()
AGENT_CORE_URL = config.AGENT_CORE_URL


@router.message(OwnerFilter())
async def handle_owner_message(message: types.Message) -> None:
    """Forward the owner's message to agent-core and relay the response back."""

    await message.answer(f"bot is working {message.from_user.id} and {message.chat.id}.")

    if not message.text:
        await message.answer("I only handle text messages for now.")
        return

    if not AGENT_CORE_URL:
        logger.info("Standalone mode: echoing message from owner")
        reply_text = f"Received: {message.text}"
        for i in range(0, len(reply_text), 4096):
            await message.answer(reply_text[i : i + 4096])
        return

    payload = {
        "telegram_user_id": message.from_user.id,
        "chat_id": message.chat.id,
        "message_id": message.message_id,
        "text": message.text,
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{AGENT_CORE_URL}/message", json=payload)
            resp.raise_for_status()
            data = resp.json()

        reply_text = data.get("reply", "✅ Done (no response body).")
        # Telegram message limit is 4096 chars
        for i in range(0, len(reply_text), 4096):
            await message.answer(reply_text[i : i + 4096])

    except httpx.HTTPStatusError as exc:
        logger.error("agent-core returned %s: %s", exc.response.status_code, exc.response.text)
        await message.answer(f"⚠️ Agent error ({exc.response.status_code})")
    except Exception as exc:
        logger.exception("Failed to reach agent-core")
        await message.answer(f"⚠️ Could not reach agent-core: {exc}")