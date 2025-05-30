"""User profile resource implementation (legacy)."""

from ..models.schemas import UserProfile
from typing import Dict, Any, Optional


async def get_user_profile(user_id: str) -> dict:
    """Get user profile by ID."""
    # In production, this would fetch from a database
    profile = UserProfile(
        id=user_id,
        name=f"User {user_id}",
        email=f"user{user_id}@example.com",
        status="active",
        preferences={
            "theme": "dark",
            "notifications": True,
            "language": "en"
        }
    )
    
    return profile.model_dump()