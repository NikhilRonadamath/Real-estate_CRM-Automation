
import logging

from fastapi import APIRouter, HTTPException, status

from app.ai.lead_analyzer import analyze_lead
from app.integrations.firebase import FirestoreNotFoundError
from app.services.lead_query_service import (
    get_lead,
    save_lead_ai_analysis,
)

router = APIRouter(prefix="/api/ai", tags=["AI Analysis"])
logger = logging.getLogger(__name__)


@router.get("/leads/{lead_id}/analysis")
def get_saved_lead_analysis(lead_id: str):
    """Retrieve saved analysis without calling Groq."""
    try:
        lead = get_lead(lead_id)

        return {
            "success": True,
            "lead_id": lead_id,
            "analysis": lead.get("ai_analysis"),
            "analyzed_at": lead.get("ai_analyzed_at"),
        }

    except FirestoreNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        ) from error

    except Exception as error:
        logger.exception(
            "Failed to retrieve saved AI analysis for lead %s",
            lead_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve saved AI analysis.",
        ) from error


@router.post("/leads/{lead_id}/analyze")
def analyze_lead_endpoint(lead_id: str):
    """Generate, validate, and persist a new AI analysis."""
    try:
        lead = get_lead(lead_id)

        # Groq returns a validated AILeadAnalysis model.
        analysis = analyze_lead(lead)

    except FirestoreNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        ) from error

    except RuntimeError as error:
        logger.exception("AI lead analysis failed")

        detail = str(error)

        if (
            "GROQ_API_KEY" in detail
            or "Groq SDK is not installed" in detail
        ):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=detail,
            ) from error

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI analysis could not be completed. Please try again.",
        ) from error

    except Exception as error:
        logger.exception(
            "AI lead analysis failed for lead %s",
            lead_id,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI analysis could not be completed. Please try again.",
        ) from error

    # Separate persistence errors from Groq errors.
    try:
        saved = save_lead_ai_analysis(
            lead_id,
            analysis.model_dump(mode="json"),
        )

        return {
            "success": True,
            "lead_id": lead_id,
            "analysis": saved["analysis"],
            "analyzed_at": saved["analyzed_at"],
        }

    except FirestoreNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        ) from error

    except Exception as error:
        logger.exception(
            "AI analysis generated but could not be saved for lead %s",
            lead_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI analysis was generated but could not be saved.",
        ) from error
