import uuid
from datetime import datetime, timezone

from app.integrations.firebase import DOCUMENTS_URL, firestore_request
from app.services.lead_service import encode_fields, decode_fields


CONVERSATIONS_COLLECTION = "conversations"


def get_current_time():
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def find_lead_by_phone(phone: str):
    """
    Find a lead using the WhatsApp phone number.

    Twilio format:
    whatsapp:+917975070214

    Firestore format:
    +917975070214
    """

    clean_phone = phone.replace("whatsapp:", "").strip()

    response = firestore_request(
        "GET",
        f"{DOCUMENTS_URL}/leads",
    )

    documents = response.json().get("documents", [])

    for document in documents:
        lead = decode_fields(
            document.get("fields", {})
        )

        lead_phone = str(
            lead.get("phone", "")
        ).strip()

        if lead_phone == clean_phone:
            lead_id = (
                lead.get("lead_id")
                or document.get("name", "").rsplit("/", 1)[-1]
            )

            lead["lead_id"] = lead_id

            return lead

    return None


def save_message(
    lead_id: str,
    phone: str,
    sender: str,
    message: str,
):
    """
    Save one WhatsApp message as a Firestore document.
    """

    message_id = (
        f"MSG_{uuid.uuid4().hex[:16].upper()}"
    )

    message_data = {
        "message_id": message_id,
        "lead_id": lead_id,
        "phone": phone.replace(
            "whatsapp:", ""
        ).strip(),
        "sender": sender,
        "message": message,
        "timestamp": get_current_time(),
        "channel": "whatsapp",
    }

    firestore_request(
        "POST",
        f"{DOCUMENTS_URL}/{CONVERSATIONS_COLLECTION}",
        params={
            "documentId": message_id
        },
        json={
            "fields": encode_fields(message_data)
        },
    )

    print(
        f"Message saved: {message_id} "
        f"for lead {lead_id}"
    )

    return message_data

def update_lead_with_ai_analysis(
    lead_id: str,
    ai_analysis: dict,
):
    """
    Update the lead document with the latest AI analysis.
    """

    now = get_current_time()

    update_data = {
        "ai_enabled": True,
        "ai_status": "analyzed",
        "ai_analyzed_at": now,
        "updated_at": now,

        # Update important CRM fields
        "seller_intent": ai_analysis.get(
            "seller_intent",
            "unknown",
        ),
        "lead_score": ai_analysis.get(
            "lead_score",
            0,
        ),

        # Store complete AI analysis
        "ai_analysis": ai_analysis,
    }

    firestore_request(
        "PATCH",
        f"{DOCUMENTS_URL}/leads/{lead_id}",
        params={
            "updateMask.fieldPaths": list(
                update_data.keys()
            )
        },
        json={
            "fields": encode_fields(update_data)
        },
    )

    print(
        f"AI analysis saved for lead {lead_id}"
    )

def get_conversation_history(lead_id: str):
    """
    Return all saved conversation messages
    for a specific lead.
    """

    response = firestore_request(
        "GET",
        f"{DOCUMENTS_URL}/{CONVERSATIONS_COLLECTION}",
    )

    documents = response.json().get(
        "documents",
        [],
    )

    messages = []

    for document in documents:
        data = decode_fields(
            document.get("fields", {})
        )

        if data.get("lead_id") == lead_id:
            messages.append(data)

    messages.sort(
        key=lambda item: item.get(
            "timestamp",
            "",
        )
    )


    return messages