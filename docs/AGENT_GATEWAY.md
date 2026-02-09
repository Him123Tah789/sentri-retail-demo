# Sentri Agent Gateway

## Architecture

```
Telegram / Web Chat
        ↓
   Sentri Agent Gateway  ⭐ (brain/router)
        ↓
 ┌───────────────┬───────────────┬───────────────┐
 │ Local LLM     │ Risk Engines   │ Future RAG KB │
 │ (chat/summar) │ (trusted tools)│ (knowledge)   │
 └───────────────┴───────────────┴───────────────┘
```

**Key Concepts:**
- ✅ LLM talks (generates responses)
- ✅ Rules/ML decide (risk detection)
- ✅ Gateway controls everything (routing)

## Components

### 1. Agent Gateway (`services/agent_gateway.py`)
The central brain that routes messages to the right tools.

**Intent Detection:**
- `SCAN_LINK` - URL in message → Risk Engine
- `SCAN_EMAIL` - "scan email" command → Email Analyzer
- `SCAN_LOG` - "scan log" command → Log Analyzer
- `GENERAL_CHAT` - Everything else → LLM + Knowledge Base
- `HELP` - Help requests
- `STATUS` - System status

### 2. Telegram Bot (`services/telegram_bot.py`)
Fast-win channel for instant security scanning.

**Commands:**
- `/start` - Welcome message
- `/help` - Show commands
- `/status` - System health
- `/scan <url>` - Scan a link
- `/scan email <text>` - Analyze email

### 3. Gateway API (`api/gateway.py`)
Universal HTTP endpoint for any client.

**Endpoints:**
- `POST /api/v1/gateway/message` - Process any message
- `GET /api/v1/gateway/health` - Health check
- `GET /api/v1/gateway/capabilities` - List features

## Setup Telegram Bot

### Step 1: Create Bot
1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Choose a name (e.g., "Sentri Security Bot")
4. Choose a username (e.g., "sentri_security_bot")
5. Copy the token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Configure
Create `.env` file in `app/backend/`:
```bash
TELEGRAM_BOT_TOKEN=your_token_here
```

Or set environment variable:
```powershell
$env:TELEGRAM_BOT_TOKEN = "your_token_here"
```

### Step 3: Run Bot
```bash
cd app/backend
python -m app.services.telegram_bot
```

## API Usage

### Scan a Link
```bash
curl -X POST http://localhost:8003/api/v1/gateway/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "https://suspicious-site.xyz/login", "channel": "api"}'
```

**Response:**
```json
{
  "text": "🔴 **Link Scan Result**\n\n**URL:** `https://suspicious-site.xyz/login`\n**Risk Score:** 65/100\n...",
  "intent": "scan_link",
  "tool_used": "risk_engine",
  "risk_score": 65,
  "risk_level": "HIGH"
}
```

### General Chat
```bash
curl -X POST http://localhost:8003/api/v1/gateway/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is phishing?", "channel": "api"}'
```

## Future Enhancements

### RAG Knowledge Base (Coming Soon)
```python
# Planned structure
class RAGKnowledgeBase:
    def __init__(self):
        self.vector_store = None  # ChromaDB or similar
        self.embeddings = None    # Sentence transformers
    
    async def search(self, query: str) -> List[Document]:
        # Search internal docs for context
        pass
    
    async def add_documents(self, docs: List[str]):
        # Index new documents
        pass
```

### Additional Channels
- WhatsApp Business API
- Slack Integration
- Microsoft Teams
- Discord Bot

## Files Overview

```
app/backend/app/
├── api/
│   └── gateway.py          # Gateway HTTP endpoints
├── services/
│   ├── agent_gateway.py    # Central router/brain
│   ├── telegram_bot.py     # Telegram integration
│   ├── risk_engine.py      # Security scanning (trusted tool)
│   └── llm_service.py      # LLM + knowledge base
```
