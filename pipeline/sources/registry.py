from pathlib import Path
import pandas as pd
from jobhive.scrapers import TikTokScraper, SmartRecruitersScraper, LeverScraper
from .base import ScraperSource

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def _load_slugs(scraper_name: str) -> list[str]:
    path = DATA_DIR / f"{scraper_name.lower()}.csv"
    return pd.read_csv(path)["slug"].tolist()

SOURCES: list[ScraperSource] = [
    ScraperSource(
        name="tiktok",
        scraper_cls=TikTokScraper,
        slugs=["placeholder"],  # single-company scrapers have a redundant slug field
        max_workers=1,
    ),
    ScraperSource(
        name="smartrecruiters",
        scraper_cls=SmartRecruitersScraper,
        slugs=_load_slugs("smartrecruiters"),
        max_workers=32,
    ),
    ScraperSource(
        name="lever",
        scraper_cls=LeverScraper,
        slugs=_load_slugs("lever"),
        max_workers=32,
    ),
]
