from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError, TimedOut
import os
from jobhive.models import Job
import html
import asyncio

token: str = os.environ["TELEGRAM_BOT_TOKEN"]
chat_id: str = os.environ["TELEGRAM_CHAT_ID"]

bot = Bot(
    token=token
    )

async def send_message(text: str): 
    try:    
        return await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except TimedOut: 
        print(f"Telegram timeout occurred")
        await asyncio.sleep(1.0)
    except TelegramError as e:
        print(f"Error occured: {e.message}") 

async def send_job(job: Job):
    text = (
        f"<b>{html.escape(job.title)}</b>\n"
        f"🏢 {html.escape(job.company)}\n"
        f'👉 <a href="{html.escape(str(job.apply_url))}">View Listing</a>'
    )
    return await send_message(text)
