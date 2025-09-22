"""Starknet AI API client."""

import asyncio
import json
import logging
from urllib.parse import quote_plus

import aiohttp

from config import (
    CHAT_MODEL,
    CHAT_MODEL_PROVIDER,
    EMBEDDING_MODEL,
    EMBEDDING_MODEL_PROVIDER,
    FOCUS_MODES,
)

logger = logging.getLogger(__name__)


class StarknetAI:
    def __init__(self, base_url: str, ws_url: str):
        self.base_url = base_url
        self.ws_url = ws_url
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            self.session = None

    async def get_available_models(self) -> dict:
        """Fetch available models from the API."""
        try:
            session = self.session or aiohttp.ClientSession()
            async with session.get(f"{self.base_url}/models", timeout=15) as resp:
                data = await resp.json()
                return data
        except Exception as e:
            logger.error("Failed to fetch models: %s", e)
            return {}
        finally:
            if not self.session and 'session' in locals():
                try:
                    await session.close()
                except Exception:
                    pass

    async def get_response(
        self, message: str, chat_id: str, history: list[dict] | None = None
    ) -> str:
        """Get AI response for a message with retry logic and connection pooling."""

        # Convert history to API format
        formatted_history = []
        if history:
            for msg in history[-6:]:  # Last 6 messages (3 exchanges)
                role = "human" if msg["role"] == "user" else "ai"
                formatted_history.append([role, msg["message"]])

        params = {
            "chatModel": quote_plus(CHAT_MODEL),
            "chatModelProvider": CHAT_MODEL_PROVIDER,
            "embeddingModel": quote_plus(EMBEDDING_MODEL),
            "embeddingModelProvider": EMBEDDING_MODEL_PROVIDER,
        }
        ws_url = f"{self.ws_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])

        # Retry logic for transient failures
        for attempt in range(3):
            try:
                session = self.session or aiohttp.ClientSession()
                async with session.ws_connect(ws_url, timeout=30) as ws:
                    await ws.send_str(
                        json.dumps(
                            {
                                "type": "message",
                                "message": {
                                    "messageId": f"tg-{chat_id}-msg",
                                    "chatId": chat_id,
                                    "content": message,
                                },
                                "copilot": False,
                                "focusMode": FOCUS_MODES.get("default", "starknetEcosystemSearch"),
                                "history": formatted_history,
                            }
                        )
                    )

                    full_response = ""
                    sources: list[dict] = []
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            # Capture messageId if present for traceability
                            message_id = data.get("messageId") or data.get("data", {}).get("messageId") if isinstance(data.get("data"), dict) else None
                            if data["type"] == "sources":
                                sources = data.get("data", [])[:3]
                            elif data["type"] == "message":
                                full_response += data.get("data", "")
                            elif data["type"] == "messageEnd":
                                # Prefer messageId in "data" if available
                                end_message_id = (
                                    data.get("data", {}).get("messageId")
                                    if isinstance(data.get("data"), dict)
                                    else data.get("messageId")
                                )
                                # We don't surface the id, but we could log it for tracing
                                if end_message_id:
                                    logger.debug("AI message completed: %s", end_message_id)
                                break
                            elif data["type"] == "error":
                                logger.error(f"API error: {data}")
                                if attempt == 2:
                                    return "Sorry, I encountered an error. Please try again."
                                break

                    if sources and full_response:
                        full_response += "\n\n📚 Sources:"
                        for idx, source in enumerate(sources, 1):
                            url = source.get("metadata", {}).get("url", "")
                            if url:
                                full_response += f"\n{idx}. {url}"

                    if not self.session:
                        await session.close()

                    return full_response or "I couldn't generate a response. Please try again."

            except TimeoutError:
                logger.warning(f"AI WebSocket timeout on attempt {attempt + 1}/3")
                if attempt == 2:
                    return "Response timeout. Please try with a shorter question."
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"AI API error on attempt {attempt + 1}/3: {e}")
                if attempt == 2:
                    return "I'm having trouble connecting to the knowledge base. Please try again."
                await asyncio.sleep(1)
            finally:
                if not self.session and 'session' in locals():
                    try:
                        await session.close()
                    except Exception:
                        pass
