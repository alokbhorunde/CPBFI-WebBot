"""Main menu — 6 category buttons."""


def get_menu() -> dict:
    """Return the main support menu."""
    return {
        "text": "Please select a category:",
        "buttons": [
            {"text": "🔐 Login", "cb": "login"},
            {"text": "📝 Assessment", "cb": "assessment"},
            {"text": "🎥 LMS / Videos", "cb": "lms"},
            {"text": "🧭 Navigation Help", "cb": "navhelp"},
            {"text": "❓ Other Issue", "cb": "other"},
            {"text": "💬 Chat with Us", "cb": "ai_chat"},
        ]
    }
