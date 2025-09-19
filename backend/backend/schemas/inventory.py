from pydantic import BaseModel, Field, field_validator
from typing import Optional


class PurchaseRequest(BaseModel):
    """Request model for purchasing items."""

    item_id: str = Field(
        ...,
        description="Unique identifier for the item to purchase",
        min_length=1,
    )
    quantity: int = Field(..., description="Number of items to purchase", gt=0)


class AddInventoryRequest(BaseModel):
    """Request model for adding new inventory items."""

    item_name: str = Field(
        ..., description="Name of the item", min_length=1, max_length=200
    )
    link: str = Field(
        ..., description="URL link for the item", min_length=1, max_length=500
    )
    quantity: int = Field(..., description="Initial quantity of the item", ge=0)
    purchase_price: float = Field(
        ..., description="Price paid to acquire the item", ge=0.0
    )
    sell_price: float = Field(
        ..., description="Price to sell the item for", gt=0.0
    )
    description: str = Field(
        ...,
        description="Description of the item",
        min_length=1,
        max_length=1000,
    )

    @field_validator("sell_price")
    @classmethod
    def validate_sell_price_greater_than_purchase(cls, v: float, info) -> float:
        if "purchase_price" in info.data and v <= info.data["purchase_price"]:
            raise ValueError("sell_price must be greater than purchase_price")
        return v


class UpdateInventoryRequest(BaseModel):
    """Request model for updating inventory items."""

    quantity: Optional[int] = Field(
        default=None, description="New quantity for the item", ge=0
    )
    sell_price: Optional[float] = Field(
        default=None, description="New sell price for the item", ge=0.0
    )
