"""LMS flow — full tree ported from TG bot handlers/lms.py."""
from core.state import UserState


def _resp(text, buttons):
    return {"text": text, "buttons": buttons}


def handle_menu(state: UserState) -> dict:
    """Show LMS issue selection."""
    state.lms_escalation = state.lms_escalation or {"count": 0, "issue": ""}
    return _resp(
        "**LMS / Videos Issue**\n\nPlease select the LMS-related issue you are facing:",
        [
            {"text": "Batch Videos Not Visible", "cb": "lms_videos_not_visible"},
            {"text": "Videos Not Playing", "cb": "lms_videos_not_playing"},
            {"text": "Progress / Completion Not Updated", "cb": "lms_progress"},
            {"text": "Course Expired / Access Duration", "cb": "lms_expired"},
            {"text": "Other LMS Issue", "cb": "lms_other"},
            {"text": "⬅️ Back to Main Menu", "cb": "main_menu"},
        ]
    )


def handle_callback(state: UserState, callback: str) -> dict:
    """Handle all lms_* callbacks."""

    if callback == "lms_videos_not_visible":
        _track(state, "Batch Videos Not Visible")
        return _resp(
            "**Batch Videos Not Visible**\n\n"
            "If batch launch videos are not visible on your dashboard, please note:\n\n"
            "1. Batch videos are assigned only after batch launch.\n"
            "2. System sync may take some time after launch.\n"
            "3. Log out and log in again.\n"
            "4. Refresh your dashboard and check for updates.\n\n"
            "Select an option below if you need further help.",
            [
                {"text": "Still Not Visible", "cb": "lms_still_not_working"},
                {"text": "⬅️ Back", "cb": "lms"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    if callback == "lms_videos_not_playing":
        _track(state, "Videos Not Playing")
        return _resp(
            "**Videos Not Playing**\n\n"
            "If videos are not playing on the LMS, try the following steps:\n\n"
            "1. Use Google Chrome browser (recommended).\n"
            "2. Check your internet connection.\n"
            "3. Refresh the page once.\n"
            "4. Clear browser cache if required.\n"
            "5. Log out and log in again before retrying.\n\n"
            "Select an option below if you need further help.",
            [
                {"text": "Tried All Steps", "cb": "lms_still_not_working"},
                {"text": "⬅️ Back", "cb": "lms"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    if callback == "lms_progress":
        _track(state, "Progress / Completion Not Updated")
        return _resp(
            "**Progress / Completion Not Updated**\n\n"
            "If your learning progress or completion status is not updating:\n\n"
            "1. LMS progress may take time to sync with the portal.\n"
            "2. Ensure all required videos/modules are completed.\n"
            "3. Follow the learning sequence strictly.\n"
            "4. Avoid skipping videos.\n"
            "5. Log out and log in again after some time.\n"
            "6. Refresh the dashboard.\n\n"
            "Select an option below if you need further help.",
            [
                {"text": "Still Not Updated", "cb": "lms_still_not_working"},
                {"text": "⬅️ Back", "cb": "lms"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    if callback == "lms_expired":
        _track(state, "Course Expired / Access Duration")
        return _resp(
            "**Course Expired / LMS Access Duration**\n\n"
            "Regarding LMS content access:\n\n"
            "LMS access is available for **30 to 45 days** from the batch launch date.\n\n"
            "After this period, course content may show as expired.\n\n"
            "Select an option below if you need further help.",
            [
                {"text": "Still Have a Question", "cb": "lms_still_not_working"},
                {"text": "⬅️ Back", "cb": "lms"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    if callback == "lms_other":
        state.lms_other_mode = True
        _track(state, "Other LMS Issue")
        return _resp(
            "**Other LMS Issue**\n\n"
            "Please briefly describe the LMS issue you are facing.\n"
            "Our AI will analyze and provide help.",
            [
                {"text": "⬅️ Back", "cb": "lms"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    # --- Still Not Working (escalation trigger) ---
    if callback == "lms_still_not_working":
        state.lms_escalation["count"] = state.lms_escalation.get("count", 0) + 1
        attempts = state.lms_escalation["count"]

        if attempts >= 2:
            return {
                "text": "", "buttons": [],
                "_trigger_escalation": True,
                "_issue": state.lms_escalation.get("issue", "LMS Issue"),
            }
        else:
            return _resp(
                "**Let's try once more**\n\n"
                "Please try the following:\n"
                "1. Clear your browser cache\n"
                "2. Try in Incognito/Private mode\n"
                "3. Use a different browser (Chrome recommended)\n"
                "4. Check your internet connection\n\n"
                f"_Attempt {attempts}/2 - After 2 attempts, we'll connect you with support._\n\n"
                "Select an option below if you need further help.",
                [
                    {"text": "Still Not Working", "cb": "lms_still_not_working"},
                    {"text": "⬅️ Back", "cb": "lms"},
                    {"text": "🏠 Main Menu", "cb": "main_menu"},
                ]
            )

    # --- Fixed ---
    if callback == "lms_fixed":
        state.lms_escalation = {"count": 0, "issue": ""}
        return _resp("Great! Your LMS issue is resolved.\n\nHappy learning!",
                      [{"text": "🏠 Main Menu", "cb": "main_menu"}])

    # --- Back ---
    if callback == "lms_back_menu":
        from core.flows.menu import get_menu
        return get_menu()

    return handle_menu(state)


def _track(state: UserState, issue: str):
    state.lms_escalation["issue"] = issue
