from dotenv import load_dotenv

load_dotenv()
from bot import bot
from db.jobs import update_seen_jobs
from pipeline.scripts.scrape import scrape
import asyncio
from ats_scrapers.models import Job, ATSType


async def run():
    # scrape and find unique jobs
    filtered_jobs: list[Job] = scrape()
    # update database
    if len(filtered_jobs) > 0:
        update_seen_jobs(filtered_jobs)
    # send new updates to telegram
    for job in filtered_jobs:
        if job.ats_type == ATSType.CUSTOM:
            await bot.send_job(job=job, use_apply_url=True)
        else:
            await bot.send_job(job=job)
        await asyncio.sleep(3)


async def populate_db():
    # scrape and find unique jobs
    filtered_jobs: list[Job] = scrape()
    # update database
    update_seen_jobs(filtered_jobs)


if __name__ == "__main__":
    asyncio.run(run())
