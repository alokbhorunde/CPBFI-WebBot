"""Central message router — replaces general.py from Telegram bot.

Every API call hits this: route_callback() for button clicks, route_text() for typed messages.
Returns a plain dict {text, buttons} — no Telegram/web framework code.
"""
import logging
from core.state import UserState
from core.flows import menu, login, assessment, lms, navigation, ai_chat, other
from core import escalation
from utils.ai import ask_ai_free

logger = logging.getLogger(__name__)

GREETINGS = {"hi", "hello", "hey", "start", "menu", "help", "main menu", "home"}


def route_callback(state: UserState, callback: str) -> dict:
    """Route a button click. Returns {text: str, buttons: list[dict]}."""

    # Universal actions
    if callback == "main_menu":
        state.clear_all()
        return menu.get_menu()

    if callback in ("login_fixed", "assessment_fixed", "pcq_fixed", "post_fixed", "lms_fixed"):
        state.clear_all()
        return _resp("Great! Your issue is resolved.\n\nHappy learning!",
                      [{"text": "🏠 Main Menu", "cb": "main_menu"}])

    # Cancel escalation — clear detail collection, back to menu
    if callback.endswith("_cancel_escalation"):
        state.detail_collection = None
        return menu.get_menu()

    # --- LOGIN ---
    if callback == "login":
        state.detail_collection = None
        return login.handle_menu(state)
    if callback.startswith("login_"):
        result = login.handle_callback(state, callback)
        if result.get("_trigger_escalation"):
            return escalation.start_collection(state, "login",
                result["_issue"], result.get("_portal", ""))
        return result

    # --- ASSESSMENT ---
    if callback == "assessment":
        state.detail_collection = None
        return assessment.handle_menu(state)
    if callback.startswith(("assessment_", "pcq", "post")):
        result = assessment.handle_callback(state, callback)
        if result.get("_trigger_escalation"):
            return escalation.start_collection(state, "assessment",
                result["_issue"], assessment_type=result.get("_type", ""))
        return result

    # --- LMS ---
    if callback == "lms":
        state.detail_collection = None
        return lms.handle_menu(state)
    if callback.startswith("lms_"):
        result = lms.handle_callback(state, callback)
        if result.get("_trigger_escalation"):
            return escalation.start_collection(state, "lms", result["_issue"])
        return result

    # --- NAVIGATION ---
    if callback.startswith(("navhelp", "nav_")):
        return navigation.handle_callback(state, callback)

    # --- AI CHAT ---
    if callback == "ai_chat":
        state.ai_chat_mode = True
        return ai_chat.enter_chat_mode()
    if callback == "exit_ai_chat":
        state.ai_chat_mode = False
        return menu.get_menu()

    # --- OTHER ISSUE ---
    if callback == "other":
        state.other_issue_mode = True
        return other.enter_other_mode()

    logger.warning(f"Unhandled callback: {callback}")
    return menu.get_menu()


def route_text(state: UserState, text: str) -> dict:
    """Route a text message. Returns {text: str, buttons: list[dict]}."""

    # Greeting = full reset
    if text.strip().lower() in GREETINGS or text.strip().lower().startswith("/start"):
        state.clear_all()
        m = menu.get_menu()
        return _resp("👋 Welcome to CPBFI Helpdesk!\n\nHow can I assist you today?", m["buttons"])

    # Detail collection = highest priority
    if state.is_collecting_details():
        return escalation.process_input(state, text)

    # "Other" modes (AI analysis for specific categories)
    if state.login_other_mode:
        portal = state.login_other_mode
        state.login_other_mode = None
        prompt = f"User is facing a login issue on {portal} portal. Their issue: {text}"
        ai = ask_ai_free(prompt)
        return _resp(ai, [
            {"text": "✅ Issue Resolved", "cb": "login_fixed"},
            {"text": "Still Need Help", "cb": f"login_still_not_working_{portal.lower()}"},
            {"text": "⬅️ Back", "cb": "login"},
        ])

    if state.assessment_other_mode and state.assessment_other_mode.get("active"):
        atype = state.assessment_other_mode.get("type", "Assessment")
        state.assessment_other_mode = {"active": False, "type": ""}
        prompt = f"User is facing a {atype} issue on Skillserv portal. Their issue: {text}"
        ai = ask_ai_free(prompt)
        back = "assessment_pcq" if atype == "PCQ" else "assessment_post"
        return _resp(ai, [
            {"text": "✅ Issue Resolved", "cb": "assessment_fixed"},
            {"text": "Still Need Help", "cb": "assessment_still_not_working"},
            {"text": "⬅️ Back", "cb": back},
        ])

    if state.lms_other_mode:
        state.lms_other_mode = False
        prompt = f"User is facing an LMS/Video issue on Skillserv portal. Their issue: {text}"
        ai = ask_ai_free(prompt)
        return _resp(ai, [
            {"text": "✅ Issue Resolved", "cb": "lms_fixed"},
            {"text": "Still Need Help", "cb": "lms_still_not_working"},
            {"text": "⬅️ Back", "cb": "lms"},
        ])

    if state.other_issue_mode:
        state.other_issue_mode = False
        ai = ask_ai_free(text)
        return _resp(ai, [
            {"text": "✅ Issue Resolved", "cb": "main_menu"},
            {"text": "Still Need Help", "cb": "other"},
            {"text": "🏠 Main Menu", "cb": "main_menu"},
        ])

    # AI Chat mode — multi-turn
    if state.ai_chat_mode:
        ai = ask_ai_free(text, human_mode=True)
        return _resp(ai, [{"text": "❌ Exit Chat", "cb": "exit_ai_chat"}])

    # Fallback — AI + menu
    ai = ask_ai_free(text)
    m = menu.get_menu()
    return _resp(ai, m["buttons"])


def _resp(text: str, buttons: list) -> dict:
    return {"text": text, "buttons": buttons}
