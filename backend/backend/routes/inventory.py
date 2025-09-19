from typing import Literal, TypeAlias

from flask import Blueprint, jsonify
from flask.wrappers import Response

from backend.inventory import InventoryManagerCSV

bp = Blueprint("inventory", __name__)

StatusCode: TypeAlias = (
    tuple[Response, Literal[200]] | tuple[Response, Literal[500]]
)

_inventory_csv = "data/inventory.csv"


@bp.route("/api/inventory", methods=["GET"])
def get_inventory() -> StatusCode:
    """Returns the current inventory as JSON."""
    try:
        inventory_manager = InventoryManagerCSV(_inventory_csv)
        inventory_df = inventory_manager.get_inventory()

        # Convert DataFrame to list of dictionaries for JSON response
        inventory_data = inventory_df.to_dict("records")

        return jsonify({"inventory": inventory_data}), 200

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@bp.route("/api/purchase", methods=["POST"])
def purchase_item() -> StatusCode:
    """Handles item purchases by decreasing inventory quantity."""
    try:
        from flask import request

        if request.json is None:
            return jsonify({"error": "Invalid request format"}), 400

        item_id = request.json.get("item_id")
        quantity = request.json.get("quantity", 1)

        if not item_id:
            return jsonify({"error": "item_id is required"}), 400

        if quantity <= 0:
            return jsonify({"error": "quantity must be positive"}), 400

        inventory_manager = InventoryManagerCSV(_inventory_csv)
        inventory_df = inventory_manager.get_inventory()

        # Check if item exists
        item_row = inventory_df[inventory_df["item_id"] == item_id]
        if item_row.empty:
            return jsonify({"error": "Item not found"}), 404

        current_quantity = int(item_row.iloc[0]["quantity"])
        if current_quantity < quantity:
            return jsonify({"error": "Insufficient inventory"}), 400

        # Update quantity
        new_quantity = current_quantity - quantity
        inventory_manager._update_quantity(item_id, new_quantity)

        # Calculate total price
        unit_price = float(item_row.iloc[0]["sell_price_usd"])
        total_price = unit_price * quantity

        return jsonify(
            {
                "message": "Purchase successful",
                "item_id": item_id,
                "quantity_purchased": quantity,
                "total_price": total_price,
                "remaining_quantity": new_quantity,
            }
        ), 200

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500
