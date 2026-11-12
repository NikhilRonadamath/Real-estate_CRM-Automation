import os

from groq import Groq

from app.core.config import settings


def generate_whatsapp_reply(
    lead: dict | None,
    incoming_message: str,
) -> str:
    """
    Generate a natural, helpful WhatsApp response based on
    the customer's message and available lead information.
    """

    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    client = Groq(api_key=settings.GROQ_API_KEY)

    # Use lead information when we recognize the sender.
    if lead:
        lead_context = f"""
Customer name: {lead.get("name", "Unknown")}
Property type: {lead.get("property_type", "Unknown")}
Location: {lead.get("location", "Unknown")}
Estimated value: {lead.get("estimated_value", "Not provided")}
Selling timeline: {lead.get("selling_timeline", "Not provided")}
Motivation: {lead.get("motivation", "Not provided")}
Current seller intent: {lead.get("seller_intent", "Unknown")}
"""
    else:
        lead_context = "No existing lead information is available."

    prompt = f"""
You are a friendly AI assistant for a real estate lead management team.

Your job is to communicate naturally with potential property sellers
through WhatsApp.

Customer information:
{lead_context}

The customer's latest WhatsApp message is:
"{incoming_message}"

Instructions:
- Reply naturally and professionally.
- Keep the response short and suitable for WhatsApp.
- Be helpful, not overly sales-focused.
- Ask at most one useful follow-up question when needed.
- Do not invent property details.
- If the customer wants to sell, understand their timeline and motivation.
- If they want a property valuation, explain that the team can help arrange one.
- Do not mention that you are using Groq or an API.

Return only the message that should be sent to the customer.
"""

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a concise and helpful real estate "
                    "WhatsApp assistant."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.7,
        max_tokens=200,
    )

    return response.choices[0].message.content.strip()