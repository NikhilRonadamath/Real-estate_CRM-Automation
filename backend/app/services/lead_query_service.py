from datetime import datetime, timezone
from urllib.parse import quote

from app.core.config import settings
from app.integrations.firebase import DOCUMENTS_URL, firestore_request
from app.services.lead_service import decode_fields, encode_fields

COLLECTION = settings.FIREBASE_COLLECTION


def list_leads() -> list[dict]:
    """Return all lead documents from the configured Firestore collection."""
    leads = []
    page_token = None

    while True:
        params = {"pageSize": 100}

        if page_token:
            params["pageToken"] = page_token

        page = firestore_request(
            "GET",
            f"{DOCUMENTS_URL}/{COLLECTION}",
            params=params,
        ).json()

        for document in page.get("documents", []):
            lead = decode_fields(document.get("fields", {}))
            lead_id = (
                lead.get("lead_id")
                or document.get("name", "").rsplit("/", 1)[-1]
            )
            lead.setdefault("lead_id", lead_id)
            lead["id"] = lead_id
            leads.append(lead)

        page_token = page.get("nextPageToken")

        if not page_token:
            return leads


def get_lead(lead_id: str) -> dict:
    """Return one lead by Firestore document ID."""
    path_id = quote(lead_id, safe="")

    document = firestore_request(
        "GET",
        f"{DOCUMENTS_URL}/{COLLECTION}/{path_id}",
    ).json()

    lead = decode_fields(document.get("fields", {}))

    resolved_id = (
        lead.get("lead_id")
        or document.get("name", "").rsplit("/", 1)[-1]
    )

    lead.setdefault("lead_id", resolved_id)
    lead["id"] = resolved_id

    return lead


def update_lead_status(lead_id: str, new_status: str) -> dict:
    """Update only the status and update timestamp for an existing lead."""

    lead = get_lead(lead_id)

    updated_at = (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )

    path_id = quote(lead_id, safe="")

    response = firestore_request(
        "PATCH",
        f"{DOCUMENTS_URL}/{COLLECTION}/{path_id}",
        params={
            "updateMask.fieldPaths": [
                "status",
                "updated_at",
            ],
        },
        json={
            "fields": encode_fields(
                {
                    "status": new_status,
                    "updated_at": updated_at,
                }
            )
        },
    )

    updated = decode_fields(
        response.json().get("fields", {})
    )

    lead.update(updated)
    lead["status"] = new_status
    lead["updated_at"] = updated_at

    return lead


def save_lead_ai_analysis(lead_id: str, analysis: dict) -> dict:
    """
    Save the complete AI analysis and synchronize important
    AI-generated values with the main CRM lead fields.
    """

    from app.models.ai_response import AILeadAnalysis

    # Validate the AI response before saving it.
    validated = AILeadAnalysis.model_validate(analysis)
    analysis_data = validated.model_dump(mode="json")

    analyzed_at = (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )

    # Ensure the lead exists before updating.
    get_lead(lead_id)

    # Map AI seller intent to the CRM lead status.
    intent_status_map = {
        "ready_to_sell": "qualified",
        "exploring": "nurturing",
        "uncertain": "nurturing",
        "not_interested": "closed",
        "unknown": "new",
    }

    new_status = intent_status_map.get(
        analysis_data.get("seller_intent"),
        "new",
    )

    # Save both the complete analysis and important values
    # directly on the main lead document.
    fields_to_update = {
        "ai_analysis": analysis_data,
        "ai_analyzed_at": analyzed_at,
        "lead_score": analysis_data.get("lead_score", 0),
        "seller_intent": analysis_data.get(
            "seller_intent",
            "unknown",
        ),
        "ai_enabled": True,
        "ai_status": "analyzed",
        "status": new_status,
        "updated_at": analyzed_at,
    }

    path_id = quote(lead_id, safe="")

    response = firestore_request(
        "PATCH",
        f"{DOCUMENTS_URL}/{COLLECTION}/{path_id}",
        params={
            "updateMask.fieldPaths": [
                "ai_analysis",
                "ai_analyzed_at",
                "lead_score",
                "seller_intent",
                "ai_enabled",
                "ai_status",
                "status",
                "updated_at",
            ],
        },
        json={
            "fields": encode_fields(fields_to_update)
        },
    )

    saved_fields = decode_fields(
        response.json().get("fields", {})
    )

    print(
        f"AI analysis and CRM fields updated successfully "
        f"for lead {lead_id}"
    )

    return {
        "analysis": saved_fields.get(
            "ai_analysis",
            analysis_data,
        ),
        "analyzed_at": saved_fields.get(
            "ai_analyzed_at",
            analyzed_at,
        ),
    }