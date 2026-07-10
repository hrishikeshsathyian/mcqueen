from dotenv import load_dotenv
load_dotenv()
from bot import bot
import asyncio

async def run(): 
    await bot.send_message()

if __name__ == "__main__":
    asyncio.run(run()) 
