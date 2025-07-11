import os
from typing import Optional

from google import genai


_client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
)


def create_chat():
    """Creates a chat session with the Gemini model."""
    try:
        return _client.chats.create(model="gemini-2.5-flash")
    except Exception as e:
        raise RuntimeError(f"Failed to create chat: {e}")


def send_message(chat, message: str) -> Optional[str]:
    """Sends a message to the Gemini model and returns the response."""
    try:
        return chat.send_message(message).text

    except Exception as e:
        raise RuntimeError(f"Failed to generate content: {e}")
