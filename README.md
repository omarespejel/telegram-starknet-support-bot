# Starknet Telegram Group Bot

Minimal bot for answering Starknet questions in Telegram groups using AI.

## Features

✅ Works in groups (responds when mentioned)  
✅ Works in DMs  
✅ Rate limits per chat  
✅ Saves conversation history  
✅ Uses Starknet AI API via WebSocket  
✅ Simple and maintainable  
✅ Ready to deploy  

## Project Structure

```
starknet-group-bot/
├── bot.py              # Main bot file (entry point)
├── ai_client.py        # Starknet AI WebSocket client
├── database.py         # Supabase database wrapper
├── config.py           # Configuration and environment variables
├── env.example         # Template for environment variables
├── pyproject.toml      # Python project configuration
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment configuration
└── README.md           # This file
```

## Setup

### 1. Environment Setup
```bash
# Copy environment template
cp env.example .env

# Fill in your credentials in .env
```

### 2. Bot Configuration (BotFather)
Talk to [@BotFather](https://t.me/BotFather) on Telegram:
```
/newbot → Create bot
/setprivacy → Disable (allows reading group messages)
/setjoingroups → Enable
/setcommands → Set commands:
start - Initialize bot
help - Show help
```

### 3. Supabase Setup
1. Create project at [supabase.com](https://supabase.com)
2. Run this SQL schema in SQL Editor:
```sql
-- Simple conversations table
CREATE TABLE conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    chat_id TEXT NOT NULL,
    chat_type TEXT NOT NULL,
    username TEXT,
    message TEXT NOT NULL,
    role TEXT CHECK (role IN ('user', 'assistant')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_chat_id ON conversations(chat_id);
CREATE INDEX idx_created_at ON conversations(created_at);
```
3. Get API keys from Settings → API

### 4. Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Run bot
python bot.py
```

### 5. Deploy to Render
1. Push code to GitHub
2. Connect repo to Render
3. Add environment variables
4. Deploy

## Usage

### In Telegram Groups
```
@your_bot_name What is Cairo?
@your_bot_name How do I deploy a smart contract?
```

### In Direct Messages
```
What is Cairo?
How do I deploy a smart contract?
```

## Environment Variables

Required:
- `TELEGRAM_BOT_TOKEN` - From BotFather
- `BOT_USERNAME` - Your bot's username
- `AI_API_BASE_URL` - Your Starknet AI API base URL
- `AI_API_WS_URL` - Your Starknet AI WebSocket URL

Optional:
- `SUPABASE_URL` - For conversation history
- `SUPABASE_SERVICE_KEY` - For conversation history
- `ENVIRONMENT` - development/production

## Rate Limiting

- 20 messages per hour per chat
- Configurable in `config.py`

## Topics the Bot Knows

- Cairo programming
- Smart contracts
- StarkNet architecture
- Account abstraction
- zk-STARKs
- L2 scaling

## File Overview

- **bot.py** (~150 lines) - Main bot logic, handlers, rate limiting
- **ai_client.py** (~100 lines) - WebSocket connection to AI API
- **database.py** (~50 lines) - Simple Supabase operations
- **config.py** (~20 lines) - Environment variable loading

Total: ~400 lines of clean, focused code.
