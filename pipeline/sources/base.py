from typing import Callable
from ats_scrapers.models import Job
from dataclasses import dataclass
from ats_scrapers.scrapers import BaseScraper
from ats_scrapers.exceptions import ATSScrapersError
from concurrent.futures import ThreadPoolExecutor, as_completed

JobFilter = Callable[[Job], bool]

def default_is_singapore(j: Job) -> bool:
    return bool(j.location and ("singapore" in j.location.lower() or "sg" in j.location.lower()))

def default_is_intern(j: Job) -> bool:
    return bool(j.employment_type and j.employment_type == "INTERN") or bool(j.title and "intern" in j.title.lower())

@dataclass 
class ScraperSource: 
    name: str 
    scraper_cls: type[BaseScraper]
    slugs: list[str]
    is_singapore: JobFilter = default_is_singapore
    is_intern: JobFilter = default_is_intern
    max_workers: int = 8

    def _fetch_one(self, slug: str) -> list[Job]:
        try:
            return self.scraper_cls(slug).fetch()
        except ATSScrapersError as exc:
            print(f"[{self.name}] {slug}: {type(exc).__name__}: {exc}")
            return []

    def fetch_raw(self) -> list[Job]: 
        if len(self.slugs) == 1: 
            return self._fetch_one(self.slugs[0])
        jobs: list[Job] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {pool.submit(self._fetch_one, slug): slug for slug in self.slugs}
            for i, future in enumerate(as_completed(futures), start=1):
                slug = futures[future]
                try:
                    result = future.result()
                except ATSScrapersError as exc:
                    print(f"[{self.name}] skipped {slug}: {exc}")
                    continue
                except Exception as exc:
                    print(f"[{self.name}] unexpected error for {slug}: {exc}")
                    continue
                jobs.extend(result)
                print(f"[{self.name}] ({i}/{len(futures)}) {slug}")
        return jobs
    
    def filter_new(self, jobs: list[Job], seen_global_ids: set[str]) -> list[Job]:
        result : list[Job] = []
        for j in jobs:
            global_id = f"{j.ats_type}:{j.ats_id}"
            if self.is_singapore(j) and self.is_intern(j) and global_id not in seen_global_ids:
                result.append(j)
        return result

