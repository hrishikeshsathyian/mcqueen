from dotenv import load_dotenv

load_dotenv()
from logging_config import setup_logging

setup_logging()

import logging
from bot import bot
from db.jobs import upsert_seen_jobs, upsert_dropped_jobs
from pipeline.scripts.scrape import scrape
import asyncio
from ats_scrapers.models import Job, ATSType

logger = logging.getLogger(__name__)


async def run():
    jobs, dropped = scrape()
    logger.info(f"Found {len(jobs)} new job(s)")

    # update db
    if len(jobs) > 0:
        upsert_seen_jobs(jobs)

    if len(dropped) > 0:
        upsert_dropped_jobs(dropped) 

    # send new updates to telegram
    for job in jobs:
        if job.ats_type == ATSType.CUSTOM:
            await bot.send_job(job=job, use_apply_url=True)
        else:
            await bot.send_job(job=job)
        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(run())
