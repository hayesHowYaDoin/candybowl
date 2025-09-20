from typing import Literal, TypeAlias
import uuid
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask.wrappers import Response

from backend.ai.chat import (
    Chat,
    haggle_chat,
    restock_chat,
    request_chat,
    send_message,
)
from backend.auth.jwt_auth import require_auth, require_admin
from backend.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionResponse,
    ChatStatusResponse,
    CleanupResponse,
)
from backend.utils.validation import validate_json

bp = Blueprint("chat", __name__)

# Chat sessions with timestamps for cleanup
chats: dict[str, dict] = {}

# Chat session expiry time (30 minutes)
CHAT_EXPIRY_MINUTES = 30

StatusCode: TypeAlias = (
    tuple[Response, Literal[200]]
    | tuple[Response, Literal[400]]
    | tuple[Response, Literal[404]]
    | tuple[Response, Literal[500]]
)


def cleanup_expired_chats():
    """Remove chat sessions older than CHAT_EXPIRY_MINUTES."""
    current_time = datetime.now()
    expired_ids = []

    for chat_id, session_data in chats.items():
        if current_time - session_data["created_at"] > timedelta(
            minutes=CHAT_EXPIRY_MINUTES
        ):
            expired_ids.append(chat_id)

    for chat_id in expired_ids:
        del chats[chat_id]

    return len(expired_ids)


def get_active_chat(chat_id: str) -> Chat | None:
    """Get an active chat session, cleaning up expired ones first."""
    cleanup_expired_chats()
    session_data = chats.get(chat_id)
    return session_data["chat"] if session_data else None


@bp.route(rule="/chat/request", methods=["GET"])
@require_auth
def request_item() -> StatusCode:
    """Starts a request session."""
    try:
        # Clean up expired chats before creating new one
        cleanup_expired_chats()

        chat = request_chat()
        chat_id = str(uuid.uuid4())
        chats[chat_id] = {
            "chat": chat,
            "created_at": datetime.now(),
            "last_accessed": datetime.now(),
        }

        # Send welcome message
        welcome_message = "Hi! 🍬 I'm ready to help you request new items for the candy bowl. Tell me what treats you'd like to see added, and I'll evaluate whether they would be profitable and a good fit for our bowl. What would you like to request?"
        
        response_data = ChatSessionResponse(chat_id=chat_id, response=welcome_message)
        return jsonify(response_data.model_dump()), 200

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@bp.route("/chat/haggle", methods=["GET"])
@require_auth
def haggle() -> StatusCode:
    """Starts a haggling session."""
    try:
        # Clean up expired chats before creating new one
        cleanup_expired_chats()

        chat = haggle_chat()
        chat_id = str(uuid.uuid4())
        chats[chat_id] = {
            "chat": chat,
            "created_at": datetime.now(),
            "last_accessed": datetime.now(),
        }

        # Send welcome message
        welcome_message = "Hey there! 💰 Ready to negotiate? I'm here to discuss prices for items currently in the candy bowl. I'll try to get the best value for both of us, but I'm always open to reasonable offers. What item would you like to haggle over?"
        
        response_data = ChatSessionResponse(chat_id=chat_id, response=welcome_message)
        return jsonify(response_data.model_dump()), 200

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@bp.route("/chat/restock", methods=["GET"])
@require_auth
@require_admin
def restock() -> StatusCode:
    """Starts a restocking session."""
    try:
        # Clean up expired chats before creating new one
        cleanup_expired_chats()

        chat, response = restock_chat()
        chat_id = str(uuid.uuid4())
        chats[chat_id] = {
            "chat": chat,
            "created_at": datetime.now(),
            "last_accessed": datetime.now(),
        }

        response_data = ChatSessionResponse(chat_id=chat_id, response=response)
        return jsonify(response_data.model_dump()), 200

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@bp.route("/chat/message", methods=["POST"])
@require_auth
@validate_json(ChatMessageRequest)
def message() -> StatusCode:
    """Sends a message to the chat and returns the response."""
    try:
        validated_data: ChatMessageRequest = request.validated_data

        chat = get_active_chat(validated_data.chat_id)
        if not chat:
            return jsonify({"error": "Chat not found or expired"}), 404

        # Update last accessed time
        if validated_data.chat_id in chats:
            chats[validated_data.chat_id]["last_accessed"] = datetime.now()

        response = send_message(chat, validated_data.message)
        if not response:
            return jsonify(
                {"error": "Received empty response from the model"}
            ), 500

        response_data = ChatMessageResponse(response=response)
        return jsonify(response_data.model_dump()), 200

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@bp.route("/chat/status", methods=["GET"])
@require_auth
@require_admin
def chat_status() -> StatusCode:
    """Returns information about active chat sessions."""
    try:
        # Clean up expired chats first
        expired_count = cleanup_expired_chats()

        active_sessions = []
        current_time = datetime.now()

        for chat_id, session_data in chats.items():
            age_minutes = (
                current_time - session_data["created_at"]
            ).total_seconds() / 60
            last_active_minutes = (
                current_time - session_data["last_accessed"]
            ).total_seconds() / 60

            active_sessions.append(
                {
                    "chat_id": chat_id,
                    "age_minutes": round(age_minutes, 2),
                    "last_active_minutes": round(last_active_minutes, 2),
                }
            )

        response_data = ChatStatusResponse(
            active_sessions=len(chats),
            sessions_cleaned=expired_count,
            expiry_minutes=CHAT_EXPIRY_MINUTES,
            sessions=active_sessions,
        )
        return jsonify(response_data.model_dump()), 200

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@bp.route("/chat/<chat_id>/close", methods=["DELETE"])
@require_auth
def close_chat(chat_id: str) -> StatusCode:
    """Close a specific chat session."""
    try:
        if chat_id in chats:
            del chats[chat_id]
            return jsonify({"message": "Chat session closed"}), 200
        else:
            return jsonify({"error": "Chat session not found"}), 404

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@bp.route("/chat/cleanup", methods=["POST"])
@require_auth
@require_admin
def manual_cleanup() -> StatusCode:
    """Manually trigger cleanup of expired chat sessions."""
    try:
        expired_count = cleanup_expired_chats()

        response_data = CleanupResponse(
            message=f"Cleaned up {expired_count} expired chat sessions",
            active_sessions=len(chats),
        )
        return jsonify(response_data.model_dump()), 200

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500
