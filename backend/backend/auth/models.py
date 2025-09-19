from enum import Enum
from dataclasses import dataclass, asdict
from typing import Optional
import pandas as pd
import hashlib
import uuid
import os
from datetime import datetime


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"


@dataclass
class User:
    user_id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    created_at: str
    is_active: bool = True

    def to_dict(self) -> dict:
        """Convert user to dictionary for JSON serialization."""
        data = asdict(self)
        data["role"] = self.role.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create user from dictionary."""
        data["role"] = UserRole(data["role"])
        return cls(**data)


class UserManager:
    def __init__(self, csv_path: str = "backend/data/users.csv"):
        self.csv_path = csv_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create users CSV file if it doesn't exist."""
        if not os.path.exists(self.csv_path):
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            # Create empty DataFrame with proper columns
            empty_df = pd.DataFrame(
                columns=[
                    "user_id",
                    "username",
                    "email",
                    "password_hash",
                    "role",
                    "created_at",
                    "is_active",
                ]
            )
            empty_df.to_csv(self.csv_path, index=False)

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 (in production, use bcrypt)."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        return self._hash_password(password) == password_hash

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: UserRole = UserRole.USER,
    ) -> User:
        """Create a new user and save to CSV."""
        user_id = str(uuid.uuid4())
        password_hash = self._hash_password(password)
        created_at = datetime.now().isoformat()

        user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            created_at=created_at,
            is_active=True,
        )

        # Load existing users
        df = pd.read_csv(self.csv_path)

        # Add new user
        new_row = pd.DataFrame([user.to_dict()])
        df = pd.concat([df, new_row], ignore_index=True)

        # Save back to CSV
        df.to_csv(self.csv_path, index=False)

        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        try:
            df = pd.read_csv(self.csv_path)
            user_row = df[df["username"] == username]

            if user_row.empty:
                return None

            user_data = user_row.iloc[0].to_dict()

            if not user_data["is_active"]:
                return None

            if self._verify_password(password, user_data["password_hash"]):
                return User.from_dict(user_data)

            return None
        except Exception:
            return None

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by user ID."""
        try:
            df = pd.read_csv(self.csv_path)
            user_row = df[df["user_id"] == user_id]

            if user_row.empty:
                return None

            user_data = user_row.iloc[0].to_dict()
            return User.from_dict(user_data)
        except Exception:
            return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        try:
            df = pd.read_csv(self.csv_path)
            user_row = df[df["username"] == username]

            if user_row.empty:
                return None

            user_data = user_row.iloc[0].to_dict()
            return User.from_dict(user_data)
        except Exception:
            return None

    def get_user_count(self) -> int:
        """Get total number of users."""
        try:
            df = pd.read_csv(self.csv_path)
            return len(df)
        except Exception:
            return 0

    def update_user_role(self, user_id: str, new_role: UserRole) -> bool:
        """Update user role (admin function)."""
        try:
            df = pd.read_csv(self.csv_path)
            user_index = df[df["user_id"] == user_id].index

            if len(user_index) == 0:
                return False

            df.loc[user_index, "role"] = new_role.value
            df.to_csv(self.csv_path, index=False)
            return True
        except Exception:
            return False
