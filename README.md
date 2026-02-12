# 🤖 CPBFI Web Chatbot

A standalone helpdesk chatbot for **CPBFI** (Centre for Promotion of Banking & Financial Inclusion) that mirrors the existing Telegram bot functionality. Integrates into any website with a single `<script>` tag.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [Widget Integration](#-widget-integration)
- [Support Flows](#-support-flows)
- [Database Schema](#-database-schema)
- [Deployment](#-deployment)
- [License](#-license)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Login Help** | Troubleshooting for Skillserv & Knowlens portals (credentials, OTP, forgot password) |
| **Assessment Support** | PCQ and Post Assessment issue resolution (6 issues each) |
| **LMS / Videos** | Video playback, progress tracking, course access, and expiry help |
| **Navigation Guides** | Step-by-step guides for 7 platform actions |
| **AI Chat** | Multi-turn AI conversations powered by Groq (Llama 3.1) |
| **Smart Escalation** | Auto-collects student details (name, email, BFSI ID) after 2 failed attempts and sends email to IT |
| **Session Persistence** | Chat survives page refreshes via `sessionStorage` |
| **Rate Limiting** | 10 messages per 30 seconds per session |
| **Admin Dashboard** | API endpoints for stats and escalation management |
| **Mobile Responsive** | Full-screen chat on mobile, floating widget on desktop |

---

## 🏗 Architecture

```
┌──────────────────┐         ┌──────────────────────────────────┐
│   Any Website    │         │       FastAPI Backend             │
│                  │         │                                  │
│  <script src=    │ ──────► │  POST /api/session/start          │
│  "chatbot.js">   │         │  POST /api/chat                  │
│                  │ ◄────── │                                  │
│  Widget renders  │   JSON  │  core/router.py ──► flows/*      │
│  messages + btns │         │       │                          │
└──────────────────┘         │       ▼                          │
                             │  db/crud.py ──► SQLite           │
                             │  utils/ai.py ──► Groq API        │
                             │  utils/email.py ──► SMTP         │
                             └──────────────────────────────────┘
```

### Request Flow

1. **User opens page** → Widget loads → Calls `POST /api/session/start`
2. **Server** → Creates session in DB → Returns welcome message + 6 menu buttons
3. **User clicks button or types** → Widget calls `POST /api/chat`
4. **Server** → Loads session state from DB → Routes to correct flow → Returns response → Saves state back

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11+, FastAPI, Uvicorn |
| **Database** | SQLite (via SQLAlchemy async + aiosqlite) |
| **AI** | Groq API (Llama 3.1 8B Instant) |
| **Email** | SMTP (Gmail) |
| **Frontend** | Vanilla JavaScript + CSS (zero dependencies) |

---

## 📁 Project Structure

```
cpbfi-web-chatbot/
│
├── app.py                    # FastAPI entry — serves API + widget
├── config.py                 # Environment variable settings
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment config
├── .gitignore
├── Dockerfile
├── README.md
│
├── api/                      # REST API layer
│   ├── __init__.py
│   ├── schemas.py            # Pydantic request/response models
│   ├── chat.py               # POST /api/session/start, POST /api/chat
│   └── admin.py              # GET /api/admin/stats, GET /api/admin/escalations
│
├── core/                     # Business logic engine
│   ├── __init__.py
│   ├── state.py              # UserState dataclass (replaces 9 TG bot dicts)
│   ├── router.py             # Central message/callback router
│   ├── escalation.py         # Shared detail collection (name→email→BFSI→send)
│   └── flows/                # Individual support flows
│       ├── __init__.py
│       ├── menu.py           # Main menu (6 buttons)
│       ├── login.py          # Login flow (2 portals × 4 issues)
│       ├── assessment.py     # Assessment flow (PCQ: 6 issues, Post: 6 issues)
│       ├── lms.py            # LMS flow (5 issue types)
│       ├── navigation.py     # 7 navigation guides
│       ├── ai_chat.py        # Multi-turn AI chat mode
│       └── other.py          # Single-turn AI for misc issues
│
├── db/                       # Database layer
│   ├── __init__.py
│   ├── database.py           # Async SQLAlchemy engine + session factory
│   ├── models.py             # 4 tables (sessions, messages, escalations, analytics)
│   └── crud.py               # All database read/write operations
│
├── utils/                    # Shared utilities
│   ├── __init__.py
│   ├── ai.py                 # Groq AI client with retry logic
│   ├── email_service.py      # SMTP email sender
│   ├── prompts.py            # AI system prompts
│   ├── validators.py         # Email validation
│   └── rate_limiter.py       # Per-session rate limiter
│
└── widget/                   # Frontend (served as static files)
    ├── chatbot.js            # Self-contained widget (zero dependencies)
    └── chatbot.css           # Blue & white theme
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- A [Groq API key](https://console.groq.com/) (free tier works)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/alokbhorunde/CPBFI-WebBot.git
cd CPBFI-WebBot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env → add your GROQ_API_KEY and email settings

# 4. Run the server
python app.py
```

Open **http://localhost:8080** → Click the blue chat bubble 💬

---

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | ✅ Yes | — | Groq API key for AI features |
| `SENDER_EMAIL` | For escalation | — | Gmail address for sending escalation emails |
| `SENDER_PASSWORD` | For escalation | — | Gmail App Password ([generate here](https://myaccount.google.com/apppasswords)) |
| `SMTP_SERVER` | No | `smtp.gmail.com` | SMTP server address |
| `SMTP_PORT` | No | `587` | SMTP server port |
| `RECEIVER_EMAIL` | For escalation | — | IT support team email |
| `DATABASE_URL` | No | `sqlite+aiosqlite:///./chatbot.db` | Database connection string |
| `ADMIN_KEY` | No | `changeme` | API key for admin endpoints |
| `ALLOWED_ORIGINS` | No | `*` | CORS allowed origins (comma-separated) |
| `HOST` | No | `0.0.0.0` | Server bind host |
| `PORT` | No | `8080` | Server bind port |

---

## 📖 API Documentation

### Interactive Docs

Once the server is running, visit: **http://localhost:8080/docs** (Swagger UI)

### Endpoints

#### `POST /api/session/start`

Creates a new chat session and returns the welcome message.

**Request:** No body required.

**Response:**
```json
{
  "session_id": "uuid-string",
  "message": {
    "text": "👋 Welcome to CPBFI Helpdesk!\n\nHow can I assist you today?",
    "buttons": [
      {"text": "🔐 Login", "cb": "login"},
      {"text": "📝 Assessment", "cb": "assessment"},
      {"text": "🎥 LMS / Videos", "cb": "lms"},
      {"text": "🧭 Navigation Help", "cb": "navhelp"},
      {"text": "❓ Other Issue", "cb": "other"},
      {"text": "💬 Chat with Us", "cb": "ai_chat"}
    ]
  }
}
```

---

#### `POST /api/chat`

Sends a user message or button click and returns the bot response.

**Request:**
```json
{
  "session_id": "uuid-from-start",
  "message": "Hello",
  "callback_data": null
}
```

For button clicks:
```json
{
  "session_id": "uuid-from-start",
  "message": null,
  "callback_data": "login"
}
```

**Response:**
```json
{
  "text": "**Login Issue**\n\nWhich portal are you trying to log in to?",
  "buttons": [
    {"text": "Skillserv Portal", "cb": "login_portal_skillserv"},
    {"text": "Knowlens Portal", "cb": "login_portal_knowlens"},
    {"text": "⬅️ Back to Main Menu", "cb": "main_menu"}
  ]
}
```

---

#### `GET /api/admin/stats`

Returns dashboard analytics. Requires `X-Admin-Key` header.

**Headers:** `X-Admin-Key: your-admin-key`

**Response:**
```json
{
  "total_sessions": 150,
  "today_sessions": 12,
  "total_messages": 890,
  "total_escalations": 8,
  "pending_escalations": 2,
  "events_this_week": 340
}
```

---

#### `GET /api/admin/escalations`

Returns list of escalation tickets. Supports `?status=pending` filter.

**Headers:** `X-Admin-Key: your-admin-key`

**Response:**
```json
[
  {
    "id": 1,
    "session_id": "uuid",
    "category": "login",
    "issue": "Invalid/Wrong Credentials",
    "portal": "Skillserv",
    "student_name": "John Doe",
    "student_email": "john@example.com",
    "bfsi_id": "BFSI12345",
    "email_sent": true,
    "status": "sent",
    "created_at": "2026-02-12T10:30:00"
  }
]
```

---

## 🔌 Widget Integration

### Basic Integration (any website)

Add this **single line** before `</body>` in your HTML:

```html
<script src="https://your-server.com/widget/chatbot.js"></script>
```

That's it! The widget will:
- Auto-detect the API URL from the script source
- Create the chat bubble in the bottom-right corner
- Manage sessions via `sessionStorage`
- Work on any page without conflicts

### Custom Theming

Override CSS variables in your site's stylesheet:

```css
:root {
    --cb-primary: #2563eb;        /* Primary blue */
    --cb-primary-hover: #1d4ed8;  /* Darker blue on hover */
    --cb-bg: #ffffff;             /* Panel background */
    --cb-surface: #f0f4ff;        /* Input/button surface */
    --cb-border: #e2e8f0;         /* Border color */
    --cb-text: #1e293b;           /* Text color */
    --cb-text-dim: #64748b;       /* Secondary text */
}
```

---

## 🔄 Support Flows

### Flow Diagram

```
Welcome Message
    ├── 🔐 Login
    │   ├── Skillserv Portal
    │   │   ├── Invalid Credentials → Troubleshoot → Still Not Working (×2) → Escalation
    │   │   ├── OTP Not Received → Troubleshoot → Still Not Working (×2) → Escalation
    │   │   ├── Forgot Password → Troubleshoot → Still Not Working (×2) → Escalation
    │   │   └── Other Issue → AI Analysis → Resolved / Escalation
    │   └── Knowlens Portal (same sub-tree)
    │
    ├── 📝 Assessment
    │   ├── Pre-Course Quiz (PCQ)
    │   │   ├── Where is the Quiz? → Troubleshoot → Escalation
    │   │   ├── Test Not Showing → Troubleshoot → Escalation
    │   │   ├── Unable to Submit → Troubleshoot → Escalation
    │   │   ├── Exited Midway → Troubleshoot → Escalation
    │   │   ├── Joined Late → Info → Escalation
    │   │   └── Other PCQ Issue → AI Analysis → Escalation
    │   └── Post Assessment (same 6 issues)
    │
    ├── 🎥 LMS / Videos
    │   ├── Batch Videos Not Visible → Troubleshoot → Escalation
    │   ├── Videos Not Playing → Troubleshoot → Escalation
    │   ├── Progress Not Updated → Troubleshoot → Escalation
    │   ├── Course Expired → Info → Escalation
    │   └── Other LMS Issue → AI Analysis → Escalation
    │
    ├── 🧭 Navigation Help
    │   ├── How to Login
    │   ├── How to Attempt PCQ
    │   ├── How to Attempt Post Assessment
    │   ├── How to Submit Feedback
    │   ├── How to Complete Profile
    │   ├── How to Download HR Certificate
    │   └── How to Download Completion Certificate
    │
    ├── ❓ Other Issue → AI Analysis
    │
    └── 💬 Chat with Us → Multi-turn AI Chat
```

### Escalation Flow

After **2 failed troubleshooting attempts**, the bot auto-collects:

1. **Description** (assessment only) — what happened and what was tried
2. **Full Name**
3. **Email ID** (validated)
4. **BFSI ID**

Then sends an email to the IT support team and saves the ticket to the database.

---

## 🗄 Database Schema

### Tables

| Table | Purpose |
|-------|---------|
| `sessions` | Chat sessions with JSON state blob |
| `messages` | Full conversation log (user + bot messages) |
| `escalations` | Support tickets with student details |
| `analytics` | Event logging for dashboards |

### Key Columns

**sessions:**
| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `state` | JSON | Serialized `UserState` object |
| `is_active` | Boolean | Whether session is active |
| `ip_address` | String | Client IP |
| `created_at` | DateTime | Session start time |

**escalations:**
| Column | Type | Description |
|--------|------|-------------|
| `category` | String | login / assessment / lms |
| `issue` | String | Specific issue description |
| `portal` | String | Skillserv / Knowlens |
| `student_name` | String | Student's full name |
| `student_email` | String | Validated email |
| `bfsi_id` | String | BFSI registration ID |
| `email_sent` | Boolean | Whether IT was notified |
| `status` | String | pending / sent / resolved |

---

## 🐳 Deployment

### Docker

```bash
docker build -t cpbfi-chatbot .
docker run -p 8080:8080 --env-file .env cpbfi-chatbot
```

### Production Checklist

- [ ] Set a strong `ADMIN_KEY`
- [ ] Set `ALLOWED_ORIGINS` to your portal domain(s)
- [ ] Configure email credentials for escalation
- [ ] Switch `DATABASE_URL` to PostgreSQL for production
- [ ] Deploy behind a reverse proxy (Nginx/Caddy) with HTTPS

---

## 📄 License

This project is built for **CPBFI** internal use.
