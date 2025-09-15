"""Bot configuration."""

import os

from dotenv import load_dotenv

load_dotenv()

# Core settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME", "starknet_bot")

# AI API
AI_API_BASE_URL = os.getenv("AI_API_BASE_URL", "http://localhost:8000")
AI_API_WS_URL = os.getenv("AI_API_WS_URL", "ws://localhost:8000/ws")

# Optional model selection
CHAT_MODEL = os.getenv("CHAT_MODEL", "Claude 3.5 Sonnet")
CHAT_MODEL_PROVIDER = os.getenv("CHAT_MODEL_PROVIDER", "anthropic")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "Text embedding 3 large")
EMBEDDING_MODEL_PROVIDER = os.getenv("EMBEDDING_MODEL_PROVIDER", "openai")

# Focus modes
FOCUS_MODES = {
    "default": "cairoBookSearch",
    "web": "webSearch",
    "cairo": "cairoBookSearch",
}

# Database
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Rate limiting
RATE_LIMIT_PER_CHAT = 20  # messages per hour per chat
RATE_LIMIT_WINDOW = 3600  # seconds

# Note: TELEGRAM_BOT_TOKEN is validated at runtime in bot.py

# Validate WebSocket URL format if provided
if AI_API_WS_URL and not AI_API_WS_URL.startswith(("ws://", "wss://")):
    raise ValueError("AI_API_WS_URL must start with ws:// or wss://")
