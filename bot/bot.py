import asyncio
import datetime
import html
import logging
import os

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import RetryAfter, TelegramError, TimedOut

from ats_scrapers.models import Job

logger = logging.getLogger(__name__)

token: str = os.environ["TELEGRAM_BOT_TOKEN"]
chat_id: str = os.environ["TELEGRAM_CHAT_ID"]

bot = Bot(token=token)

MAX_RETRIES = 5


async def send_message(
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
):
    for attempt in range(MAX_RETRIES):
        try:
            return await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                reply_markup=reply_markup,
            )

        except RetryAfter as e:
            retry_after = e.retry_after
            if isinstance(retry_after, datetime.timedelta):
                retry_after = retry_after.total_seconds()
            print(f"Telegram flood control hit. Retrying in {retry_after}s...")
            await asyncio.sleep(retry_after + 0.5)

        except TimedOut:
            print("Telegram timeout occurred. Retrying...")
            await asyncio.sleep(1.0)

        except TelegramError as e:
            print(f"Telegram error occurred: {e}")
            return None

    print(f"Giving up sending message after {MAX_RETRIES} retries.")
    return None


async def send_job(job: Job, use_apply_url: bool = False):
    if use_apply_url:
        url = str(job.apply_url)
    else:
        url = str(job.url)

    text = (
        "🚨 <b>Internship Alert</b>\n\n"
        f"💼 <b>{html.escape(job.title)}</b>\n"
        f"🏢 {html.escape(job.company)}"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Apply Now 🚀",
                    url=url,
                )
            ]
        ]
    )

    return await send_message(
        text=text,
        reply_markup=keyboard,
    )
