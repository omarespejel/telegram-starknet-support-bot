"""Simple database wrapper for Supabase."""

import logging
import asyncio

from supabase import Client, create_client

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key) if url and key else None

    async def save_message(
        self,
        user_id: str,
        chat_id: str,
        chat_type: str,
        username: str | None,
        message: str,
        role: str,
    ) -> None:
        """Save a message to the database."""
        if not self.client:
            return  # Skip if no database configured

        try:
            await asyncio.to_thread(
                lambda: self.client.table("conversations")
                .insert(
                    {
                        "user_id": user_id,
                        "chat_id": chat_id,
                        "chat_type": chat_type,
                        "username": username,
                        "message": message[:2000],  # Truncate long messages
                        "role": role,
                    }
                )
                .execute()
            )
        except Exception as e:
            logger.error(f"Failed to save message: {e}")

    async def get_chat_history(self, chat_id: str, limit: int = 10) -> list:
        """Get recent messages for a chat."""
        if not self.client:
            return []

        try:
            result = await asyncio.to_thread(
                lambda: self.client.table("conversations")
                .select("role, message")
                .eq("chat_id", chat_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return list(reversed(result.data)) if result.data else []
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return []
