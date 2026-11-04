from datetime import datetime, timezone
import logging
from app.integrations.firebase import (
    DOCUMENTS_URL,
    firestore_request,
    FirestoreNotFoundError,
)

from app.integrations.firebase import DOCUMENTS_URL, firestore_request
from app.services.lead_service import encode_fields, decode_fields

logger = logging.getLogger(__name__)


def utc_now():
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def get_recovery_job(job_id: str):
    """Return an existing job, or None if it does not exist."""

    url = f"{DOCUMENTS_URL}/recovery_jobs/{job_id}"

    try:
        response = firestore_request("GET", url)

        if not response:
            return None

        return decode_fields(response.get("fields", {}))

    except FirestoreNotFoundError:
        # A missing job is expected during its first creation.
        return None


def create_recovery_job(lead: dict):
    lead_id = lead["lead_id"]

    # This is the next proposed campaign attempt.
    # It is NOT counted as a completed or sent attempt.
    attempt_number = int(lead.get("recovery_attempts", 0)) + 1

    job_id = f"RECOVERY_{lead_id}_A{attempt_number}"
    existing_job = get_recovery_job(job_id)

    if existing_job:
        return {
            **existing_job,
            "job_id": job_id,
            "created": False,
        }

    now = utc_now()

    job_data = {
        "job_id": job_id,
        "lead_id": lead_id,
        "lead_name": lead.get("name"),
        "channel": "whatsapp",
        "attempt_number": attempt_number,
        "retry_count": 0,

        # Preview only. No worker will send this job.
        "status": "preview",
        "mode": "dry_run",

        "scheduled_at": None,
        "executed_at": None,
        "last_error": None,

        "created_at": now,
        "updated_at": now,
    }

    url = f"{DOCUMENTS_URL}/recovery_jobs"

    firestore_request(
        "POST",
        url,
        params={"documentId": job_id},
        json={"fields": encode_fields(job_data)},
    )

    return {
        **job_data,
        "created": True,
    }


def list_recovery_jobs():
    url = f"{DOCUMENTS_URL}/recovery_jobs"

    response = firestore_request("GET", url)

    # Convert requests.Response into a Python dictionary
    data = response.json()

    documents = data.get("documents", [])

    jobs = []

    for document in documents:
        job = decode_fields(document.get("fields", {}))
        job["job_id"] = document["name"].split("/")[-1]
        jobs.append(job)

    return sorted(
        jobs,
        key=lambda job: job.get("created_at", ""),
        reverse=True,
    )