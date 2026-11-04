from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.integrations.firebase import check_firestore_connection
from app.routers import ai, leads, recovery, whatsapp
app = FastAPI(
	title=settings.APP_NAME,
	description="Real Estate AI Lead Recovery Engine API",
	version=settings.APP_VERSION,
)
app.include_router(whatsapp.router)
app.add_middleware(
	CORSMiddleware,
	allow_origins=list(
		dict.fromkeys(
			[
				settings.FRONTEND_URL,
				"http://127.0.0.1:5173",
				"http://localhost:5174",
				"http://127.0.0.1:5174",
			]
		)
	),
	allow_credentials=True,
	allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
	allow_headers=["Content-Type", "Authorization"],
)

app.include_router(leads.router)
app.include_router(recovery.router)
app.include_router(ai.router)


@app.get("/")
def root():
	return {
		"application": settings.APP_NAME,
		"version": settings.APP_VERSION,
		"status": "running",
	}


@app.get("/api/health")
def health():
	return {"status": "healthy"}


@app.get("/api/firebase-health")
def firebase_health():
	return check_firestore_connection()
