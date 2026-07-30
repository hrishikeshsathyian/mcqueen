from typing import Callable
from ats_scrapers.models import Job
from dataclasses import dataclass
from ats_scrapers.scrapers import BaseScraper
from ats_scrapers.exceptions import ATSScrapersError
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import re

logger = logging.getLogger(__name__)

JobFilter = Callable[[Job], bool]


def default_is_singapore(j: Job) -> bool:
    _SINGAPORE_RE = re.compile(r"\b(singapore|sg|sgp)\b", re.IGNORECASE)
    return bool(j.location and _SINGAPORE_RE.search(j.location))


def default_is_intern(j: Job) -> bool:
    _INTERN_RE = re.compile(r"\bintern", re.IGNORECASE)
    return bool(j.employment_type and j.employment_type == "INTERN") or bool(
        j.title and _INTERN_RE.search(j.title)
    )

def default_is_tech(j: Job) -> bool: 
    return True

@dataclass
class ScraperSource:
    name: str
    scraper_cls: type[BaseScraper]
    slugs: list[str]
    is_singapore: JobFilter = default_is_singapore
    is_intern: JobFilter = default_is_intern
    is_tech: JobFilter = default_is_tech
    max_workers: int = 8

    def _fetch_one(self, slug: str) -> list[Job]:
        return self.scraper_cls(slug).fetch()

    def _fetch_raw(self) -> list[Job]:
        if len(self.slugs) == 1:
            return self._fetch_one(self.slugs[0])
        raw_jobs: list[Job] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {pool.submit(self._fetch_one, slug): slug for slug in self.slugs}
            for i, future in enumerate(as_completed(futures), start=1):
                slug = futures[future]
                try:
                    result = future.result()
                except ATSScrapersError as exc:
                    logger.warning(f"[{self.name}] skipped {slug}: {exc}")
                    continue
                except Exception as exc:
                    logger.error(
                        f"[{self.name}] unexpected error for {slug}: {exc}",
                        exc_info=True,
                    )
                    continue
                raw_jobs.extend(result)
                logger.info(f"[{self.name}] ({i}/{len(futures)}) {slug}")
        return raw_jobs

    def _filter(self, jobs: list[Job], seen_global_ids: set[str]) -> list[Job]:
        filtered_jobs: list[Job] = []
        dropped_jobs_country: list[Job] = []
        dropped_jobs_role: list[Job] = []
        dropped_jobs_non_tech: list[Job] = []

        for j in jobs:
            global_id = f"{j.ats_type}:{j.ats_id}"
            ## check if seen before 
            if global_id in seen_global_ids:
                continue

            if not self.is_singapore(j):
                dropped_jobs_country.append(j)
                continue 

            if not self.is_intern(j):
                dropped_jobs_role.append(j)
                continue

            if not self.is_tech(j):
                dropped_jobs_non_tech.append(j)

            filtered_jobs.append(j)

        logger.debug(
            f"[{self.name}] filtered {len(filtered_jobs)}/{len(jobs)} job(s) "
            f"(dropped: {len(dropped_jobs_country)} non-SG, "
            f"{len(dropped_jobs_role)} non-intern, "
            f"{len(dropped_jobs_non_tech)} non-tech)"
        )
        return filtered_jobs

    def scrape(self, seen_global_ids: set[str]) -> list[Job]:
        return self._filter(self._fetch_raw(), seen_global_ids)
