import os

from google import genai


_client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
)


def get_client() -> genai.Client:
    """Returns the Google GenAI client."""
    if _client is None:
        raise ValueError("Google GenAI client is not initialized.")
    return _client
