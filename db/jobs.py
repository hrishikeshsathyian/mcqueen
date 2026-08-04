import logging

from .client import supabase
from .models import SeenJobCreate
from ats_scrapers.models import Job as JobHiveJob
from postgrest import APIError
from typing import cast

logger = logging.getLogger(__name__)


def upsert_dropped_jobs(jobs: list[JobHiveJob]) -> None:
    rows = [SeenJobCreate.from_job(job).model_dump(mode="json") for job in jobs]
    try:
        # ON CONFLICT (global_id) DO NOTHING
        supabase.table("dropped_jobs_non_tech").upsert(
            rows, on_conflict="global_id", ignore_duplicates=True
        ).execute()
        logger.info(f"Upserted {len(rows)} job(s) into dropped_jobs_non_tech")
    except APIError:
        logger.error("Error occurred trying to insert jobs to dropped_jobs_non_tech", exc_info=True)


def upsert_seen_jobs(jobs: list[JobHiveJob]) -> None:
    rows = [SeenJobCreate.from_job(job).model_dump(mode="json") for job in jobs]
    try:
        # ON CONFLICT (global_id) DO NOTHING
        supabase.table("seen_jobs").upsert(
            rows, on_conflict="global_id", ignore_duplicates=True
        ).execute()
        logger.info(f"Upserted {len(rows)} job(s) into seen_jobs")
    except APIError:
        logger.error("Error occurred trying to insert jobs to seen_jobs", exc_info=True)


def get_seen_global_ids() -> set[str]:
    response = supabase.table("seen_jobs").select("global_id").execute()
    rows = cast(list[dict[str, str]], response.data)
    ids: set[str] = set()
    for row in rows:
        ids.add(row["global_id"])
    logger.debug(f"Retrieved {len(ids)} seen global id(s)")
    return ids


def get_seen_jobs_csv_rows() -> list[dict[str, str]]:
    # Backed by the `export_seen_jobs_csv` function defined in db/migrations,
    # which coalesces apply_url/url into a single `url` column.
    response = supabase.rpc("export_seen_jobs_csv").execute()
    rows = cast(list[dict[str, str]], response.data)
    logger.debug(f"Retrieved {len(rows)} seen job row(s) for CSV export")
    return rows
