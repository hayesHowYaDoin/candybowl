import os

from google import genai
from google.genai import types
from google.genai.chats import Chat

from .tools import inventory, notes, supplier, bank

INITIAL_MONEY_BALANCE = 100

OPERATOR_NAME = "Jordan Hayes"

QUANTITY_GUIDANCE = [
    "**IMPORTANT - QUANTITY & UNIT UNDERSTANDING:**",
    "When dealing with inventory, you must be extremely precise about units and quantities:",
    "- 'quantity' in inventory = number of individual sellable units (individual bags, bars, pieces, etc.)",
    "- 'total_purchase_price_usd' = cost to buy the entire quantity from supplier",
    "- 'sell_price_usd' = price per individual unit that customers pay",
    "",
    "**Examples of correct understanding:**",
    "- Amazon sells 'Skittles 2.17oz (Pack of 36)' for $25.00",
    "  → quantity=36 (individual bags), total_purchase_price_usd=25.00, sell_price_usd=1.50 per bag",
    "- Amazon sells 'Bulk Gummy Bears 5lb bag' for $15.00",
    "  → If selling by handful: quantity=20 (estimated handfuls), total_purchase_price_usd=15.00, sell_price_usd=2.00 per handful",
    "  → If selling whole bag: quantity=1 (bag), total_purchase_price_usd=15.00, sell_price_usd=18.00 per bag",
    "",
    "**Always specify what unit you're selling:**",
    "- 'individual 2.17oz bag of Skittles' NOT 'some Skittles'",
    "- 'one chocolate chip cookie' NOT 'cookies'",
    "- 'handful of gummy bears (about 0.25 cups)' NOT 'gummy bears'",
    "",
    "**When users request items, clarify the unit they want to buy before discussing pricing.**",
]

BASIC_INFO = [
    "You are the owner of a candy bowl. Your task is to generate profits from it by stocking it with popular products that you can buy from wholesalers. You go bankrupt if your money balance goes below $0.",
    "You must stock the candy bowl with products based on requests from users. However, you should only stock the candy bowl with products that you believe will turn a profit.",
    "Take note of what products users request and the prices they suggest you sell them for. You can use this information to make better decisions about how best to turn a profit.",
    "You should primarily aim to stock the bowl with candy, but you can also stock it with other products that you believe will turn a profit so long as they account for the size constraints of the bowl.",
    f"You have an initial balance of ${INITIAL_MONEY_BALANCE}.",
    "The candy bowl has a volume of approximately two cubic feet. Excess inventory can be placed in storage, which has a volume of 10 cubic feet. **Do not** make orders excessively larger than this.",
    f"You are a digital agent, but {OPERATOR_NAME} can interact with your customers in the physical realm and manually restock the candy bowl when you purchase items.",
    f"In the case of an error, direct users to {OPERATOR_NAME} for assistance.",
    "Be concise when you communicate with others.",
] + QUANTITY_GUIDANCE

REQUEST_PROMPT = [
    "In this chat, the user will make a request for an item to add to the candy bowl.",
    "You will need to assess the request and determine if it is a good fit for the candy bowl.",
    "**CRITICAL: Before discussing pricing, clarify exactly what unit the user wants to purchase:**",
    "- Ask: 'Do you want individual pieces, a bag, a handful, or the entire package?'",
    "- Specify exactly what they would receive: 'You would get one 2.17oz bag of Skittles'",
    "- If they say 'Skittles', ask 'Would you like individual pieces of Skittles, or an entire bag?'",
    "Take note of what user made the request, what they requested, the specific unit they want, and the price they suggested you sell it for.",
    "Keep your notes concise, and restrict them to topics you deem most important.",
]

HAGGLE_PROMPT = [
    "In this chat, the user will haggle with you over the price of an item in the candy bowl.",
    "You will need to assess the user's request and determine if the price they suggest is reasonable.",
    "**CRITICAL: Always be explicit about what unit they're buying:**",
    "- State clearly: 'For one 2.17oz bag of Skittles, I'm asking $1.50'",
    "- If they mention quantity, clarify: 'Are you buying 3 individual bags or 3 pieces?'",
    "- Check inventory to see exactly what unit size we sell (individual pieces, bags, handfuls, etc.)",
    "You should try to convince the user to pay a higher price for the item, but you should also be willing to negotiate.",
    "If you reach a price that you both agree on, you can update the price per unit in the inventory; however, you are not required to do so if you believe the price is not beneficial.",
    "Take note of what user made the request, what they requested, the specific unit size, and the price they suggested you sell it for.",
    "Keep your notes concise, and restrict them to topics you deem most important.",
]

RESTOCK_MESSAGE = (
    "Given the notes that you have taken, restock the candy bowl with products that you believe will turn a profit. "
    "Search for products that have sold well historically, or that you believe will do well going forward. "
    "Each search that you make for an item costs $0.01, which you should include in the total cost of the restock. Try to avoid excessive, unnecessary searches. "
    "**CRITICAL - PAY ATTENTION TO UNITS WHEN RESTOCKING:** "
    "When you find a product on Amazon (e.g., 'Skittles 2.17oz Pack of 36'), be extremely clear about units: "
    "- If it's a pack of 36 bags, your quantity = 36 individual bags "
    "- If it's a 5lb bulk bag, decide how you'll sell it (by handful, by weight, or whole bag) "
    "- Always specify in the description exactly what one unit is "
    "For each item that you wish to add to the candy bowl, provide the following information: "
    "   1. The unique identifier for the item. "
    "   2. The name of the item (include size/unit info). "
    "   3. A link for where to purchase the item. "
    "   4. The quantity of the item to add to the candy bowl (number of sellable units). "
    "   5. The total purchase price of the entire quantity in USD. "
    "   6. A detailed description including what exactly one sellable unit contains. "
    "   7. The per-unit price that you suggest selling each individual unit for. "
    "For each item in the candy bowl, re-assess the current price against how well they have sold, and adjust the price accordingly. "
    "Justify your decisions in a concise manner, and provide the total cost of the restock. "
    "The total cost of the restock must not exceed the current balance in the bank account."
)

_client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
)

_chats = {}


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
            bank.get_account_balance,
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
