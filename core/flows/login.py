"""Login flow — full tree ported from TG bot handlers/login.py.

Returns plain {text, buttons} dicts. Escalation trigger is signaled by _trigger_escalation key.
"""
from core.state import UserState


def _resp(text, buttons):
    return {"text": text, "buttons": buttons}


def handle_menu(state: UserState) -> dict:
    """Show login portal selection."""
    state.login_escalation = state.login_escalation or {"count": 0, "portal": "", "issue": ""}
    return _resp(
        "**Login Issue**\n\nWhich portal are you trying to log in to?",
        [
            {"text": "Skillserv Portal", "cb": "login_portal_skillserv"},
            {"text": "Knowlens Portal", "cb": "login_portal_knowlens"},
            {"text": "⬅️ Back to Main Menu", "cb": "main_menu"},
        ]
    )


def handle_callback(state: UserState, callback: str) -> dict:
    """Handle all login_* callbacks."""

    # --- Portal selection ---
    if callback in ("login_portal_skillserv", "login_portal_knowlens"):
        portal = "Skillserv" if "skillserv" in callback else "Knowlens"
        state.login_escalation["portal"] = portal

        return _resp(
            f"**{portal} Portal — Login Help**\n\nWhat issue are you facing while logging in?",
            [
                {"text": "Invalid / Wrong Credentials", "cb": f"login_creds_{portal.lower()}"},
                {"text": "OTP Not Received", "cb": f"login_otp_{portal.lower()}"},
                {"text": "Forgot Password Issue", "cb": f"login_forgot_{portal.lower()}"},
                {"text": "Other Login Issue", "cb": f"login_other_{portal.lower()}"},
                {"text": "⬅️ Back", "cb": "login"},
            ]
        )

    # --- Invalid/Wrong Credentials ---
    if callback.startswith("login_creds_"):
        portal = callback.split("_")[-1].capitalize()
        _track(state, portal, "Invalid/Wrong Credentials")

        return _resp(
            "**Invalid / Wrong Credentials**\n\n"
            "Please check the following carefully:\n\n"
            "1. Make sure you are entering the correct:\n"
            "   • Registered Email ID\n"
            "   • Password (check caps lock)\n\n"
            "2. Confirm you are using the same email ID used during registration.\n\n"
            "3. Try closing the browser tab completely and log in again.\n\n"
            "4. If possible, try logging in from another device or browser.\n\n"
            "Select an option below if you need further help.",
            [
                {"text": "Forgot Password", "cb": f"login_forgot_{portal.lower()}"},
                {"text": "Still Not Working", "cb": f"login_still_not_working_{portal.lower()}"},
                {"text": "⬅️ Back", "cb": f"login_portal_{portal.lower()}"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    # --- OTP Not Received ---
    if callback.startswith("login_otp_"):
        portal = callback.split("_")[-1].capitalize()
        _track(state, portal, "OTP Not Received")

        return _resp(
            "**OTP Not Received**\n\n"
            "Please try the following steps:\n\n"
            "1. Check your **Spam / Junk** folder.\n"
            "2. Wait **2–3 minutes**, then refresh the login page and request a new OTP.\n"
            "3. Do **NOT** request OTP multiple times in a short duration.\n"
            "4. Try a different browser (Chrome, Edge, Firefox).\n"
            "5. Try a different device (phone, tablet, laptop).\n"
            "6. Ensure you're on a stable internet connection.\n\n"
            "_Requesting too many OTPs may temporarily block delivery._\n\n"
            "Select an option below if you need further help.",
            [
                {"text": "Still Not Received", "cb": f"login_still_not_working_{portal.lower()}"},
                {"text": "⬅️ Back", "cb": f"login_portal_{portal.lower()}"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    # --- Still Not Working (escalation trigger) ---
    if callback.startswith("login_still_not_working_"):
        portal = callback.split("_")[-1].capitalize()
        state.login_escalation["count"] = state.login_escalation.get("count", 0) + 1
        attempts = state.login_escalation["count"]

        if attempts >= 2:
            return {
                "text": "", "buttons": [],
                "_trigger_escalation": True,
                "_issue": state.login_escalation.get("issue", "Login Issue"),
                "_portal": portal,
            }
        else:
            return _resp(
                "**Let's try once more**\n\n"
                "Please try the following:\n"
                "1. Clear your browser cache\n"
                "2. Try in Incognito/Private mode\n"
                "3. Use a different browser or device\n\n"
                f"_Attempt {attempts}/2 - After 2 attempts, we'll connect you with support._\n\n"
                "Select an option below if you need further help.",
                [
                    {"text": "Still Not Working", "cb": f"login_still_not_working_{portal.lower()}"},
                    {"text": "⬅️ Back", "cb": f"login_portal_{portal.lower()}"},
                    {"text": "🏠 Main Menu", "cb": "main_menu"},
                ]
            )

    # --- Forgot Password ---
    if callback.startswith("login_forgot_"):
        portal = callback.split("_")[-1].capitalize()
        _track(state, portal, "Forgot Password")

        return _resp(
            f"**Forgot Password — {portal}**\n\n"
            "Please try the following steps:\n\n"
            "1. Close all browser tabs and clear cache.\n"
            "2. Go to the login page and click 'Forgot Password'.\n"
            "3. Enter your **registered email ID** carefully.\n"
            "4. Wait **2–3 minutes** for the reset link.\n"
            "5. Check your **Spam / Junk** folder.\n"
            "6. If not received, try again after a few minutes.\n\n"
            "_Too many requests may temporarily block delivery._\n\n"
            "Select an option below if you need further help.",
            [
                {"text": "Still Facing Issue", "cb": f"login_still_not_working_{portal.lower()}"},
                {"text": "⬅️ Back", "cb": f"login_portal_{portal.lower()}"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    # --- Other Login Issue (enters AI mode) ---
    if callback.startswith("login_other_"):
        portal = callback.split("_")[-1].capitalize()
        state.login_other_mode = portal
        _track(state, portal, "Other Login Issue")

        return _resp(
            f"**Other Login Issue — {portal}**\n\n"
            "Please briefly describe the login issue you are facing.\n"
            "Our AI will analyze and provide help.",
            [
                {"text": "⬅️ Back", "cb": f"login_portal_{portal.lower()}"},
            ]
        )

    # --- Fixed ---
    if callback == "login_fixed":
        state.login_escalation = {"count": 0, "portal": "", "issue": ""}
        return _resp("Great! Your login issue is resolved.\n\nHappy learning!",
                      [{"text": "🏠 Main Menu", "cb": "main_menu"}])

    # --- Back to menu ---
    if callback == "login_back_menu":
        from core.flows.menu import get_menu
        return get_menu()

    # Fallback
    return handle_menu(state)


def _track(state: UserState, portal: str, issue: str):
    """Track the current issue for escalation counting."""
    state.login_escalation["portal"] = portal
    state.login_escalation["issue"] = issue
