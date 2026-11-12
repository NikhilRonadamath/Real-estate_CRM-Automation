from datetime import datetime, timezone
from urllib.parse import parse_qs
from xml.sax.saxutils import escape

from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.services.lead_service import (
    get_lead_by_phone,
    update_lead,
)


router = APIRouter(
    prefix="/api/whatsapp",
    tags=["WhatsApp"],
)


@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """Receive incoming WhatsApp messages from Twilio."""

    raw_body = await request.body()
    form_data = parse_qs(raw_body.decode("utf-8"))

    sender = form_data.get("From", [""])[0]
    incoming_message = form_data.get("Body", [""])[0]
    message_sid = form_data.get("MessageSid", [""])[0]

    print("\n--- Incoming WhatsApp Message ---")
    print("Sender:", sender)
    print("Message:", incoming_message)
    print("Message SID:", message_sid)

    # Find the lead using the sender's WhatsApp number.
    lead = get_lead_by_phone(sender)

    if lead:
        lead_id = lead["lead_id"]

        now = (
            datetime.now(timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z")
        )

        updated_lead = update_lead(
            lead_id,
            {
                # AI becomes active once the user starts interacting.
                "ai_enabled": True,
                "ai_status": "active",

                # Lead communication status.
                "status": "engaged",
                "preferred_channel": "whatsapp",

                # Track the latest communication.
                "last_contacted_at": now,
                "last_message": incoming_message,
                "last_message_at": now,
            },
        )

        print(f"Lead found: {lead_id}")
        print("Lead successfully updated in Firestore")
        print("New status:", updated_lead.get("status"))

        reply_text = (
            f"Hi {lead.get('name', '')}! Thanks for your response. "
            "I'm here to help with your property requirements. "
            "Could you tell me a little more about what you're looking to do?"
        )

    else:
        print(f"No lead found for phone number: {sender}")

        reply_text = (
            "Hello! Thanks for contacting our Real Estate team. "
            "Could you please share your name and property details?"
        )

    # Return TwiML so Twilio sends the response.
    twiml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<Response>"
        f"<Message><Body>{escape(reply_text)}</Body></Message>"
        "</Response>"
    )

    return Response(
        content=twiml,
        media_type="application/xml",
    )