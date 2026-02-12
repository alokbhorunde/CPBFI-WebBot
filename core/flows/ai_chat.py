"""AI Chat flow — multi-turn AI chat mode."""


def _resp(text, buttons):
    return {"text": text, "buttons": buttons}


def enter_chat_mode() -> dict:
    """Enter AI chat mode."""
    return _resp(
        "**CPBFI Support Chat**\n\n"
        "You can ask me about:\n"
        "• Login & Password issues\n"
        "• PCQ & Post Assessment\n"
        "• LMS & Videos\n"
        "• Platform Navigation\n"
        "• Profile & Documents\n"
        "• Certificates\n\n"
        "_I can only help with CPBFI platform questions._\n\n"
        "Press 'Exit AI Chat' to return to menu.",
        [{"text": "❌ Exit AI Chat", "cb": "exit_ai_chat"}]
    )
