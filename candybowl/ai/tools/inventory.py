from loguru import logger

from candybowl.inventory import InventoryManagerCSV


_inventory_csv = "data/inventory.csv"


def get_inventory() -> str:
    """Retrieves a collection of all items currently in the inventory.

    Returns:
        A JSON string representation of the current inventory. The fields for each item are as follows:
            - item_id: Unique identifier for the item.
            - item_name: The name of the item.
            - link: A link for where to purchase the item.
            - quantity: The current quantity of the item in stock.
            - price_usd: The price of the item in USD.
            - description: A description of the item.
    """
    logger.info("Retrieving current inventory.")

    try:
        inventory = (
            InventoryManagerCSV(_inventory_csv).get_inventory().to_json()
        )

        logger.info(f"Current inventory: {inventory}")
        return inventory
    except Exception as e:
        logger.error(f"Error retrieving inventory: {e}")
        return f"Error: {e}"


def stock_item(
    item_name: str,
    link: str,
    quantity: int,
    price_usd: float,
    description: str,
) -> str:
    """Adds new items to the inventory.

    Increases the quantity of a given item if it already exists in the inventory, or adds a new entry if it does not.

    Args:
        item_name: The name of the item.
        link: The link to the item.
        quantity: The quantity to add.
        price_usd: The price of the item in USD.
        description: A description of the item.

    Returns:
        A message indicating success or failure.
    """
    logger.info(
        f"Adding new item to inventory:\n  item_name: {item_name}\n"
        f"  link: {link}\n  price_usd: {price_usd}\n  description: {description}"
    )

    try:
        inventory = InventoryManagerCSV(_inventory_csv)
        inventory.stock_item(
            item_name=item_name,
            link=link,
            quantity=quantity,
            price_usd=price_usd,
            description=description,
        )

        logger.info(f"Current inventory: {inventory.get_inventory().to_json()}")

        return "Item added successfully."
    except Exception as ex:
        logger.error(f"Error adding item: {ex}")
        return f"Error: {ex}"
