from ats_scrapers.scrapers import LeverScraper

FAKE_SLUG = "fake-company"
FAKE_URL = f"https://api.lever.co/v0/postings/{FAKE_SLUG}?mode=json"

FAKE_POSTING = {
    "id": "fake-job-1",
    "text": "Software Engineer Intern",
    "hostedUrl": "https://jobs.lever.co/fake-company/fake-job-1",
    "categories": {
        "location": "Singapore",
        "commitment": "Internship",
        "department": "Engineering",
        "team": "Platform",
    },
    "description": "<p>Fake job description.</p>",
    "lists": [],
    "workplaceType": "on-site",
}


def test_fetch_parses_one_fake_posting(httpx_mock):
    httpx_mock.add_response(url=FAKE_URL, json=[FAKE_POSTING])

    jobs = LeverScraper(FAKE_SLUG).fetch()

    assert len(jobs) == 1
    job = jobs[0]
    assert job.title == "Software Engineer Intern"
    assert job.ats_id == "fake-job-1"
    assert job.location == "Singapore"
    assert job.employment_type == "INTERN"


def test_fetch_returns_empty_list_for_empty_board(httpx_mock):
    httpx_mock.add_response(url=FAKE_URL, json=[])

    jobs = LeverScraper(FAKE_SLUG).fetch()

    assert jobs == []
