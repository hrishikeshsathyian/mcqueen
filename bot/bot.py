from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
import os

token: str = os.environ["TELEGRAM_BOT_TOKEN"]
chat_id: str = os.environ["TELEGRAM_CHAT_ID"]

bot = Bot(
    token=token
    )

async def send_message(): 
    try:    
        return await bot.send_message(
            chat_id=chat_id,
            text="Hello World",
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except TelegramError as err:
        print(f"Error occured: {err.message}") 



