import asyncio
import html
import logging
import os

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import TelegramError, TimedOut

from ats_scrapers.models import Job

logger = logging.getLogger(__name__)

token: str = os.environ["TELEGRAM_BOT_TOKEN"]
chat_id: str = os.environ["TELEGRAM_CHAT_ID"]

bot = Bot(token=token)


async def send_message(
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
):
    try:
        return await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
        )

    except TimedOut:
        logger.warning("Telegram timeout occurred. Retrying...")
        await asyncio.sleep(1.0)

        return await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
        )

    except TelegramError as e:
        logger.error(f"Telegram error occurred: {e}", exc_info=True)


async def send_job(job: Job, use_apply_url: bool = False):
    if use_apply_url:
        url = str(job.apply_url)
    else:
        url = str(job.url)

    text = (
        "🚨 <b>New Internship Alert</b>\n\n"
        f"💼 <b>{html.escape(job.title)}</b>\n"
        f"🏢 {html.escape(job.company)}"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="View Listing ↗️",
                    url=url,
                )
            ]
        ]
    )

    return await send_message(
        text=text,
        reply_markup=keyboard,
    )
