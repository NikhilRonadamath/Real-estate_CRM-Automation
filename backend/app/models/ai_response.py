from typing import Literal

from pydantic import BaseModel, Field


class AILeadAnalysis(BaseModel):
    seller_intent: Literal[
        "ready_to_sell",
        "exploring",
        "not_interested",
        "uncertain",
        "unknown",
    ]
    motivation_analysis: str
    selling_urgency: Literal["immediate", "high", "medium", "low", "unknown"]
    lead_score: int = Field(ge=0, le=100)
    qualification_summary: str
    missing_information: list[str]
    recommended_action: Literal[
        "schedule_valuation",
        "contact_seller",
        "request_property_details",
        "nurture_lead",
        "human_handoff",
        "no_action",
    ]
    recommendation_reason: str
    confidence: float = Field(ge=0, le=1)
