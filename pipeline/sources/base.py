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
    _INTERN_RE = re.compile(r"\b(intern|summer|fall|winter)\b", re.IGNORECASE)
    return bool(j.employment_type and j.employment_type == "INTERN") or bool(
        j.title and _INTERN_RE.search(j.title)
    )




# Non-software engineering disciplines to exclude even though they contain "engineer"
NON_TECH_ENGINEERING_RE = re.compile(
    r"\b(civil|mechanical|electrical|chemical|structural|industrial|"
    r"aerospace|biomedical|environmental|process)\s+engineer",
    re.IGNORECASE,
)


TECH_RE = re.compile(
    r"""
    \b(
        # --- generic role words (catch bare usage) ---
        software |
        developer(s)? | development |
        engineer(ing)?(s)? |                        # catches "Engineer", "Engineering", bare
        programmer |
        research(er)?\s+scientist | applied\s+scientist |
        algorithm(s)? |
        architect |

        # --- stack / specialization ---
        swe |
        full[-\s]?stack | front[-\s]?end | back[-\s]?end |
        computer\s+science | computer\s+engineer(ing)? |

        # --- data (broad catch, per your request) ---
        \bdata\b |
        data\s+(scien(ce|tist)|engineer(ing)?|analy(st|tics)) |

        # --- ML / AI ---
        machine\s+learning | \bml\b |
        artificial\s+intelligence | \bai\b |
        deep\s+learning | \bnlp\b |
        large\s+(language\s+)?model(s)? | \bllm\b |
        knowledge\s+graph |

        # --- infra / ops ---
        dev\s?ops | site\s+reliability | \bsre\b |
        cloud\s+engineer | infrastructure\s+engineer | platform\s+engineer |

        # --- security ---
        cyber\s?security | \bsecurity\b |           
        information\s+security | infosec |

        # --- QA / test ---
        quality\s+assurance | \bqa\s+engineer\b | test\s+engineer | \bsdet\b |

        # --- mobile ---
        mobile\s+(developer|engineer) |
        \bios\b\s+(developer|engineer) |
        android\s+(developer|engineer) |

        # --- product / program mgmt ---
        product\s+manag(er|ement) | associate\s+product\s+manager | \bapm\b |
        technical\s+program\s+manager | \btpm\b |

        # --- systems / IT ---
        information\s+technology | systems?\s+(engineer|development) |
        network\s+engineer |
        database\s+administrator | \bdba\b |

        # --- generic fallback ---
        technology |
        product\s+designer |
        IT | 
    )\b
    """,
    re.IGNORECASE | re.VERBOSE,
)

def default_is_tech(j: Job) -> bool:
    if j.department and j.department == "CAREERSGOV_TECH":
        return True
    haystack = " ".join(filter(None, [j.title, j.department]))
    if NON_TECH_ENGINEERING_RE.search(haystack):
        return False
    return bool(TECH_RE.search(haystack))


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
                    logger.error(f"[{self.name}] skipped {slug}: {exc}")
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

    def _filter(self, jobs: list[Job], seen_global_ids: set[str]) -> tuple[list[Job], list[Job]]:
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
        return (filtered_jobs, dropped_jobs_non_tech)

    def scrape(self, seen_global_ids: set[str]) -> tuple[list[Job], list[Job]]:
        return self._filter(self._fetch_raw(), seen_global_ids)
