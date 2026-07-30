import logging

from db.jobs import get_seen_global_ids
from ats_scrapers.models import Job
from pipeline.sources.registry import SOURCES

logger = logging.getLogger(__name__)


def scrape() -> list[Job]:
    seen_global_ids = get_seen_global_ids()
    jobs: list[Job] = []

    for source in SOURCES:
        logger.info(f"Scraping source: {source.name}")
        scraped = source.scrape(seen_global_ids=seen_global_ids)
        logger.info(f"[{source.name}] found {len(scraped)} new job(s)")
        jobs.extend(scraped)

    return jobs
