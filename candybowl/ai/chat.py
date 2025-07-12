import os
from typing import Optional

from google import genai
from google.genai import types

from .tools import inventory


_client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
)

_personality_prompt = (
    "You are overseeing a candy bowl store front. Your job is to accept "
    "requests from users about what they would like to see in the candy "
    "bowl and purchase that candy. You are also responsible for setting "
    "the price users buy that candy at, and managing transactions from users "
    "that want to buy candy. You start with a budget of $100. Your goal is to "
    "make go the most money possible."
)


def create_chat():
    """Creates a chat session with the Gemini model."""
    try:
        return _client.chats.create(model="gemini-2.5-flash")
    except Exception as e:
        raise RuntimeError(f"Failed to create chat: {e}")


def initialize_chat(chat) -> Optional[str]:
    return send_message(chat, _personality_prompt)


def send_message(chat, message: str) -> Optional[str]:
    """Sends a message to the Gemini model and returns the response."""
    try:
        return chat.send_message(
            message=message,
            config=types.GenerateContentConfig(
                tools=[
                    inventory.get_inventory,
                    inventory.add_item,
                    # inventory.buy_item,
                    # inventory.sell_item,
                ],
            ),
        ).text

    except Exception as e:
        raise RuntimeError(f"Failed to generate content: {e}")
