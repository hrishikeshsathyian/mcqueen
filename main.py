from dotenv import load_dotenv
load_dotenv()
# from bot import bot
from pipeline.scripts.run import scrape
import asyncio

async def run():
    scrape()

if __name__ == "__main__":
    asyncio.run(run()) 
