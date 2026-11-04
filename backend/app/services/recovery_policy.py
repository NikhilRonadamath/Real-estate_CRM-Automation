from datetime import datetime, timezone, timedelta
from typing import Any

INACTIVITY_DAYS = 30
MAX_RECOVERY_ATTEMPTS = 3

ALLOWED_STATUSES = {"new", "contacted", "follow_up"}

CHANNEL_CONSENT = {
    "whatsapp": "whatsapp_opt_in"
}


def parse_datetime(value: Any):
    if not value:
        return None

    if isinstance(value, datetime):
        result = value
    elif isinstance(value, str):
        try:
            result = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError:
            return None
    else:
        return None

    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)

    return result.astimezone(timezone.utc)


def evaluate_lead(lead: dict, now: datetime | None = None):
    now = now or datetime.now(timezone.utc)

    reasons = []

    lead_id = lead.get("id") or lead.get("lead_id")
    channel = lead.get("preferred_channel")

    # 1. Status check
    if lead.get("status") not in ALLOWED_STATUSES:
        reasons.append("Lead status is not eligible")

    # 2. Opt-out check
    if lead.get("do_not_contact", False):
        reasons.append("Seller opted out of communication")

    # 3. Channel and consent check
    if channel not in CHANNEL_CONSENT:
        reasons.append("Invalid communication channel")
    else:
        consent_field = CHANNEL_CONSENT[channel]

        if not lead.get(consent_field, False):
            reasons.append("Missing explicit WhatsApp consent")

    if not lead.get("consent_source"):
        reasons.append("Missing consent source")

    if not parse_datetime(lead.get("consent_recorded_at")):
        reasons.append("Missing valid consent timestamp")

    # 4. Recovery attempt limit
    attempts = int(lead.get("recovery_attempts", 0) or 0)

    if attempts >= MAX_RECOVERY_ATTEMPTS:
        reasons.append("Maximum recovery attempts reached")

    # 5. AI processing check
    if not lead.get("ai_enabled", False):
        reasons.append("AI processing is disabled")

    ai_status = lead.get("ai_status", "ready")

    if ai_status in {
        "paused",
        "human_handoff",
        "completed",
        "do_not_contact"
    }:
        reasons.append(f"AI processing is {ai_status}")

    # 6. Next contact check
    next_contact = parse_datetime(
        lead.get("next_contact_at")
    )

    if next_contact and next_contact > now:
        reasons.append("Next contact time has not arrived")

    # 7. Inactivity check
    last_activity = (
        parse_datetime(lead.get("last_contacted_at"))
        or parse_datetime(lead.get("created_at"))
    )

    if not last_activity:
        reasons.append("Missing valid lead activity date")

    elif now - last_activity < timedelta(
        days=INACTIVITY_DAYS
    ):
        reasons.append("Lead has not been inactive long enough")

    return {
        "lead_id": lead_id,
        "name": lead.get("name"),
        "channel": channel,
        "eligible": len(reasons) == 0,
        "reasons": reasons,
        "recovery_attempts": attempts
    }