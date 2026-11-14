from urllib.parse import parse_qs
from xml.sax.saxutils import escape

from app.services.conversation_service import (
    find_lead_by_phone,
    get_conversation_history,
    save_message,
)

from app.ai.lead_analyzer import analyze_lead
from app.services.lead_query_service import save_lead_ai_analysis


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

    # 1. Save the customer's incoming message.
    save_message(
        lead_id=lead_id,
        phone=sender,
        sender="customer",
        message=incoming_message,
    )

    try:
        # 2. Get the complete WhatsApp conversation.
        conversation_history = get_conversation_history(
            lead_id
        )

        # 3. Analyze the lead using both form and conversation data.
        analysis = analyze_lead(
            lead,
            conversation_history,
        )

        # 4. Save the AI analysis to Firestore.
        save_lead_ai_analysis(
            lead_id,
            analysis.model_dump(mode="json"),
        )

        print(
            f"AI analysis updated for lead {lead_id}"
        )

        # Temporary response based on successful analysis.
        reply_text = (
            f"Thanks, {lead.get('name', '')}! "
            "I've updated your property requirements. "
            "Our team will help you with the next steps."
        )

    except Exception as error:
        print(
            f"AI analysis failed for {lead_id}: {error}"
        )

        # The WhatsApp conversation should continue even if AI fails.
        reply_text = (
            "Thanks for sharing those details. "
            "Our team has received your response."
        )

    # Save the outgoing response.
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