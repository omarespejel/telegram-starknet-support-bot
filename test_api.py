"""Quick verification script for the Starknet AI API connection.

Usage:
  uv run python test_api.py \
    --message "What is Cairo?" \
    --chat-id test-123 \
    --base-url https://your-api.com \
    --ws-url wss://your-api.com/ws

If flags are omitted, values from config.py are used.
"""

import argparse
import asyncio
import sys
import time

from ai_client import StarknetAI
from config import AI_API_BASE_URL, AI_API_WS_URL


async def run_test(base_url: str, ws_url: str, message: str, chat_id: str) -> None:
    print("=== Starknet AI API Connectivity Test ===")
    print(f"HTTP Base URL: {base_url}")
    print(f"WebSocket URL: {ws_url}")
    print(f"Chat ID: {chat_id}")
    print(f"Question: {message}")
    print("----------------------------------------")

    ai = StarknetAI(base_url, ws_url)

    started_at = time.perf_counter()
    try:
        response = await ai.get_response(message=message, chat_id=chat_id, history=[])
    except Exception as exc:  # pragma: no cover - simple CLI aid
        elapsed_ms = int((time.perf_counter() - started_at) * 1000)
        print(f"Error after {elapsed_ms} ms: {exc}", file=sys.stderr)
        raise
    elapsed_ms = int((time.perf_counter() - started_at) * 1000)

    # Basic debug metadata about the response
    resp_len = len(response or "")
    has_sources = "\n\n📚 Sources:" in (response or "")

    print(f"Elapsed: {elapsed_ms} ms")
    print(f"Response length: {resp_len} chars")
    print(f"Contains sources section: {has_sources}")
    if resp_len > 200:
        print("Preview (first 200 chars):")
        print(response[:200])
        print("--- Full Response ---")
    else:
        print("Response:")
    print(response)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test Starknet AI API connectivity")
    parser.add_argument(
        "--message",
        default="What is Cairo?",
        help="Message to send to the AI",
    )
    parser.add_argument(
        "--chat-id",
        default="test-123",
        help="Chat ID to use for the request",
    )
    parser.add_argument(
        "--base-url",
        default=AI_API_BASE_URL,
        help="HTTP base URL for the API (defaults to config)",
    )
    parser.add_argument(
        "--ws-url",
        default=AI_API_WS_URL,
        help="WebSocket URL for the API (defaults to config)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(
        run_test(
            base_url=args.base_url,
            ws_url=args.ws_url,
            message=args.message,
            chat_id=args.chat_id,
        )
    )


