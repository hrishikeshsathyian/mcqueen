from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo

from jobhive.models import Job as JobHiveJob


class SeenJobCreate(BaseModel):
    ats_type: str
    ats_id: str

    url: str
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
            url=str(job.url),
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
