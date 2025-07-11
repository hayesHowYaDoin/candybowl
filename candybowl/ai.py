import os
from typing import Optional

from google import genai


_client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
)


def send_message(message: str) -> Optional[str]:
    """Sends a message to the Gemini model and returns the response."""
    try:
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message,
        )

        return response.text

    except Exception as e:
        raise RuntimeError(f"Failed to generate content: {e}")
