import logging

from db.jobs import get_seen_global_ids
from ats_scrapers.models import Job
from pipeline.sources.registry import SOURCES

logger = logging.getLogger(__name__)

def scrape() -> tuple[list[Job],list[Job]]:
    seen_global_ids = get_seen_global_ids()
    jobs: list[Job] = []
    dropped_jobs: list[Job] = []

    for source in SOURCES:
        logger.info(f"Scraping source: {source.name}")
        scraped, dropped = source.scrape(seen_global_ids=seen_global_ids)
        logger.info(f"[{source.name}] found {len(scraped)} new job(s)")
        logger.info(f"[{source.name}] dropped {len(dropped)} job(s) for being deemed as non technical")
        jobs.extend(scraped)
        dropped_jobs.extend(dropped)

    logger.info(f"Found {len(jobs)} new job(s) in total across all scrapers")
    return (jobs, dropped_jobs)
