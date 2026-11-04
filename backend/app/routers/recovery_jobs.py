import logging

from fastapi import APIRouter, HTTPException, status

from app.services.lead_query_service import list_leads
from app.services.recovery_policy import evaluate_lead
from app.services.recovery_job_service import (
    create_recovery_job,
    list_recovery_jobs,
)

router = APIRouter(prefix="/api/recovery", tags=["AI Lead Recovery"])

logger = logging.getLogger(__name__)


@router.get("/preview")
def preview_recovery():
    """Check lead eligibility. Does not create jobs or send messages."""
    try:
        results = [evaluate_lead(lead) for lead in list_leads()]

        eligible = [item for item in results if item["eligible"]]
        blocked = [item for item in results if not item["eligible"]]

        return {
            "success": True,
            "mode": "dry_run",
            "messages_sent": 0,
            "total_leads_scanned": len(results),
            "eligible_count": len(eligible),
            "blocked_count": len(blocked),
            "eligible_leads": eligible,
            "blocked_leads": blocked,
        }

    except Exception:
        logger.exception("Recovery preview failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to scan recovery leads",
        )


@router.post("/jobs/dry-run")
def create_recovery_jobs_dry_run():
    """
    Create preview job records for currently eligible leads.
    This endpoint never sends messages.
    """
    try:
        leads = list_leads()

        created_jobs = []
        existing_jobs = []
        skipped_leads = []

        for lead in leads:
            eligibility = evaluate_lead(lead)

            if not eligibility["eligible"]:
                skipped_leads.append({
                    "lead_id": lead.get("lead_id"),
                    "name": lead.get("name"),
                    "reasons": eligibility["reasons"],
                })
                continue

            job = create_recovery_job(lead)

            if job["created"]:
                created_jobs.append(job)
            else:
                existing_jobs.append(job)

        return {
            "success": True,
            "mode": "dry_run",
            "messages_sent": 0,
            "created_count": len(created_jobs),
            "existing_count": len(existing_jobs),
            "skipped_count": len(skipped_leads),
            "created_jobs": created_jobs,
            "existing_jobs": existing_jobs,
            "skipped_leads": skipped_leads,
        }

    except Exception:
        logger.exception("Recovery job creation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create recovery jobs",
        )


@router.get("/jobs")
def get_recovery_jobs():
    """List recovery job records."""
    try:
        jobs = list_recovery_jobs()

        return {
            "success": True,
            "total": len(jobs),
            "jobs": jobs,
        }

    except Exception:
        logger.exception("Fetching recovery jobs failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch recovery jobs",
        )