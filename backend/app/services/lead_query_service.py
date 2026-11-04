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
			"GET", f"{DOCUMENTS_URL}/{COLLECTION}", params=params
		).json()
		for document in page.get("documents", []):
			lead = decode_fields(document.get("fields", {}))
			lead_id = lead.get("lead_id") or document.get("name", "").rsplit("/", 1)[-1]
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
		"GET", f"{DOCUMENTS_URL}/{COLLECTION}/{path_id}"
	).json()
	lead = decode_fields(document.get("fields", {}))
	resolved_id = lead.get("lead_id") or document.get("name", "").rsplit("/", 1)[-1]
	lead.setdefault("lead_id", resolved_id)
	lead["id"] = resolved_id
	return lead


def update_lead_status(lead_id: str, new_status: str) -> dict:
	"""Update only the status and update timestamp for an existing lead."""
	lead = get_lead(lead_id)
	updated_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
		"+00:00", "Z"
	)
	path_id = quote(lead_id, safe="")
	response = firestore_request(
		"PATCH",
		f"{DOCUMENTS_URL}/{COLLECTION}/{path_id}",
		params={
			"updateMask.fieldPaths": ["status", "updated_at"],
		},
		json={"fields": encode_fields({"status": new_status, "updated_at": updated_at})},
	)
	updated = decode_fields(response.json().get("fields", {}))
	lead.update(updated)
	lead["status"] = new_status
	lead["updated_at"] = updated_at
	return lead


def save_lead_ai_analysis(lead_id: str, analysis: dict) -> dict:
    """Save the latest AI analysis without replacing other lead fields."""
    from app.models.ai_response import AILeadAnalysis

    # Validate before persisting.
    validated = AILeadAnalysis.model_validate(analysis)
    analysis_data = validated.model_dump(mode="json")

    analyzed_at = (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )

    # Ensure the lead exists before updating.
    get_lead(lead_id)

    fields_to_update = {
        "ai_analysis": analysis_data,
        "ai_analyzed_at": analyzed_at,
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
                "updated_at",
            ],
        },
        json={"fields": encode_fields(fields_to_update)},
    )

    saved_fields = decode_fields(response.json().get("fields", {}))

    return {
        "analysis": saved_fields["ai_analysis"],
        "analyzed_at": saved_fields["ai_analyzed_at"],
    }
