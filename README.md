# CPBFI Web Chatbot

Helpdesk chatbot that mirrors the CPBFI Telegram bot — drop into any website via a single `<script>` tag.

## Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your GROQ_API_KEY and email settings

# 3. Run
python app.py
```

Open http://localhost:8080 — click the chat bubble.

## Integration

Add this one line to any HTML page:

```html
<script src="https://your-server.com/widget/chatbot.js"></script>
```

The widget auto-detects the API URL from the script src.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/session/start` | Start a new chat session |
| POST | `/api/chat` | Send message or button click |
| GET | `/api/admin/stats` | Dashboard analytics (admin key required) |
| GET | `/api/admin/escalations` | List escalation tickets (admin key required) |

Admin endpoints require `X-Admin-Key` header matching `ADMIN_KEY` env var.

## Docker

```bash
docker build -t cpbfi-chatbot .
docker run -p 8080:8080 --env-file .env cpbfi-chatbot
```

## Project Structure

```
├── app.py              # FastAPI entry + demo page
├── config.py           # Environment settings
├── api/
│   ├── chat.py         # /api/session/start, /api/chat
│   ├── admin.py        # /api/admin/stats, /api/admin/escalations
│   └── schemas.py      # Pydantic models
├── core/
│   ├── state.py        # UserState dataclass
│   ├── router.py       # Central message router
│   ├── escalation.py   # Shared escalation engine
│   └── flows/          # Login, Assessment, LMS, Navigation, AI, Other
├── db/
│   ├── database.py     # Async SQLAlchemy setup
│   ├── models.py       # 4 tables
│   └── crud.py         # All DB operations
├── utils/              # AI, email, prompts, validators, rate limiter
└── widget/
    ├── chatbot.js      # Drop-in widget (zero dependencies)
    └── chatbot.css     # Dark glassmorphism theme
```
