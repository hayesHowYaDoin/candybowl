import os
import uuid

import pandas as pd


class InventoryManagerCSV:
    def __init__(self, csv_file: str):
        """Initializes the InventoryManager with a CSV file."""
        self.csv_filepath = csv_file
        self._initialize_csv()

    def _initialize_csv(self):
        """Ensures the CSV file exists with the correct header."""
        if not os.path.exists(self.csv_filepath):
            pd.DataFrame(
                columns=[
                    "item_id",
                    "item_name",
                    "link",
                    "quantity",
                    "price_usd",
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

    def add_item(
        self,
        item_name: str,
        link: str,
        price_usd: float,
        description: str,
    ) -> None:
        """Adds a new item to the inventory."""
        inventory = self.get_inventory()
        if not inventory[
            (inventory["item_name"] == item_name) | (inventory["link"] == link)
        ].empty:
            raise ValueError(
                "An item with the same name or link already exists."
            )

        new_row = {
            "item_id": str(uuid.uuid4()),
            "item_name": item_name,
            "link": link,
            "quantity": 0,
            "price_usd": price_usd,
            "description": description,
        }

        inventory = pd.concat(
            [
                inventory,
                pd.DataFrame([new_row]),
            ],
            ignore_index=True,
        )

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

    def buy_item(self, item_id: str, quantity: int) -> None:
        """Buys an item, increasing its quantity in the inventory."""
        inventory = self._get_all_items()
        if item_id not in inventory["item_id"].values:
            raise ValueError(f"Item with ID {item_id} does not exist.")

        current_quantity = inventory.loc[
            inventory["item_id"] == item_id, "quantity"
        ].values[0]
        new_quantity = current_quantity + quantity
        self._update_quantity(item_id, new_quantity)

    def sell_item(self, item_id: str, quantity: int) -> None:
        """Sells an item, decreasing its quantity in the inventory."""
        inventory = self._get_all_items()
        if item_id not in inventory["item_id"].values:
            raise ValueError(f"Item with ID {item_id} does not exist.")

        current_quantity = inventory.loc[
            inventory["item_id"] == item_id, "quantity"
        ].values[0]
        if current_quantity < quantity:
            raise ValueError("Not enough quantity to sell.")

        new_quantity = current_quantity - quantity
        self._update_quantity(item_id, new_quantity)
