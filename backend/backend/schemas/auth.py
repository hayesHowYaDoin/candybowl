from pydantic import BaseModel, Field, field_validator
import re


class RegisterRequest(BaseModel):
    """Request model for user registration."""

    username: str = Field(
        ...,
        description="Username for the new account",
        min_length=3,
        max_length=20,
    )
    email: str = Field(
        ..., description="Email address for the new account", min_length=1
    )
    password: str = Field(
        ..., description="Password for the new account", min_length=6
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username can only contain letters, numbers, and underscores"
            )
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        return v


class LoginRequest(BaseModel):
    """Request model for user login."""

    username: str = Field(..., description="Username for login", min_length=1)
    password: str = Field(..., description="Password for login", min_length=1)


class UpdateRoleRequest(BaseModel):
    """Request model for updating user role."""

    role: str = Field(
        ..., description="New role for the user", pattern="^(user|admin)$"
    )


class ValidateTokenRequest(BaseModel):
    """Request model for token validation."""

    token: str = Field(..., description="JWT token to validate", min_length=1)
