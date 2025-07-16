from loguru import logger

from backend.inventory import InventoryManagerCSV


_inventory_csv = "data/inventory.csv"


def get_inventory() -> str:
    """Retrieves a collection of all items currently in the inventory.

    Returns:
        A JSON string representation of the current inventory. The fields for each item are as follows:
            - item_id: Unique identifier for the item.
            - item_name: The name of the item.
            - link: A link for where to purchase the item.
            - quantity: The current quantity of the item in stock.
            - total_purchase_price_usd: The price of one of the item in USD (note that one item can have multiple units).
            - sell_price_usd: The price of a single unit of the item in USD.
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
    total_purchase_price_usd: float,
    sell_price_usd: float,
    description: str,
) -> str:
    """Adds new items to the inventory.

    Increases the quantity of a given item if it already exists in the inventory, or adds a new entry if it does not.

    Args:
        item_name: The name of the item.
        link: The link to the item.
        quantity: The quantity to add.
        total_purchase_price_usd: The price of one of the item in USD (note that one item can have multiple units).
        sell_price_usd: The price of a single unit of the item in USD.
        description: A description of the item.

    Returns:
        A message indicating success or failure.
    """
    logger.info(
        f"Adding new item to inventory:\n  item_name: {item_name}\n"
        f"  link: {link}\n  total_purchase_price_usd: {total_purchase_price_usd}\n  sell_price_usd: {sell_price_usd}\n  description: {description}"
    )

    try:
        inventory = InventoryManagerCSV(_inventory_csv)
        inventory.stock_item(
            item_name=item_name,
            link=link,
            quantity=quantity,
            total_purchase_price_usd=total_purchase_price_usd,
            sell_price_usd=sell_price_usd,
            description=description,
        )

        logger.info(f"Current inventory: {inventory.get_inventory().to_json()}")
        return "Item added successfully."

    except Exception as ex:
        logger.error(f"Error adding item: {ex}")
        return f"Error: {ex}"


def set_price(item_id: str, new_price_usd: float) -> str:
    """Sets a new price for an item in the inventory.
    Args:
        item_id: The unique identifier for the item.
        new_price_usd: The new price of the item in USD.
    Returns:
        A message indicating success or failure.
    """
    logger.info(f"Setting new price for item {item_id}: {new_price_usd} USD")

    try:
        inventory = InventoryManagerCSV(_inventory_csv)
        inventory.set_price(item_id=item_id, new_price_usd=new_price_usd)

        logger.info(f"Current inventory: {inventory.get_inventory().to_json()}")
        return "Price updated successfully."

    except Exception as ex:
        logger.error(f"Error updating price: {ex}")
        return f"Error: {ex}"
