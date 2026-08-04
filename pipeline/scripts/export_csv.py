import csv
import logging
from pathlib import Path

from db.jobs import get_seen_jobs_csv_rows

logger = logging.getLogger(__name__)

CSV_PATH = Path("data/seen_jobs.csv")
FIELDNAMES = ["global_id", "title", "company", "url", "fetched_at"]


def export_seen_jobs_csv(path: Path = CSV_PATH) -> None:
    rows = get_seen_jobs_csv_rows()
    csv_rows = [
        {
            "global_id": row["global_id"],
            "title": row["title"],
            "company": row["company"],
            "url": row.get("apply_url") or row.get("url"),
            "fetched_at": row["fetched_at"],
        }
        for row in rows
    ]

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(csv_rows)

    logger.info(f"Exported {len(csv_rows)} seen job(s) to {path}")
