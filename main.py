from dotenv import load_dotenv
load_dotenv()
from bot import bot
from db.jobs import update_seen_jobs
from pipeline.scripts.scrape import scrape
import asyncio
from jobhive.models import Job

async def run():
    # scrape and find unique jobs
    filtered_jobs: list[Job] = scrape()
    # update database
    update_seen_jobs(filtered_jobs)
    # send new updates to telegram
    for job in filtered_jobs: 
        await bot.send_job(job=job)

async def populate_db():
    # scrape and find unique jobs
    filtered_jobs: list[Job] = scrape()
    # update database
    update_seen_jobs(filtered_jobs)

if __name__ == "__main__":
    asyncio.run(run()) 
