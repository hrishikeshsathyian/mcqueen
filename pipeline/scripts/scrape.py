from db.jobs import get_seen_global_ids
from ats_scrapers.models import Job
from pipeline.sources.registry import SOURCES


def scrape() -> list[Job]:
    seen_global_ids = get_seen_global_ids()
    jobs: list[Job] = []

    for source in SOURCES:
        scraped = source.scrape(seen_global_ids=seen_global_ids)
        jobs.extend(scraped)

    return jobs
