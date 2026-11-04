import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env", override=True)
FIREBASE_SERVICE_ACCOUNT_JSON: str = os.getenv(
    "FIREBASE_SERVICE_ACCOUNT_JSON", ""
)

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "AI Lead Recovery Engine")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
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

    # Add this for Render deployment
    FIREBASE_SERVICE_ACCOUNT_JSON: str = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_JSON",
        ""
    )


settings = Settings()