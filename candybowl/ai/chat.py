import os

from google import genai
from google.genai import types
from google.genai.chats import Chat

from .tools import inventory, notes, supplier


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

REQUEST_PROMPT = [
    "In this chat, the user will make a request for an item to add to the candy bowl.",
    "You will need to assess the request and determine if it is a good fit for the candy bowl.",
    "Take note of what user made the request, what they requested, and the price they suggested you sell it for.",
]

HAGGLE_PROMPT = [
    "In this chat, the user will haggle with you over the price of an item in the candy bowl.",
    "You will need to assess the user's request and determine if the price they suggest is reasonable.",
    "You should try to convince the user to pay a higher price for the item, but you should also be willing to negotiate.",
    "If you reach a price that you both agree on, you can update the price per unit in the inventory; however, you are not required to do so if you believe the price is not beneficial.",
]

RESTOCK_MESSAGE = (
    "Given the notes that you have taken, restock the candy bowl with products that you believe will turn a profit."
    "Search for products that have sold well historically, or that you believe will do well going forward."
    "For each item that you wish to add to the candy bowl, provide the link to the product, the quantity you wish to purchase, and the price you will sell it for."
    "For each item in the candy bowl, re-assess the current price against how well they have sold, and adjust the price accordingly."
    "Justify your decisions in a concise manner, and provide the total cost of the restock."
)


def request_chat() -> Chat:
    """Returns a chat session with the Gemini model about making a request for the candy bowl."""
    config = types.GenerateContentConfigDict(
        system_instruction=BASIC_INFO + REQUEST_PROMPT,
        tools=[inventory.get_inventory, notes.get_notes, notes.add_note],
    )

    try:
        return _client.chats.create(model="gemini-2.5-flash", config=config)

    except Exception as e:
        raise RuntimeError(f"Failed to create chat: {e}")


def haggle_chat() -> Chat:
    """Returns a chat session with the Gemini model about haggling over prices."""
    config = types.GenerateContentConfigDict(
        system_instruction=BASIC_INFO + HAGGLE_PROMPT,
        tools=[
            inventory.get_inventory,
            inventory.set_price,
            notes.get_notes,
            notes.add_note,
        ],
    )

    try:
        return _client.chats.create(model="gemini-2.5-flash", config=config)

    except Exception as e:
        raise RuntimeError(f"Failed to create chat: {e}")


def restock_chat() -> tuple[Chat, str]:
    """Returns chat session with the Gemini model about restocking the candy bowl with the initial response to the prompt."""
    config = types.GenerateContentConfigDict(
        system_instruction=BASIC_INFO,
        tools=[
            inventory.get_inventory,
            notes.get_notes,
            supplier.search_product,
        ],
    )

    try:
        chat = _client.chats.create(model="gemini-2.5-flash", config=config)
        response = send_message(chat, RESTOCK_MESSAGE)
        return chat, response

    except Exception as e:
        raise RuntimeError(f"Failed to create chat: {e}")


def send_message(chat, message: str) -> str:
    """Sends a message to the Gemini model and returns the response."""
    try:
        response = chat.send_message(message=message).text
        if response is None:
            raise ValueError("Received empty response from the model.")

        return response

    except Exception as e:
        raise RuntimeError(f"Failed to generate content: {e}")
