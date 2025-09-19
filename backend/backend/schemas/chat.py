from pydantic import BaseModel, Field
from typing import Optional


class ChatMessageRequest(BaseModel):
    """Request model for sending a message to a chat session."""

    chat_id: str = Field(
        ..., description="Unique identifier for the chat session", min_length=1
    )
    message: str = Field(
        ...,
        description="Message content to send to the chat",
        min_length=1,
        max_length=5000,
    )


class ChatMessageResponse(BaseModel):
    """Response model for chat message endpoints."""

    response: str = Field(description="AI response to the user's message")


class ChatSessionResponse(BaseModel):
    """Response model for starting a new chat session."""

    chat_id: str = Field(
        description="Unique identifier for the new chat session"
    )
    response: Optional[str] = Field(
        default=None, description="Initial response for restock chats"
    )


class ChatStatusResponse(BaseModel):
    """Response model for chat status endpoint."""

    active_sessions: int = Field(
        description="Number of currently active chat sessions"
    )
    sessions_cleaned: int = Field(
        description="Number of expired sessions cleaned up"
    )
    expiry_minutes: int = Field(
        description="Chat session expiry time in minutes"
    )
    sessions: list[dict] = Field(description="Details of active chat sessions")


class CleanupResponse(BaseModel):
    """Response model for manual cleanup endpoint."""

    message: str = Field(description="Cleanup result message")
    active_sessions: int = Field(
        description="Number of active sessions remaining"
    )
