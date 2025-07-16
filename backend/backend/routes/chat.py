from typing import Literal, TypeAlias
import uuid

from flask import Blueprint, jsonify, request
from flask.wrappers import Response

from backend.ai.chat import (
    Chat,
    haggle_chat,
    restock_chat,
    request_chat,
    send_message,
)

bp = Blueprint("chat", __name__)

chats: dict[str, Chat] = {}

StatusCode: TypeAlias = (
    tuple[Response, Literal[200]]
    | tuple[Response, Literal[400]]
    | tuple[Response, Literal[404]]
    | tuple[Response, Literal[500]]
)


@bp.route(rule="/chat/request", methods=["GET"])
def request_item() -> StatusCode:
    """Starts a request session."""
    try:
        chat = request_chat()
        chat_id = str(uuid.uuid4())
        chats[chat_id] = chat

        return jsonify({"chat_id": chat_id}), 200

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@bp.route("/chat/haggle", methods=["GET"])
def haggle() -> StatusCode:
    """Starts a haggling session."""
    try:
        chat = haggle_chat()
        chat_id = str(uuid.uuid4())
        chats[chat_id] = chat

        return jsonify({"chat_id": chat_id}), 200

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@bp.route("/chat/restock", methods=["GET"])
def restock() -> StatusCode:
    """Starts a restocking session."""
    try:
        chat, response = restock_chat()
        chat_id = str(uuid.uuid4())
        chats[chat_id] = chat

        return jsonify({"chat_id": chat_id, "response": response}), 200

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@bp.route("/chat/message", methods=["POST"])
def message() -> StatusCode:
    """Sends a message to the chat and returns the response."""
    try:
        if request.json is None:
            return jsonify({"error": "Invalid request format"}), 400

        chat = chats.get(request.json.get("chat_id"))
        if not chat:
            return jsonify({"error": "Chat not found"}), 404

        message = request.json.get("message")
        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400

        response = send_message(chat, message)
        if not response:
            return jsonify(
                {"error": "Received empty response from the model"}
            ), 500

        return jsonify({"response": response}), 200

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500
