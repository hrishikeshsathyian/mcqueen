from ats_scrapers.scrapers import BaseScraper
from ats_scrapers.models import Job, ATSType
from typing import Any
import logging
import requests
from pydantic import HttpUrl

logger = logging.getLogger(__name__)

CAREERS_GOV_URL = "https://raw.githubusercontent.com/opengovsg/careersgovsg-jobs-data/main/data/job-listings.json"
CAREERS_GOV_INTERNSHIP_EMPLOYMENT_TYPE = "Internship"
CAREERS_GOV_INTERNSHIP_EMPLOYMENT_TYPE_CODE = "0005"
CAREERS_GOV_INDUSTRY_FIELD_CODE_OTHERS = "0025"
CAREERS_GOV_INDUSTRY_FIELD_CODE_IT = "0017"


class CareersGovScraper(BaseScraper):

    async def afetch(self) -> list[Job]:
        fetched: list[Job] = []
        response = requests.get(CAREERS_GOV_URL)
        response.raise_for_status()
        data: list[Any] = response.json()
        filtered = [
            posting
            for posting in data
            if posting["employmentType"] == CAREERS_GOV_INTERNSHIP_EMPLOYMENT_TYPE
            and posting["employmentTypeCode"]
            == CAREERS_GOV_INTERNSHIP_EMPLOYMENT_TYPE_CODE
            and (
                posting["fieldCode"] == CAREERS_GOV_INDUSTRY_FIELD_CODE_IT
            )
        ]
        for row in filtered:
            res: Job = self.parse(row)
            fetched.append(res)
        logger.debug(f"Fetched {len(fetched)} internship posting(s) from careers@gov")
        return fetched

    def parse(self, posting: Any) -> Job:
        return Job(
            url=HttpUrl(CAREERS_GOV_URL),
            title=posting["jobTitle"],
            company=posting["agency"],
            ats_type=ATSType.CUSTOM,
            ats_id=posting["postingNo"],
            location="Singapore",
            employment_type="INTERN",
            commitment=None,
            description=posting["jobDescription"],
            fetched_at=None,
            experience=None,
            apply_url=HttpUrl(self._build_listing_url(posting)),
            requisition_id=None,
            department="CAREERSGOV_TECH"
        )

    def _build_listing_url(self, posting: Any) -> str:
        platform = posting.get("platform", "").lower()
        job_id = posting.get("jobId", "")
        posting_no = posting.get("postingNo", "")
        if platform == "workable":
            return f"https://apply.workable.com/j/{posting_no}"
        if platform == "greenhouse":
            return (
                f"https://jobs.careers.gov.sg/jobs/{platform}/{job_id}?gh_jid={job_id}"
            )
        return f"https://jobs.careers.gov.sg/jobs/{platform}/{job_id}/{posting_no}"  # for hrp
