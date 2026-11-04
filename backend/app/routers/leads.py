import logging

from fastapi import APIRouter, HTTPException, status

from app.integrations.firebase import FirestoreNotFoundError
from app.models.lead import LeadCreate, LeadResponse, LeadStatusUpdate
from app.services.lead_query_service import (
	get_lead as query_get_lead,
	list_leads,
	update_lead_status,
)
from app.services.lead_service import LeadService

router = APIRouter(prefix="/api/leads", tags=["Lead Management"])
logger = logging.getLogger(__name__)


@router.post(
	"/",
	response_model=LeadResponse,
	status_code=status.HTTP_201_CREATED,
)
def create_lead(lead: LeadCreate):
	try:
		result = LeadService.create_lead(lead)
		return {
			"success": True,
			"message": "Lead registered successfully",
			**result,
		}
	except Exception:
		logger.exception("Failed to create lead")
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Unable to register lead. Please try again.",
		)


@router.get("/")
def get_leads():
	try:
		return list_leads()
	except Exception:
		logger.exception("Failed to retrieve leads")
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Unable to retrieve leads. Please try again.",
		)


@router.get("/{lead_id}")
def get_lead(lead_id: str):
	try:
		lead = query_get_lead(lead_id)
	except FirestoreNotFoundError:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Lead not found",
		)
	except Exception:
		logger.exception("Failed to retrieve lead %s", lead_id)
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Unable to retrieve lead. Please try again.",
		)

	if lead is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Lead not found",
		)
	return lead


@router.patch("/{lead_id}/status")
def patch_lead_status(lead_id: str, update: LeadStatusUpdate):
	try:
		lead = update_lead_status(lead_id, update.status)
	except FirestoreNotFoundError:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Lead not found",
		)
	except Exception:
		logger.exception("Failed to update status for lead %s", lead_id)
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Unable to update lead status. Please try again.",
		)
	return {"success": True, "lead": lead}
