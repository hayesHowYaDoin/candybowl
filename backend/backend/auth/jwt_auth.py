import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from typing import Optional, Dict, Any

from .models import User, UserManager


def get_jwt_secret() -> str:
    """Get JWT secret from environment or generate a default one."""
    secret = os.getenv("JWT_SECRET")
    if not secret:
        # In production, this should be a secure random value
        secret = "candybowl-default-secret-change-in-production"
    return secret


def generate_token(user: User) -> str:
    """Generate JWT token for user."""
    payload = {
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role.value,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm="HS256")


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get current user from request context."""
    return getattr(request, "current_user", None)


def require_auth(f):
    """Decorator to require authentication for an endpoint."""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify(
                {"error": "Authorization header must start with Bearer"}
            ), 401

        token = auth_header.replace("Bearer ", "")

        if not token:
            return jsonify({"error": "Token required"}), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Verify user still exists and is active
        user_manager = UserManager()
        user = user_manager.get_user_by_id(payload["user_id"])
        if not user or not user.is_active:
            return jsonify({"error": "User account is inactive"}), 401

        # Add user info to request context
        request.current_user = {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.value,
        }

        return f(*args, **kwargs)

    return decorated


def require_admin(f):
    """Decorator to require admin role for an endpoint."""

    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = get_current_user()

        if not current_user:
            return jsonify({"error": "Authentication required"}), 401

        if current_user.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403

        return f(*args, **kwargs)

    return decorated


def optional_auth(f):
    """Decorator for optional authentication (adds user info if present)."""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            payload = verify_token(token)

            if payload:
                user_manager = UserManager()
                user = user_manager.get_user_by_id(payload["user_id"])
                if user and user.is_active:
                    request.current_user = {
                        "user_id": user.user_id,
                        "username": user.username,
                        "role": user.role.value,
                    }

        return f(*args, **kwargs)

    return decorated
