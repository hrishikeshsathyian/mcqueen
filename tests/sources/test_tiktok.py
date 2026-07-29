from ats_scrapers.scrapers import TikTokScraper

API_URL = "https://api.lifeattiktok.com/api/v1/public/supplier/search/job/posts"

FAKE_POST = {
    "id": 111222,
    "title": "Software Engineer Intern",
    "description": "Fake description.",
    "requirement": "Fake requirements.",
    "recruit_type": {"en_name": "Intern"},
    "job_category": {"en_name": "Engineering"},
    "location_info": {"en_name": "Singapore"},
}


def test_fetch_parses_one_fake_post(httpx_mock):
    httpx_mock.add_response(
        url=API_URL,
        method="POST",
        json={"data": {"job_post_list": [FAKE_POST], "count": 1}},
    )

    jobs = TikTokScraper("fake-slug").fetch()

    assert len(jobs) == 1
    job = jobs[0]
    assert job.title == "Software Engineer Intern"
    assert job.ats_id == "111222"
    assert job.employment_type == "INTERN"


def test_fetch_returns_empty_list_when_no_posts(httpx_mock):
    httpx_mock.add_response(
        url=API_URL,
        method="POST",
        json={"data": {"job_post_list": [], "count": 0}},
    )

    jobs = TikTokScraper("fake-slug").fetch()

    assert jobs == []
