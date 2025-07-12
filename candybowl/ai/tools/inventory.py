from typing import Optional

from loguru import logger

from candybowl.inventory import InventoryManagerCSV


_inventory_csv = "data/inventory.csv"


def get_inventory() -> str:
    """Returns the inventory as a DataFrame."""
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


def add_item(
    item_name: str,
    link: str,
    price_usd: float,
    description: str,
) -> Optional[str]:
    """Adds a new item to the inventory."""
    logger.info(
        f"Adding new item to inventory:\n  item_name: {item_name}\n"
        f"  link: {link}\n  price_usd: {price_usd}\n  description: {description}"
    )

    try:
        InventoryManagerCSV(_inventory_csv).add_item(
            item_name=item_name,
            link=link,
            price_usd=price_usd,
            description=description,
        )
    except Exception as ex:
        logger.error(f"Error adding item: {ex}")
        return f"Error: {ex}"


def buy_item(item_id: str, quantity: int) -> Optional[str]:
    """Allows the model to purchase items to increase inventory in exchange for currency."""
    logger.info(
        f"Buying item to increase inventory:\n  item_id: {item_id}\n  quantity: {quantity}"
    )
    try:
        InventoryManagerCSV(_inventory_csv).buy_item(
            item_id=item_id, quantity=quantity
        )
    except Exception as ex:
        logger.error(f"Error buying item: {ex}")
        return f"Error: {ex}"


def sell_item(item_id: str, quantity: int) -> Optional[str]:
    """Allows the model to sell items to users to decrease inventory in exchange for currency."""
    logger.info(
        f"Selling item to decrease inventory:\n  item_id: {item_id}\n  quantity: {quantity}"
    )

    try:
        InventoryManagerCSV(_inventory_csv).sell_item(
            item_id=item_id, quantity=quantity
        )
    except Exception as ex:
        logger.error(f"Error selling item: {ex}")
        return f"Error: {ex}"
