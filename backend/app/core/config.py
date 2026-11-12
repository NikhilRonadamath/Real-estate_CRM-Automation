import os
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env", override=True)


class Settings:
    APP_NAME: str = os.getenv(
        "APP_NAME",
        "AI Lead Recovery Engine"
    )

    APP_VERSION: str = os.getenv(
        "APP_VERSION",
        "1.0.0"
    )

    FRONTEND_URL: str = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173"
    )

    FIREBASE_CREDENTIALS_PATH: str = os.getenv(
        "FIREBASE_CREDENTIALS_PATH",
        "firebase-service-account.json"
    )

    FIREBASE_CREDENTIALS: str = os.getenv(
        "FIREBASE_CREDENTIALS",
        os.getenv("FIREBASE_CREDENTIALS_PATH", "")
    )

    FIREBASE_PROJECT_ID: str = os.getenv(
        "FIREBASE_PROJECT_ID",
        ""
    )

    FIREBASE_COLLECTION: str = os.getenv(
        "FIREBASE_COLLECTION",
        "leads"
    )

    FIREBASE_SERVICE_ACCOUNT_JSON: str = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_JSON",
        ""
    )

    # Twilio WhatsApp
    TWILIO_ACCOUNT_SID: str = os.getenv(
        "TWILIO_ACCOUNT_SID",
        ""
    )

    TWILIO_AUTH_TOKEN: str = os.getenv(
        "TWILIO_AUTH_TOKEN",
        ""
    )

    TWILIO_WHATSAPP_FROM: str = os.getenv(
        "TWILIO_WHATSAPP_FROM",
        ""
    )
	GROQ_API_KEY: str = os.getenv(
   	 "GROQ_API_KEY",
   	 ""
	)

	GROQ_MODEL: str = os.getenv(
   	 "GROQ_MODEL",
   	 "openai/gpt-oss-20b"
	)


settings = Settings()