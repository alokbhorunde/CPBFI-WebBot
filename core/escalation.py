"""Shared escalation engine — replaces 3 copy-pasted versions from TG bot.

Handles: start_collection → name → email (validated) → bfsi → send email → confirm/fail
"""
import logging
from core.state import UserState
from utils.validators import is_valid_email
from utils.email_service import send_email_to_it

logger = logging.getLogger(__name__)


def start_collection(state: UserState, category: str, issue: str,
                     portal: str = "", assessment_type: str = "") -> dict:
    """Begin name → email → bfsi form."""
    state.detail_collection = {
        "step": "name",
        "category": category,
        "issue": issue,
        "portal": portal,
        "assessment_type": assessment_type,
        "name": "", "email": "", "bfsi": "", "description": ""
    }

    # Assessment has an extra "describe" step first
    if category == "assessment":
        state.detail_collection["step"] = "describe"
        return {
            "text": (f"**Escalating {assessment_type or 'Assessment'} Issue to Support Team**\n\n"
                     "Before we connect you with support, please **briefly describe what exactly happened** "
                     "and what you already tried.\n\n"
                     "_Example: I refreshed the page and tried incognito mode but the quiz still shows 'Not Available'._"),
            "buttons": [{"text": "❌ Cancel", "cb": f"{category}_cancel_escalation"}]
        }

    return {
        "text": ("**Escalating to Support Team**\n\n"
                 "We need a few details to help you faster.\n\n"
                 "**Step 1/3:** Please enter your **Full Name**:"),
        "buttons": [{"text": "❌ Cancel", "cb": f"{category}_cancel_escalation"}]
    }


def process_input(state: UserState, text: str) -> dict:
    """Process the next step in detail collection. Returns response dict."""
    d = state.detail_collection
    step = d["step"]
    cancel_btn = [{"text": "❌ Cancel", "cb": f"{d['category']}_cancel_escalation"}]

    if step == "describe":
        d["description"] = text.strip()
        d["step"] = "name"
        return {"text": "Got it. Now we need a few details.\n\n**Step 1/3:** Please enter your **Full Name**:",
                "buttons": cancel_btn}

    if step == "name":
        if len(text.strip()) < 2:
            return {"text": "⚠️ Name must be at least 2 characters. Please try again:", "buttons": cancel_btn}
        d["name"] = text.strip()
        d["step"] = "email"
        return {"text": f"Name: **{text.strip()}**\n\n**Step 2/3:** Please enter your **Email ID**:",
                "buttons": cancel_btn}

    if step == "email":
        if not is_valid_email(text.strip()):
            return {"text": "⚠️ That doesn't look like a valid email.\n\nPlease enter a valid **Email ID** (e.g. name@example.com):",
                    "buttons": cancel_btn}
        d["email"] = text.strip()
        d["step"] = "bfsi"
        return {"text": f"Email: **{text.strip()}**\n\n**Step 3/3:** Please enter your **BFSI ID**:",
                "buttons": cancel_btn}

    if step == "bfsi":
        d["bfsi"] = text.strip()
        d["step"] = None  # Mark complete

        # Build email subject
        subject_parts = [d["category"].upper()]
        if d.get("assessment_type"):
            subject_parts.append(d["assessment_type"])
        subject_parts.append(d["issue"])
        if d.get("portal"):
            subject_parts.append(d["portal"])
        subject = " - ".join(subject_parts)

        body_extra = f"\nStudent Description: {d['description']}" if d.get("description") else ""

        email_sent = send_email_to_it(
            f"{d['name']} ({d['email']})",
            f"{subject}{body_extra}"
        )

        d["_email_sent"] = email_sent
        d["_complete"] = True

        if email_sent:
            return {
                "text": (f"**Issue Escalated Successfully!**\n\n"
                         f"**Details Submitted:**\n"
                         f"• Name: {d['name']}\n"
                         f"• Email: {d['email']}\n"
                         f"• BFSI ID: {d['bfsi']}\n"
                         f"• Category: {d['category'].title()}\n"
                         f"• Issue: {d['issue']}\n\n"
                         "Our support team will contact you shortly.\n"
                         "For urgent queries: support@cpbfi.org"),
                "buttons": [{"text": "🏠 Main Menu", "cb": "main_menu"}]
            }
        else:
            return {
                "text": (f"**Issue Recorded — Email Could Not Be Sent**\n\n"
                         f"• Name: {d['name']}\n"
                         f"• Email: {d['email']}\n"
                         f"• BFSI ID: {d['bfsi']}\n"
                         f"• Issue: {d['issue']}\n\n"
                         "⚠️ We couldn't send the escalation email automatically.\n"
                         "Please contact support directly: **support@cpbfi.org**"),
                "buttons": [{"text": "🏠 Main Menu", "cb": "main_menu"}]
            }

    return {"text": "Something went wrong. Please start over.",
            "buttons": [{"text": "🏠 Main Menu", "cb": "main_menu"}]}
