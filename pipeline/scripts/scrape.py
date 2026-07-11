from db.jobs import get_seen_global_ids
from jobhive.models import Job
from pipeline.sources.registry import SOURCES

def scrape() -> list[Job]: 
    seen_global_ids = get_seen_global_ids()
    jobs: list[Job] = []

    for source in SOURCES:
        print(f"Fetching for source [{source.name}]")
        raw = source.fetch_raw()
        filtered = source.filter_new(raw, seen_global_ids) 
        print(f"[{source.name}] {len(filtered)} new matching jobs")
        jobs.extend(filtered)

    return jobs
