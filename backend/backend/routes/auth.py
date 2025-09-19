from typing import Literal, TypeAlias
import re
from flask import Blueprint, request, jsonify
from flask.wrappers import Response

from backend.auth.models import UserManager, UserRole
from backend.auth.jwt_auth import generate_token, require_auth, require_admin

bp = Blueprint("auth", __name__)

StatusCode: TypeAlias = (
    tuple[Response, Literal[200]]
    | tuple[Response, Literal[201]]
    | tuple[Response, Literal[400]]
    | tuple[Response, Literal[401]]
    | tuple[Response, Literal[403]]
    | tuple[Response, Literal[409]]
    | tuple[Response, Literal[500]]
)

user_manager = UserManager()


def validate_email(email: str) -> bool:
    """Basic email validation."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"

    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter"

    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number"

    return True, ""


def validate_username(username: str) -> tuple[bool, str]:
    """Validate username."""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"

    if len(username) > 20:
        return False, "Username must be no more than 20 characters long"

    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return (
            False,
            "Username can only contain letters, numbers, and underscores",
        )

    return True, ""


@bp.route("/auth/register", methods=["POST"])
def register() -> StatusCode:
    """Register a new user."""
    try:
        if request.json is None:
            return jsonify({"error": "Invalid request format"}), 400

        username = request.json.get("username", "").strip()
        email = request.json.get("email", "").strip()
        password = request.json.get("password", "")

        # Validation
        if not all([username, email, password]):
            return jsonify(
                {"error": "Username, email, and password are required"}
            ), 400

        # Validate username
        username_valid, username_error = validate_username(username)
        if not username_valid:
            return jsonify({"error": username_error}), 400

        # Validate email
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400

        # Validate password
        password_valid, password_error = validate_password(password)
        if not password_valid:
            return jsonify({"error": password_error}), 400

        # Check if username already exists
        if user_manager.get_user_by_username(username):
            return jsonify({"error": "Username already exists"}), 409

        # Check if email already exists
        try:
            import pandas as pd

            df = pd.read_csv(user_manager.csv_path)
            if not df[df["email"] == email].empty:
                return jsonify({"error": "Email already registered"}), 409
        except Exception:
            pass

        # Determine role - first user becomes admin
        is_first_user = user_manager.get_user_count() == 0
        role = UserRole.ADMIN if is_first_user else UserRole.USER

        # Create user
        user = user_manager.create_user(username, email, password, role)
        token = generate_token(user)

        return jsonify(
            {
                "message": "User registered successfully",
                "token": token,
                "user": {
                    "id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                    "is_first_user": is_first_user,
                },
            }
        ), 201

    except Exception as ex:
        return jsonify({"error": f"Registration failed: {str(ex)}"}), 500


@bp.route("/auth/login", methods=["POST"])
def login() -> StatusCode:
    """Login user with username and password."""
    try:
        if request.json is None:
            return jsonify({"error": "Invalid request format"}), 400

        username = request.json.get("username", "").strip()
        password = request.json.get("password", "")

        if not all([username, password]):
            return jsonify({"error": "Username and password are required"}), 400

        # Authenticate user
        user = user_manager.authenticate(username, password)
        if not user:
            return jsonify({"error": "Invalid username or password"}), 401

        # Generate token
        token = generate_token(user)

        return jsonify(
            {
                "message": "Login successful",
                "token": token,
                "user": {
                    "id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                },
            }
        ), 200

    except Exception as ex:
        return jsonify({"error": f"Login failed: {str(ex)}"}), 500


@bp.route("/auth/me", methods=["GET"])
@require_auth
def get_current_user() -> StatusCode:
    """Get current authenticated user info."""
    try:
        current_user = request.current_user
        user = user_manager.get_user_by_id(current_user["user_id"])

        if not user:
            return jsonify({"error": "User not found"}), 401

        return jsonify(
            {
                "user": {
                    "id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                    "created_at": user.created_at,
                }
            }
        ), 200

    except Exception as ex:
        return jsonify({"error": f"Failed to get user info: {str(ex)}"}), 500


@bp.route("/auth/users", methods=["GET"])
@require_auth
@require_admin
def list_users() -> StatusCode:
    """List all users (admin only)."""
    try:
        import pandas as pd

        df = pd.read_csv(user_manager.csv_path)

        users = []
        for _, row in df.iterrows():
            users.append(
                {
                    "id": row["user_id"],
                    "username": row["username"],
                    "email": row["email"],
                    "role": row["role"],
                    "created_at": row["created_at"],
                    "is_active": row["is_active"],
                }
            )

        return jsonify({"users": users, "total": len(users)}), 200

    except Exception as ex:
        return jsonify({"error": f"Failed to list users: {str(ex)}"}), 500


@bp.route("/auth/users/<user_id>/role", methods=["PUT"])
@require_auth
@require_admin
def update_user_role(user_id: str) -> StatusCode:
    """Update user role (admin only)."""
    try:
        if request.json is None:
            return jsonify({"error": "Invalid request format"}), 400

        new_role_str = request.json.get("role")
        if not new_role_str:
            return jsonify({"error": "Role is required"}), 400

        try:
            new_role = UserRole(new_role_str)
        except ValueError:
            return jsonify(
                {"error": "Invalid role. Must be 'user' or 'admin'"}
            ), 400

        # Check if user exists
        user = user_manager.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update role
        success = user_manager.update_user_role(user_id, new_role)
        if not success:
            return jsonify({"error": "Failed to update user role"}), 500

        return jsonify(
            {
                "message": f"User role updated to {new_role.value}",
                "user": {
                    "id": user_id,
                    "username": user.username,
                    "role": new_role.value,
                },
            }
        ), 200

    except Exception as ex:
        return jsonify({"error": f"Failed to update user role: {str(ex)}"}), 500


@bp.route("/auth/validate", methods=["POST"])
def validate_token() -> StatusCode:
    """Validate a JWT token."""
    try:
        if request.json is None:
            return jsonify({"error": "Invalid request format"}), 400

        token = request.json.get("token")
        if not token:
            return jsonify({"error": "Token is required"}), 400

        from backend.auth.jwt_auth import verify_token

        payload = verify_token(token)

        if not payload:
            return jsonify(
                {"valid": False, "error": "Invalid or expired token"}
            ), 401

        # Check if user still exists
        user = user_manager.get_user_by_id(payload["user_id"])
        if not user or not user.is_active:
            return jsonify(
                {"valid": False, "error": "User account is inactive"}
            ), 401

        return jsonify(
            {
                "valid": True,
                "user": {
                    "id": user.user_id,
                    "username": user.username,
                    "role": user.role.value,
                },
            }
        ), 200

    except Exception as ex:
        return jsonify({"valid": False, "error": str(ex)}), 500
