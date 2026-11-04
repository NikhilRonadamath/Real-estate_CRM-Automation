from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class LeadCreate(BaseModel):
	name: str = Field(min_length=2, max_length=100)
	email: EmailStr
	phone: str = Field(min_length=10, max_length=20)
	property_type: str = Field(min_length=2, max_length=50)
	location: str = Field(min_length=2, max_length=150)
	estimated_value: Optional[float] = Field(default=None, gt=0)
	selling_timeline: Optional[str] = Field(default=None, max_length=50)
	motivation: Optional[str] = Field(default=None, max_length=1000)
	preferred_channel: Optional[Literal["sms", "email", "whatsapp"]] = None
	sms_opt_in: bool = False
	email_opt_in: bool = False
	whatsapp_opt_in: bool = False
	outreach_consent: bool = False
	do_not_contact: bool = False


class LeadResponse(BaseModel):
	success: bool
	message: str
	lead_id: str


class LeadStatusUpdate(BaseModel):
	status: Literal["new", "contacted", "qualified", "follow_up", "recovered", "lost"]
