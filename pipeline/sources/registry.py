from pathlib import Path
import pandas as pd
from jobhive.scrapers import TikTokScraper, SmartRecruitersScraper, LeverScraper
from .base import ScraperSource
from .scrapers.careersgov import CareersGovScraper
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def _load_slugs(scraper_name: str, company_url_as_slug: bool = False) -> list[str]:
    path = DATA_DIR / f"{scraper_name.lower()}.csv"
    if company_url_as_slug:
        return pd.read_csv(path)["url"].tolist()
    return pd.read_csv(path)["slug"].tolist()

SOURCES: list[ScraperSource] = [
    ScraperSource(
        name="tiktok",
        scraper_cls=TikTokScraper,
        slugs=["placeholder"],  
        max_workers=1,
    ),
    ScraperSource(
        name="smartrecruiters",
        scraper_cls=SmartRecruitersScraper,
        slugs=_load_slugs("smartrecruiters"),
        max_workers=8,
    ),
    ScraperSource(
        name="lever",
        scraper_cls=LeverScraper,
        slugs=_load_slugs("lever"),
        max_workers=8,
    ),
    ScraperSource(
        name="careers@gov",
        scraper_cls=CareersGovScraper,
        slugs=["placeholder"],
        max_workers=1,
    ),
]
