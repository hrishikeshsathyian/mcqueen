from pipeline.sources.scrapers.careersgov import CareersGovScraper

FAKE_POSTING = {
    "jobTitle": "Software Engineer Intern",
    "agency": "Fake Agency",
    "postingNo": "FAKE-001",
    "jobDescription": "Fake internship description.",
    "employmentType": "Internship",
    "employmentTypeCode": "0005",
    "fieldCode": "0017",
    "platform": "greenhouse",
    "jobId": "12345",
}

FAKE_NON_MATCHING_POSTING = {
    **FAKE_POSTING,
    "postingNo": "FAKE-002",
    "employmentType": "Full-time",
    "employmentTypeCode": "0001",
}


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_afetch_parses_matching_internship(monkeypatch):
    def fake_get(url, *args, **kwargs):
        return _FakeResponse([FAKE_POSTING, FAKE_NON_MATCHING_POSTING])

    monkeypatch.setattr("pipeline.sources.scrapers.careersgov.requests.get", fake_get)

    jobs = CareersGovScraper("fake-slug").fetch()

    assert len(jobs) == 1
    job = jobs[0]
    assert job.title == "Software Engineer Intern"
    assert job.company == "Fake Agency"
    assert job.ats_id == "FAKE-001"
    assert job.employment_type == "INTERN"
    assert (
        str(job.apply_url)
        == "https://jobs.careers.gov.sg/jobs/greenhouse/12345?gh_jid=12345"
    )
