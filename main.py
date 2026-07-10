from dotenv import load_dotenv
load_dotenv()
from bot import bot
from pipeline.scripts.scrape import scrape
import asyncio
from jobhive.models import Job

async def run():
    filtered_jobs: list[Job] = scrape()
    for job in filtered_jobs: 
        await bot.send_job(job=job)

if __name__ == "__main__":
    asyncio.run(run()) 
