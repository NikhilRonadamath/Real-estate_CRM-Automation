from pathlib import Path

import google.auth
import requests
from dotenv import load_dotenv
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

from app.core.config import BACKEND_DIR, settings

load_dotenv(BACKEND_DIR / ".env")

SCOPES = ["https://www.googleapis.com/auth/datastore"]
DOCUMENTS_URL = (
	f"https://firestore.googleapis.com/v1/projects/{settings.FIREBASE_PROJECT_ID}"
	"/databases/(default)/documents"
)
DATABASE_URL = (
	f"https://firestore.googleapis.com/v1/projects/{settings.FIREBASE_PROJECT_ID}"
	"/databases/(default)"
)


class FirestoreNotFoundError(RuntimeError):
	"""Raised when a requested Firestore document does not exist."""


def _credentials_path() -> Path:
	configured_path = settings.FIREBASE_CREDENTIALS or "firebase-service-account.json"
	path = Path(configured_path)
	return path if path.is_absolute() else BACKEND_DIR / path


def _authorized_session() -> AuthorizedSession:
	"""Use a configured key file when present, otherwise Google ADC (keyless)."""
	path = _credentials_path()
	if path.is_file() and path.stat().st_size > 0:
		credentials = service_account.Credentials.from_service_account_file(
			str(path), scopes=SCOPES
		)
	else:
		credentials, _ = google.auth.default(scopes=SCOPES)
	return AuthorizedSession(credentials)


def firestore_request(method: str, url: str, **kwargs) -> requests.Response:
	if not settings.FIREBASE_PROJECT_ID:
		raise RuntimeError("FIREBASE_PROJECT_ID is not configured in backend/.env.")
	with _authorized_session() as session:
		response = session.request(method, url, timeout=15, **kwargs)
	if not response.ok:
		try:
			error_message = response.json().get("error", {}).get("message", "")
		except (ValueError, AttributeError):
			error_message = ""
		message = f"Firestore REST request failed ({response.status_code})"
		if error_message:
			message += f": {error_message}"
		if response.status_code == 404:
			raise FirestoreNotFoundError(message)
		raise RuntimeError(message)
	return response


def check_firestore_connection() -> dict:
	"""Check auth, Firestore API access, and whether the DB uses Native Mode."""
	try:
		response = firestore_request("GET", DATABASE_URL)
		database_info = response.json()
		database_type = database_info.get("type", "UNKNOWN")
		if database_type != "FIRESTORE_NATIVE":
			return {
				"connected": False,
				"project_id": settings.FIREBASE_PROJECT_ID,
				"database_type": database_type,
				"message": (
					"This database is not in Firestore Native Mode. "
					"The Firestore document REST API cannot be used with Datastore Mode."
				),
			}
		return {
			"connected": True,
			"project_id": settings.FIREBASE_PROJECT_ID,
			"database_type": database_type,
			"database": "(default)",
			"message": "Firestore Native Mode connection successful.",
		}
	except google.auth.exceptions.DefaultCredentialsError as error:
		return {
			"connected": False,
			"project_id": settings.FIREBASE_PROJECT_ID,
			"message": (
				"No Google credentials are available. Configure organization-approved "
				"Application Default Credentials or a service identity."
			),
			"error": str(error),
		}
	except (requests.RequestException, RuntimeError, ValueError) as error:
		return {
			"connected": False,
			"project_id": settings.FIREBASE_PROJECT_ID,
			"message": "Unable to connect to Firestore. Check API access and IAM permissions.",
			"error": str(error),
		}
