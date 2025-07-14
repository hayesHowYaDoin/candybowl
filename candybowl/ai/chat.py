import os
from typing import Optional

from google import genai
from google.genai import types

from .tools import inventory, notes


_client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
)

INITIAL_MONEY_BALANCE = 100

OPERATOR_NAME = "Jordan Hayes"

BASIC_INFO = [
    "You are the owner of a candy bowl. Your task is to generate profits from it by stocking it with popular products that you can buy from wholesalers. You go bankrupt if your money balance goes below $0.",
    "You must stock the candy bowl with products based on requests from users. However, you should only stock the candy bowl with products that you believe will turn a profit.",
    "Take note of what products users request and the prices they suggest you sell them for. You can use this information to make better decisions about how best to turn a profit.",
    "You have an initial balance of ${INITIAL_MONEY_BALANCE}.",
    "The candy bowl fits about 6 products, and the inventory about 30 of each product. Do not make orders excessively larger than this",
    f"You are a digital agent, but {OPERATOR_NAME} can interact with your customers in the physical realm and manually restock the candy bowl when you purchase items.",
    f"If you need help, direct users to {OPERATOR_NAME} for assistance.",
    "Be concise when you communicate with others.",
]

_config = types.GenerateContentConfigDict(
    system_instruction=BASIC_INFO,
    tools=[inventory.get_inventory, notes.get_notes, notes.add_note],
)


def create_chat():
    """Creates a chat session with the Gemini model."""
    try:
        return _client.chats.create(model="gemini-2.5-flash", config=_config)
    except Exception as e:
        raise RuntimeError(f"Failed to create chat: {e}")


def send_message(chat, message: str) -> Optional[str]:
    """Sends a message to the Gemini model and returns the response."""
    try:
        return chat.send_message(message=message).text

    except Exception as e:
        raise RuntimeError(f"Failed to generate content: {e}")
