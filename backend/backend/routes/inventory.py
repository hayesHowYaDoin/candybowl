from typing import Literal, TypeAlias

from flask import Blueprint, jsonify, request
from flask.wrappers import Response
import pandas as pd

from backend.inventory import InventoryManagerCSV
from backend.auth.jwt_auth import require_auth, require_admin
from backend.schemas.inventory import (
    PurchaseRequest,
    AddInventoryRequest,
    UpdateInventoryRequest,
)
from backend.utils.validation import validate_json

bp = Blueprint("inventory", __name__)

StatusCode: TypeAlias = (
    tuple[Response, Literal[200]] | tuple[Response, Literal[500]]
)

_inventory_csv = "data/inventory.csv"


@bp.route("/api/inventory", methods=["GET"])
@require_auth
def get_inventory() -> StatusCode:
    """Returns the current inventory as JSON."""
    try:
        inventory_manager = InventoryManagerCSV(_inventory_csv)
        inventory_df = inventory_manager.get_inventory()

        # Convert DataFrame to list of dictionaries for JSON response
        inventory_data = inventory_df.to_dict("records")

        # Clean up any NaN values that might still exist
        import math
        import numpy as np

        for item in inventory_data:
            for key, value in list(
                item.items()
            ):  # Use list() to avoid modification during iteration
                # Check multiple NaN conditions
                is_nan = False
                try:
                    if pd.isna(value):
                        is_nan = True
                    elif isinstance(value, float) and math.isnan(value):
                        is_nan = True
                    elif (
                        hasattr(value, "__class__")
                        and "numpy" in str(value.__class__)
                        and np.isnan(value)
                    ):
                        is_nan = True
                    elif str(value).lower() == "nan":
                        is_nan = True
                except (TypeError, AttributeError, ValueError):
                    pass

                if is_nan:
                    if key == "package_count":
                        item[key] = 0
                    else:
                        item[key] = ""

        return jsonify({"inventory": inventory_data}), 200

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@bp.route("/api/purchase", methods=["POST"])
@require_auth
@validate_json(PurchaseRequest)
def purchase_item() -> StatusCode:
    """Handles item purchases by decreasing inventory quantity."""
    try:
        validated_data: PurchaseRequest = request.validated_data
        item_id = validated_data.item_id
        quantity = validated_data.quantity

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

        # Get current user info
        current_user = request.current_user

        return jsonify(
            {
                "message": "Purchase successful",
                "item_id": item_id,
                "quantity_purchased": quantity,
                "total_price": total_price,
                "remaining_quantity": new_quantity,
                "purchased_by": current_user["username"],
            }
        ), 200

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@bp.route("/api/inventory", methods=["POST"])
@require_auth
@require_admin
@validate_json(AddInventoryRequest)
def add_inventory_item() -> StatusCode:
    """Add a new item to inventory (admin only)."""
    try:
        validated_data: AddInventoryRequest = request.validated_data
        item_name = validated_data.item_name
        link = validated_data.link
        quantity = validated_data.quantity
        purchase_price = validated_data.purchase_price
        sell_price = validated_data.sell_price
        description = validated_data.description

        inventory_manager = InventoryManagerCSV(_inventory_csv)

        # Use the existing stock_item method
        item_id = inventory_manager.stock_item(
            item_name=item_name,
            link=link,
            quantity=quantity,
            price=purchase_price,
            description=description,
        )

        # Update the sell price
        inventory_manager.set_price(item_id, sell_price)

        current_user = request.current_user

        return jsonify(
            {
                "message": "Item added successfully",
                "item_id": item_id,
                "item_name": item_name,
                "quantity": quantity,
                "purchase_price": purchase_price,
                "sell_price": sell_price,
                "added_by": current_user["username"],
            }
        ), 201

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@bp.route("/api/inventory/<item_id>", methods=["PUT"])
@require_auth
@require_admin
@validate_json(UpdateInventoryRequest)
def update_inventory_item(item_id: str) -> StatusCode:
    """Update an existing inventory item (admin only)."""
    try:
        validated_data: UpdateInventoryRequest = request.validated_data

        inventory_manager = InventoryManagerCSV(_inventory_csv)
        inventory_df = inventory_manager.get_inventory()

        # Check if item exists
        item_row = inventory_df[inventory_df["item_id"] == item_id]
        if item_row.empty:
            return jsonify({"error": "Item not found"}), 404

        updates_made = []

        # Update quantity if provided
        if validated_data.quantity is not None:
            inventory_manager._update_quantity(item_id, validated_data.quantity)
            updates_made.append(f"quantity: {validated_data.quantity}")

        # Update sell price if provided
        if validated_data.sell_price is not None:
            inventory_manager.set_price(item_id, validated_data.sell_price)
            updates_made.append(f"sell_price: ${validated_data.sell_price:.2f}")

        current_user = request.current_user

        return jsonify(
            {
                "message": f"Item updated: {', '.join(updates_made)}",
                "item_id": item_id,
                "updated_by": current_user["username"],
            }
        ), 200

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@bp.route("/api/inventory/<item_id>", methods=["DELETE"])
@require_auth
@require_admin
def delete_inventory_item(item_id: str) -> StatusCode:
    """Delete an inventory item (admin only)."""
    try:
        inventory_manager = InventoryManagerCSV(_inventory_csv)
        inventory_df = inventory_manager.get_inventory()

        # Check if item exists
        item_row = inventory_df[inventory_df["item_id"] == item_id]
        if item_row.empty:
            return jsonify({"error": "Item not found"}), 404

        item_name = item_row.iloc[0]["item_name"]

        # Remove item by setting quantity to 0 (soft delete approach)
        inventory_manager._update_quantity(item_id, 0)

        current_user = request.current_user

        return jsonify(
            {
                "message": f"Item '{item_name}' removed from inventory",
                "item_id": item_id,
                "removed_by": current_user["username"],
            }
        ), 200

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500
