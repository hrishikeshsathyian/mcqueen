import pytest
from ats_scrapers.exceptions import ScraperError
from ats_scrapers.scrapers import WorkdayScraper

FAKE_URL = "https://fakeco.wd1.myworkdayjobs.com/fakecareers"
API_URL = "https://fakeco.wd1.myworkdayjobs.com/wday/cxs/fakeco/fakecareers/jobs"

FAKE_POSTING = {
    "title": "Software Engineer Intern",
    "externalPath": "/job/Singapore/Software-Engineer-Intern_R-FAKE-001",
    "locationsText": "Singapore",
    "timeType": "Full time",
    "postedOn": "Posted 5 Days Ago",
    "bulletFields": ["R-FAKE-001"],
}


def test_fetch_parses_one_fake_posting(httpx_mock):
    httpx_mock.add_response(
        url=API_URL,
        method="POST",
        json={"total": 1, "jobPostings": [FAKE_POSTING], "facets": []},
    )

    jobs = WorkdayScraper(FAKE_URL, include_descriptions=False).fetch()

    assert len(jobs) == 1
    job = jobs[0]
    assert job.title == "Software Engineer Intern"
    assert job.ats_id == "R-FAKE-001"
    assert job.location == "Singapore"
    assert str(job.url) == f"{FAKE_URL}{FAKE_POSTING['externalPath']}"


def test_fetch_returns_empty_list_for_empty_board(httpx_mock):
    httpx_mock.add_response(
        url=API_URL,
        method="POST",
        json={"total": 0, "jobPostings": [], "facets": []},
    )

    jobs = WorkdayScraper(FAKE_URL, include_descriptions=False).fetch()

    assert jobs == []


def test_fetch_raises_for_malformed_url():
    with pytest.raises(ScraperError):
        WorkdayScraper("https://not-a-workday-url.example.com").fetch()
