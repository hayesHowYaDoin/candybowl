import os
import uuid

from loguru import logger
import pandas as pd


class InventoryManagerCSV:
    def __init__(self, csv_file: str):
        """Initializes the InventoryManager with a CSV file."""
        self.csv_filepath = csv_file
        self._initialize_csv()

    def _initialize_csv(self):
        """Ensures the CSV file exists with the correct header."""
        if not os.path.exists(self.csv_filepath):
            os.makedirs(os.path.dirname(self.csv_filepath), exist_ok=True)
            pd.DataFrame(
                columns=[
                    "item_id",
                    "item_name",
                    "link",
                    "quantity",
                    "total_purchase_price_usd",
                    "sell_price_usd",
                    "description",
                ]
            ).to_csv(self.csv_filepath, index=False)

    def _get_all_items(self) -> pd.DataFrame:
        """Returns the inventory from the CSV file."""
        return pd.read_csv(
            self.csv_filepath, dtype={"id": str}
        )  # Ensure UUIDs are read as strings

    def _set_all_items(self, inventory: pd.DataFrame) -> None:
        """Saves the current inventory to the CSV file."""
        inventory.to_csv(self.csv_filepath, index=False)

    def get_inventory(self) -> pd.DataFrame:
        """Returns the inventory as a DataFrame."""
        return self._get_all_items()

    def _prune_inventory(self) -> None:
        """Removes items from the inventory that have a quantity of 0."""
        inventory = self._get_all_items()
        inventory = inventory[inventory["quantity"] > 0]
        self._set_all_items(inventory)

    def _update_quantity(self, item_id: str, new_quantity: int) -> None:
        """Updates the quantity of an item in the inventory."""
        if new_quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        inventory = self._get_all_items()
        if item_id not in inventory["item_id"].values:
            raise ValueError(f"Item with ID {item_id} does not exist.")

        inventory.loc[inventory["item_id"] == item_id, "quantity"] = (
            new_quantity
        )
        self._set_all_items(inventory)
        self._prune_inventory()

    def _add_item(
        self,
        item_id: str,
        quantity: int,
    ) -> None:
        """Adds stock for an item, increasing its quantity in the inventory."""
        inventory = self._get_all_items()
        if item_id not in inventory["item_id"].values:
            raise ValueError(f"Item with ID {item_id} does not exist.")

        current_quantity = inventory.loc[
            inventory["item_id"] == item_id, "quantity"
        ].values[0]
        new_quantity = current_quantity + quantity
        self._update_quantity(item_id, new_quantity)

    def stock_item(
        self,
        item_name: str,
        link: str,
        quantity: int,
        total_purchase_price_usd: float,
        sell_price_usd: float,
        description: str,
    ) -> None:
        """Adds new items to the inventory.

        Increases the quantity of a given item if it already exists in the inventory, or adds a new entry if it does not.

        Args:
            item_name: The name of the item.
            link: The link to the item.
            quantity: The quantity to add.
            total_purchase_price_usd: The price of one of the item in USD (note that one item can have multiple units).
            sell_price_usd: The price of a single unit of the item in USD.
            description: A description of the item.
        """
        inventory = self._get_all_items()
        if not inventory[
            (inventory["item_name"] == item_name) | (inventory["link"] == link)
        ].empty:
            logger.info(
                f"Item '{item_name}' already exists in inventory. Updating quantity..."
            )
            item_id = inventory[
                (inventory["item_name"] == item_name)
                | (inventory["link"] == link)
            ]["item_id"].values[0]
            self._add_item(item_id, quantity)

        new_row = {
            "item_id": str(uuid.uuid4()),
            "item_name": item_name,
            "link": link,
            "quantity": 0,
            "total_purchase_price_usd": total_purchase_price_usd,
            "sell_price_usd": sell_price_usd,
            "description": description,
        }

        inventory = pd.concat(
            [
                inventory,
                pd.DataFrame([new_row]),
            ],
            ignore_index=True,
        )
        self._set_all_items(inventory)

    def set_price(self, item_id: str, new_price_usd: float) -> None:
        """Sets the price of an item in the inventory.

        Args:
            item_id: The ID of the item to update.
            new_price_usd: The new price of the item in USD.
        """
        if new_price_usd < 0:
            raise ValueError("Price cannot be negative.")

        inventory = self._get_all_items()
        if item_id not in inventory["item_id"].values:
            raise ValueError(f"Item with ID {item_id} does not exist.")

        inventory.loc[inventory["item_id"] == item_id, "sell_price_usd"] = (
            new_price_usd
        )
        self._set_all_items(inventory)
