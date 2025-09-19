from loguru import logger

from backend.inventory import InventoryManagerCSV


_inventory_csv = "data/inventory.csv"


def get_inventory() -> str:
    """Retrieves a collection of all items currently in the inventory.

    Returns:
        A JSON string representation of the current inventory. The fields for each item are as follows:
            - item_id: Unique identifier for the item.
            - item_name: The name of the item (includes size/unit information).
            - link: A link for where to purchase the item.
            - quantity: The current quantity of individual sellable units in stock (e.g., 36 = 36 individual bags).
            - total_purchase_price_usd: The price paid to purchase this entire quantity from supplier.
            - sell_price_usd: The price charged to customers for ONE individual unit.
            - description: A description including exactly what one sellable unit contains.
            - unit_type: Type of unit (bag, box, piece, etc.).
            - unit_size: Size of each unit (2.17oz, 5lb, etc.).
            - package_count: Number of units in the original Amazon package.
            - selling_unit: Clear description of what customers receive (e.g., "individual 2.17oz bag").
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
    unit_type: str = "",
    unit_size: str = "",
    package_count: int = 0,
    selling_unit: str = "",
) -> str:
    """Adds new items to the inventory.

    Increases the quantity of a given item if it already exists in the inventory, or adds a new entry if it does not.

    Args:
        item_name: The name of the item (include size/unit info like "Skittles 2.17oz").
        link: The link to the item on supplier website (Amazon, etc.).
        quantity: The number of individual sellable units to add (e.g., 36 individual bags).
        total_purchase_price_usd: The total cost to purchase this entire quantity from supplier.
        sell_price_usd: The price to charge customers for ONE individual sellable unit.
        description: A detailed description including exactly what one sellable unit contains.
        unit_type: Type of unit (bag, box, piece, etc.) - extracted from Amazon listing.
        unit_size: Size of each unit (2.17oz, 5lb, etc.) - extracted from Amazon listing.
        package_count: Number of units in the original Amazon package - extracted from listing.
        selling_unit: Clear description of what customers receive (e.g., "individual 2.17oz bag").

    Returns:
        A message indicating success or failure.
    """
    logger.info(
        f"Adding new item to inventory:\n  item_name: {item_name}\n"
        f"  link: {link}\n  total_purchase_price_usd: {total_purchase_price_usd}\n  sell_price_usd: {sell_price_usd}\n  description: {description}"
    )

    try:
        inventory = InventoryManagerCSV(_inventory_csv)
        item_id = inventory.stock_item(
            item_name=item_name,
            link=link,
            quantity=quantity,
            total_purchase_price_usd=total_purchase_price_usd,
            sell_price_usd=sell_price_usd,
            description=description,
            unit_type=unit_type,
            unit_size=unit_size,
            package_count=package_count,
            selling_unit=selling_unit,
        )

        logger.info(f"Current inventory: {inventory.get_inventory().to_json()}")
        return f"Item added successfully with ID: {item_id}. Unit info: {selling_unit}"

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
