from jobhive.exceptions import JobHiveError
from jobhive.scrapers import TikTokScraper
from jobhive.models import Job
from db.jobs import update_seen_jobs, get_seen_global_ids

slug = "placeholder" # single company scrapers have redundant slug fields s

def scrape() -> list[Job]: 
    try:
        seen_global_ids: set[str] = get_seen_global_ids()
        print("Fetching jobs from tiktok...")
        jobs = TikTokScraper(slug).fetch()
        filtered_jobs: list[Job] = []
        for j in jobs:
            global_id = f"{j.ats_type}:{j.ats_id}"
            if (
                j.location
                and ("singapore" in j.location.lower() or "sg" in j.location.lower())
                and j.employment_type
                and j.employment_type == "INTERN"
                and global_id not in seen_global_ids
            ):
                filtered_jobs.append(j)
        print(f"Found {len(filtered_jobs)} unique jobs")
        if len(filtered_jobs) == 0:
            return []
        update_seen_jobs(filtered_jobs)
        return filtered_jobs

    except JobHiveError as exc:
        print(str(exc))
        return []


