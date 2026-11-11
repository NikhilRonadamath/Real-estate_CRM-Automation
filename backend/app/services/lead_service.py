import uuid
from datetime import datetime, timezone

from app.services.whatsapp_service import send_welcome_message
from app.core.config import settings
from app.integrations.firebase import DOCUMENTS_URL, firestore_request
from app.models.lead import LeadCreate


COLLECTION = settings.FIREBASE_COLLECTION


def encode_value(value):
    if value is None:
        return {"nullValue": None}
    if isinstance(value, bool):
        return {"booleanValue": value}
    if isinstance(value, int):
        return {"integerValue": str(value)}
    if isinstance(value, float):
        return {"doubleValue": value}
    if isinstance(value, str):
        return {"stringValue": value}
    if isinstance(value, dict):
        return {"mapValue": {"fields": encode_fields(value)}}
    if isinstance(value, list):
        return {"arrayValue": {"values": [encode_value(item) for item in value]}}
    raise ValueError(f"Unsupported Firestore value: {type(value).__name__}")


def encode_fields(data: dict) -> dict:
    return {key: encode_value(value) for key, value in data.items()}


def decode_value(value):
    for key, decoded in value.items():
        if key == "nullValue":
            return None
        if key == "integerValue":
            return int(decoded)
        if key == "doubleValue":
            return float(decoded)
        if key in {"stringValue", "booleanValue", "timestampValue"}:
            return decoded
        if key == "mapValue":
            return decode_fields(decoded.get("fields", {}))
        if key == "arrayValue":
            return [
                decode_value(item)
                for item in decoded.get("values", [])
            ]
        if key == "geoPointValue":
            return decoded
    return None


def decode_fields(fields: dict) -> dict:
    return {
        key: decode_value(value)
        for key, value in fields.items()
    }


def create_lead(lead_data: dict) -> dict:
    lead_id = f"LEAD_{uuid.uuid4().hex[:12].upper()}"

    now = (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )

    lead_data.update(
        {
            "lead_id": lead_id,
            "status": "new",
            "source": "website_form",
            "seller_intent": "unknown",
            "lead_score": 0,
            "ai_enabled": False,
            "created_at": now,
            "updated_at": now,

            # Communication
            "preferred_channel": "whatsapp",
            "whatsapp_opt_in": False,
            "consent_source": None,
            "consent_recorded_at": None,
            "do_not_contact": False,

            # Recovery tracking
            "recovery_attempts": 0,
            "retry_count": 0,
            "recovery_status": "not_started",
            "last_contacted_at": None,
            "next_contact_at": None,

            # AI configuration
            "ai_status": "ready",
        }
    )

    # Save the lead to Firestore first.
    firestore_request(
        "POST",
        f"{DOCUMENTS_URL}/{COLLECTION}",
        params={"documentId": lead_id},
        json={"fields": encode_fields(lead_data)},
    )

    # Automatically send a WhatsApp welcome message.
whatsapp_result = None

print(
    f"Lead {lead_id} created successfully. "
    "Starting WhatsApp communication..."
)

try:
    whatsapp_result = send_welcome_message(
        name=lead_data["name"],
        phone=lead_data["phone"],
    )

    print(f"WhatsApp result for {lead_id}: {whatsapp_result}")

except Exception as error:
    # Lead creation should not fail if WhatsApp temporarily fails.
    print(f"WhatsApp message failed for {lead_id}: {error}")

return {
    "success": True,
    "message": "Lead registered successfully",
    "lead_id": lead_id,
    "whatsapp": whatsapp_result,
}


def get_leads() -> list[dict]:
    leads = []
    page_token = None

    while True:
        params = {"pageSize": 100}

        if page_token:
            params["pageToken"] = page_token

        response = firestore_request(
            "GET",
            f"{DOCUMENTS_URL}/{COLLECTION}",
            params=params,
        )

        page = response.json()

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


def get_lead(lead_id: str):
    response = firestore_request(
        "GET",
        f"{DOCUMENTS_URL}/{COLLECTION}/{lead_id}",
    )

    document = response.json()
    lead = decode_fields(document.get("fields", {}))

    lead_id_value = (
        lead.get("lead_id")
        or document.get("name", "").rsplit("/", 1)[-1]
    )

    lead.setdefault("lead_id", lead_id_value)
    lead["id"] = lead_id_value

    return lead


class LeadService:
    @staticmethod
    def create_lead(lead: LeadCreate):
        return create_lead(lead.model_dump())

    @staticmethod
    def get_leads():
        return get_leads()

    @staticmethod
    def get_lead(lead_id: str):
        return get_lead(lead_id)