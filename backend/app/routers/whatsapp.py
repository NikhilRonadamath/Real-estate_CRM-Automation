from urllib.parse import parse_qs
from xml.sax.saxutils import escape

from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.services.conversation_service import (
    find_lead_by_phone,
    save_message,
)


router = APIRouter(
    prefix="/api/whatsapp",
    tags=["WhatsApp"],
)


@router.post("/webhook")
async def whatsapp_webhook(request: Request):

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
        lead_id = lead["lead_id"]

        # Save the customer's message.
        save_message(
            lead_id=lead_id,
            phone=sender,
            sender="customer",
            message=incoming_message,
        )

        reply_text = (
            f"Thanks for your response, {lead.get('name', '')}! "
            "Our AI assistant is reviewing your property details."
        )

        # Save the AI response too.
        save_message(
            lead_id=lead_id,
            phone=sender,
            sender="ai",
            message=reply_text,
        )

    else:
        print(
            f"No lead found for WhatsApp number: {sender}"
        )

        reply_text = (
            "Hello! We could not find your lead information. "
            "Please submit the property form first."
        )

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