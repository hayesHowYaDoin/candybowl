import os
from typing import Literal, TypeAlias
from flask import Blueprint, jsonify, request
from flask.wrappers import Response
import stripe

from backend.auth.jwt_auth import require_auth
from backend.schemas.payments import (
    CreatePaymentIntentRequest,
    ConfirmPaymentRequest,
)
from backend.utils.validation import validate_json

bp = Blueprint("payments", __name__)

StatusCode: TypeAlias = (
    tuple[Response, Literal[200]]
    | tuple[Response, Literal[400]]
    | tuple[Response, Literal[500]]
)

# Initialize Stripe with secret key from environment
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


@bp.route("/api/payments/create-intent", methods=["POST"])
@require_auth
@validate_json(CreatePaymentIntentRequest)
def create_payment_intent() -> StatusCode:
    """Create a Stripe payment intent for the given amount."""
    try:
        validated_data: CreatePaymentIntentRequest = request.validated_data
        amount_cents = int(validated_data.amount * 100)  # Convert to cents

        if amount_cents < 50:  # Stripe minimum amount
            return jsonify({"error": "Minimum payment amount is $0.50"}), 400

        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="usd",
            automatic_payment_methods={
                "enabled": True,
            },
            metadata={
                "user_id": request.current_user["user_id"],
                "username": request.current_user["username"],
            },
        )

        return jsonify(
            {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
            }
        ), 200

    except stripe.error.StripeError as e:
        return jsonify({"error": f"Stripe error: {str(e)}"}), 400
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@bp.route("/api/payments/confirm", methods=["POST"])
@require_auth
@validate_json(ConfirmPaymentRequest)
def confirm_payment() -> StatusCode:
    """Confirm a payment and process the order."""
    try:
        validated_data: ConfirmPaymentRequest = request.validated_data

        # Retrieve the payment intent from Stripe
        intent = stripe.PaymentIntent.retrieve(validated_data.payment_intent_id)

        if intent.status != "succeeded":
            return jsonify(
                {"error": "Payment not completed", "status": intent.status}
            ), 400

        # TODO: Process the order here
        # - Deduct inventory quantities
        # - Create order record
        # - Send confirmation email

        current_user = request.current_user

        return jsonify(
            {
                "message": "Payment confirmed successfully",
                "payment_intent_id": intent.id,
                "amount": intent.amount / 100,  # Convert back to dollars
                "user": current_user["username"],
            }
        ), 200

    except stripe.error.StripeError as e:
        return jsonify({"error": f"Stripe error: {str(e)}"}), 400
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@bp.route("/api/webhooks/stripe", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        if endpoint_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        else:
            # For development without webhook secret
            event = stripe.Event.construct_from(
                request.get_json(), stripe.api_key
            )
    except ValueError:
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({"error": "Invalid signature"}), 400

    # Handle the event
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        print(f"Payment succeeded: {payment_intent['id']}")

        # TODO: Update order status, send confirmation email, etc.

    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        print(f"Payment failed: {payment_intent['id']}")

        # TODO: Handle failed payment

    else:
        print(f"Unhandled event type: {event['type']}")

    return jsonify({"received": True}), 200
