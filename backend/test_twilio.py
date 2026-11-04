import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)

message = client.messages.create(
    from_=os.getenv("TWILIO_WHATSAPP_FROM"),
    content_sid="HXb5b62575e6e4ff6129ad7c8efe1f983e",
    content_variables='{"1":"12/1","2":"3pm"}',
    to=os.getenv("TWILIO_WHATSAPP_TO")
)

print("Message SID:", message.sid)
print("Message Status:", message.status)