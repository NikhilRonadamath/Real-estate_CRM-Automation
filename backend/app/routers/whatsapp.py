from urllib.parse import parse_qs
from xml.sax.saxutils import escape

from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.services.lead_service import find_lead_by_phone
from app.services.whatsapp_ai_service import generate_whatsapp_reply


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

    # Find the lead associated with the WhatsApp number.
    lead = find_lead_by_phone(sender)

    if lead:
        print(
            f"Lead found: {lead.get('name')} "
            f"({lead.get('lead_id')})"
        )
    else:
        print("No existing lead found for this phone number.")

    try:
        # Generate a personalized AI response.
        reply_text = generate_whatsapp_reply(
            lead=lead,
            incoming_message=incoming_message,
        )

        print("AI response:", reply_text)

    except Exception as error:
        print(f"AI response generation failed: {error}")

        # Safe fallback if the AI service is unavailable.
        reply_text = (
            "Thanks for your message! Our team has received it "
            "and will get back to you shortly."
        )

    # Send the response back through Twilio using TwiML.
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