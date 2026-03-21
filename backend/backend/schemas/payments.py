from pydantic import BaseModel, Field
from typing import List


class CartItem(BaseModel):
    """Cart item for payment processing."""

    item_id: str = Field(
        ..., description="Unique identifier for the inventory item"
    )
    item_name: str = Field(..., description="Name of the item")
    quantity: int = Field(..., gt=0, description="Quantity being purchased")
    unit_price: float = Field(..., gt=0, description="Price per unit in USD")
    total_price: float = Field(
        ..., gt=0, description="Total price for this item"
    )


class CreatePaymentIntentRequest(BaseModel):
    """Request to create a Stripe payment intent."""

    amount: float = Field(..., gt=0, description="Total amount in USD")
    cart_items: List[CartItem] = Field(
        ..., min_length=1, description="Items being purchased"
    )

    def calculate_total(self) -> float:
        """Calculate total from cart items."""
        return sum(item.total_price for item in self.cart_items)


class ConfirmPaymentRequest(BaseModel):
    """Request to confirm a completed payment."""

    payment_intent_id: str = Field(..., description="Stripe payment intent ID")
    cart_items: List[CartItem] = Field(
        ..., min_length=1, description="Items being purchased"
    )


class PaymentIntentResponse(BaseModel):
    """Response containing payment intent details."""

    client_secret: str = Field(..., description="Client secret for frontend")
    payment_intent_id: str = Field(..., description="Payment intent ID")


class PaymentConfirmationResponse(BaseModel):
    """Response after payment confirmation."""

    message: str = Field(..., description="Success message")
    payment_intent_id: str = Field(..., description="Payment intent ID")
    amount: float = Field(..., description="Payment amount in USD")
    user: str = Field(..., description="Username who made the payment")
