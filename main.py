from dotenv import load_dotenv

load_dotenv()
from logging_config import setup_logging

setup_logging()

import logging
from bot import bot
from db.jobs import update_seen_jobs
from pipeline.scripts.scrape import scrape
import asyncio
from ats_scrapers.models import Job, ATSType
import time

logger = logging.getLogger(__name__)


async def run():
    # scrape and find unique jobs
    jobs: list[Job] = scrape()
    logger.info(f"Found {len(jobs)} new job(s)")
    # update database
    if len(jobs) > 0:
        update_seen_jobs(jobs)
    # send new updates to telegram
    for job in jobs:
        if job.ats_type == ATSType.CUSTOM:
            await bot.send_job(job=job, use_apply_url=True)
        else:
            await bot.send_job(job=job)
        time.sleep(2)


async def populate_db():
    # scrape and find unique jobs
    filtered_jobs: list[Job] = scrape()
    logger.info(f"Populating database with {len(filtered_jobs)} job(s)")
    # update database
    update_seen_jobs(filtered_jobs)


if __name__ == "__main__":
    asyncio.run(run())
