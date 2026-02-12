"""Other Issue flow — single-turn AI for miscellaneous issues."""


def _resp(text, buttons):
    return {"text": text, "buttons": buttons}


def enter_other_mode() -> dict:
    """Show other issue prompt."""
    return _resp(
        "Please describe your issue in detail and I'll try to help:",
        [{"text": "⬅️ Back to Main Menu", "cb": "main_menu"}]
    )
