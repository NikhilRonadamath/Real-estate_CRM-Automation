from urllib.parse import parse_qs
from xml.sax.saxutils import escape

from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.services.lead_service import find_lead_by_phone


router = APIRouter(
    prefix="/api/whatsapp",
    tags=["WhatsApp"],
)


@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    # Twilio sends incoming messages as form-encoded data.
    raw_body = await request.body()
    form_data = parse_qs(raw_body.decode("utf-8"))

    sender = form_data.get("From", [""])[0]
    incoming_message = form_data.get("Body", [""])[0]
    message_sid = form_data.get("MessageSid", [""])[0]

    print("Incoming WhatsApp message")
    print("Sender:", sender)
    print("Message:", incoming_message)
    print("Message SID:", message_sid)

    # Find the lead associated with this WhatsApp number.
    lead = find_lead_by_phone(sender)

    if lead:
        print(
            f"Lead found: {lead.get('name')} "
            f"({lead.get('lead_id')})"
        )

        reply_text = (
            f"Hi {lead.get('name')}! Thanks for your message. "
            "Our team is reviewing your property details."
        )
    else:
        print("No lead found for this WhatsApp number.")

        reply_text = (
            "Hello! Thanks for contacting our Real Estate team. "
            "How can we help you with your property today?"
        )

    # Return TwiML instructions to Twilio.
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