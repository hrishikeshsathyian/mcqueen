from ats_scrapers.scrapers import SmartRecruitersScraper

FAKE_SLUG = "fake-company"
FAKE_URL = f"https://api.smartrecruiters.com/v1/companies/{FAKE_SLUG}/postings"

FAKE_POSTING = {
    "id": "fake-job-1",
    "name": "Software Engineer Intern",
    "location": {"city": "Singapore", "country": "Singapore"},
    "typeOfEmployment": {"id": "intern", "label": "Internship"},
    "releasedDate": "2026-01-01T00:00:00.000Z",
}


def test_fetch_parses_one_fake_posting(httpx_mock):
    httpx_mock.add_response(
        url=f"{FAKE_URL}?limit=100&offset=0", json={"content": [FAKE_POSTING]}
    )

    jobs = SmartRecruitersScraper(FAKE_SLUG, include_descriptions=False).fetch()

    assert len(jobs) == 1
    job = jobs[0]
    assert job.title == "Software Engineer Intern"
    assert job.ats_id == "fake-job-1"
    assert job.location == "Singapore, Singapore"
    assert job.employment_type == "INTERN"


def test_fetch_returns_empty_list_for_empty_board(httpx_mock):
    httpx_mock.add_response(url=f"{FAKE_URL}?limit=100&offset=0", json={"content": []})

    jobs = SmartRecruitersScraper(FAKE_SLUG, include_descriptions=False).fetch()

    assert jobs == []
