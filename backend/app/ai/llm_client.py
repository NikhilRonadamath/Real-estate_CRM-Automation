
import json
import os

from dotenv import load_dotenv

from app.core.config import BACKEND_DIR

load_dotenv(BACKEND_DIR / ".env", override=True)

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


def generate_structured_response(
    system_prompt: str,
    user_prompt: str,
    response_schema,
):
    """Generate and validate a structured response using Groq."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing from backend/.env")

    try:
        from groq import Groq
    except ImportError as error:
        raise RuntimeError(
            "Groq SDK is not installed. Run: pip install groq"
        ) from error

    client = Groq(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "lead_analysis",
                    "strict": False,
                    "schema": response_schema.model_json_schema(),
                },
            },
            temperature=0.2,
            max_completion_tokens=1200,
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("Groq returned an empty analysis response")

        # Parse JSON and validate against our existing Pydantic model.
        parsed_data = json.loads(content)

        return response_schema.model_validate(parsed_data)

    except json.JSONDecodeError as error:
        raise RuntimeError(
            "Groq returned invalid JSON for the lead analysis"
        ) from error

    finally:
        client.close()
