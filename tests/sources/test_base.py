from ats_scrapers.exceptions import ATSScrapersError
from ats_scrapers.models import ATSType, Job

from pipeline.sources.base import ScraperSource


def _job(**overrides) -> Job:
    defaults = dict(
        url="https://example.com/job/1",
        title="Software Engineer Intern",
        company="Acme",
        ats_type=ATSType.CUSTOM,
        ats_id="1",
        location="Singapore",
        employment_type="INTERN",
    )
    defaults.update(overrides)
    return Job(**defaults)


class FakeScraper:
    """Stand-in scraper: `slug` selects canned behavior instead of hitting a URL."""

    def __init__(self, slug: str):
        self.slug = slug

    def fetch(self) -> list[Job]:
        if self.slug == "broken":
            raise ATSScrapersError("company not found")
        return [_job(ats_id=self.slug, company=self.slug)]


def test_fetch_raw_single_slug_returns_jobs():
    source = ScraperSource(name="fake", scraper_cls=FakeScraper, slugs=["fake-slug"])
    jobs = source.fetch_raw()
    assert len(jobs) == 1
    assert jobs[0].ats_id == "fake-slug"


def test_fetch_raw_skips_slugs_that_raise():
    source = ScraperSource(
        name="fake", scraper_cls=FakeScraper, slugs=["broken", "ok-slug"]
    )
    jobs = source.fetch_raw()
    assert [j.ats_id for j in jobs] == ["ok-slug"]


def test_filter_new_keeps_only_singapore_intern_and_unseen():
    source = ScraperSource(name="fake", scraper_cls=FakeScraper, slugs=["fake-slug"])
    jobs = [
        _job(ats_id="1", location="Singapore", employment_type="INTERN"),
        _job(ats_id="2", location="New York", employment_type="INTERN"),
        _job(
            ats_id="3",
            location="Singapore",
            employment_type="FULL_TIME",
            title="Software Engineer",
        ),
        _job(ats_id="4", location="Singapore", employment_type="INTERN"),
    ]
    seen_global_ids = {f"{jobs[3].ats_type}:{jobs[3].ats_id}"}

    result = source.filter_new(jobs, seen_global_ids)

    assert [j.ats_id for j in result] == ["1"]
