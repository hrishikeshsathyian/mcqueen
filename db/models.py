from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo

from ats_scrapers.models import Job as JobHiveJob


class SeenJobCreate(BaseModel):
    ats_type: str
    ats_id: str | None

    apply_url: str | None
    url: str | None
    company: str
    title: str

    location: Optional[str] = None
    employment_type: Optional[str] = None
    department: Optional[str] = None
    posted_at: Optional[datetime] = None
    fetched_at: datetime = datetime.now(ZoneInfo("Asia/Singapore"))

    @classmethod
    def from_job(cls, job: JobHiveJob) -> "SeenJobCreate":
        return cls(
            ats_type=job.ats_type.value,
            ats_id=job.ats_id,
            apply_url=str(job.apply_url) if job.apply_url else None,
            url=str(job.url) if job.url else None,
            company=job.company,
            title=job.title,
            location=job.location,
            employment_type=job.employment_type,
            department=job.department,
            posted_at=job.posted_at,
        )


class SeenJob(SeenJobCreate):
    global_id: str

    model_config = ConfigDict(from_attributes=True)
