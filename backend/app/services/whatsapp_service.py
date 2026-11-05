from twilio.rest import Client

from app.core.config import settings


def format_whatsapp_number(phone: str) -> str:
    """Format a phone number for Twilio WhatsApp."""

    phone = phone.strip()

    if phone.startswith("whatsapp:"):
        return phone

    return f"whatsapp:{phone}"


def send_welcome_message(name: str, phone: str) -> dict:
    """Send an automatic WhatsApp message to a new lead."""

    if not all(
        [
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
            settings.TWILIO_WHATSAPP_FROM,
        ]
    ):
        raise RuntimeError(
            "Twilio WhatsApp credentials are not fully configured."
        )

    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN,
    )

    message_body = (
        f"Hi {name}! 👋\n\n"
        "Thank you for contacting our Real Estate team. "
        "We have received your property details.\n\n"
        "Our team is here to help you with your property journey. "
        "What would you like to know or discuss about your property?"
    )

    message = client.messages.create(
        from_=settings.TWILIO_WHATSAPP_FROM,
        to=format_whatsapp_number(phone),
        body=message_body,
    )

    return {
        "message_sid": message.sid,
        "status": message.status,
    }