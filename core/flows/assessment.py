"""Assessment flow — full PCQ + Post Assessment tree ported from TG bot handlers/assessment.py."""
from core.state import UserState


def _resp(text, buttons):
    return {"text": text, "buttons": buttons}


def handle_menu(state: UserState) -> dict:
    """Show assessment type selection."""
    state.assessment_escalation = state.assessment_escalation or {"count": 0, "issue": "", "type": ""}
    return _resp(
        "**Assessment Issues — Skillserv Portal**\n\nWhich type of assessment are you facing issues with?",
        [
            {"text": "Pre-Course Quiz (PCQ)", "cb": "assessment_pcq"},
            {"text": "Post Assessment", "cb": "assessment_post"},
            {"text": "⬅️ Back to Main Menu", "cb": "main_menu"},
        ]
    )


def handle_callback(state: UserState, callback: str) -> dict:
    """Handle all assessment/pcq/post callbacks."""

    # ========== PCQ ==========
    if callback in ("assessment_pcq", "pcq"):
        state.assessment_escalation["type"] = "PCQ"
        return _resp(
            "**Pre-Course Quiz (PCQ) Issue**\n\nWhat PCQ-related issue are you facing?",
            [
                {"text": "Where is the Quiz?", "cb": "pcq_where"},
                {"text": "Test Not Showing", "cb": "pcq_not_showing"},
                {"text": "Unable to Submit", "cb": "pcq_submit"},
                {"text": "Exited Midway", "cb": "pcq_exited"},
                {"text": "Joined Late", "cb": "pcq_time"},
                {"text": "Other PCQ Issue", "cb": "pcq_other"},
                {"text": "⬅️ Back", "cb": "assessment"},
            ]
        )

    if callback == "pcq_where":
        _track(state, "Where is the Quiz", "PCQ")
        return _resp(
            "**Where is the Quiz?**\n\n"
            "To access the PCQ quiz on Skillserv:\n\n"
            "1. Login to the Skillserv portal.\n"
            "2. Go to your dashboard.\n"
            "3. Look for the PCQ / Assessment section.\n"
            "4. Click on the active quiz link.\n"
            "5. If not visible, press Ctrl+F5 to hard refresh.\n"
            "6. Or close and reopen the browser, then login again.\n\n"
            "Select an option below if you need further help.",
            [
                {"text": "Still Not Visible", "cb": "assessment_still_not_working"},
                {"text": "⬅️ Back", "cb": "assessment_pcq"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    if callback == "pcq_not_showing":
        _track(state, "Test Not Showing", "PCQ")
        return _resp(
            "**Test Not Showing**\n\n"
            "If the PCQ test is not showing, please try the following:\n\n"
            "1. Refresh the page once.\n"
            "2. Ensure you are logged in using the registered email ID.\n"
            "3. Close the browser tab and login again.\n"
            "4. Try accessing the portal from another device or browser.\n\n"
            "Select an option below if you need further help.",
            [
                {"text": "Tried All Steps", "cb": "assessment_still_not_working"},
                {"text": "⬅️ Back", "cb": "assessment_pcq"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    if callback == "pcq_submit":
        _track(state, "Unable to Submit", "PCQ")
        return _resp(
            "**Unable to Submit**\n\n"
            "If you are unable to submit the PCQ:\n\n"
            "1. Ensure all questions are attempted.\n"
            "2. Check your internet connection.\n"
            "3. Wait for a few seconds and try submitting again.\n"
            "4. Avoid refreshing the page repeatedly.\n\n"
            "Select an option below if you need further help.",
            [
                {"text": "Still Unable to Submit", "cb": "assessment_still_not_working"},
                {"text": "⬅️ Back", "cb": "assessment_pcq"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    if callback == "pcq_exited":
        _track(state, "Exited Midway", "PCQ")
        return _resp(
            "**Exited Midway**\n\n"
            "If you exited the PCQ midway:\n\n"
            "1. Login again and check if the quiz resumes automatically.\n"
            "2. In most cases, re-entry depends on system rules.\n\n"
            "If the test does not resume, you may need support assistance.\n\n"
            "Select an option below if you need further help.",
            [
                {"text": "Cannot Rejoin", "cb": "assessment_still_not_working"},
                {"text": "⬅️ Back", "cb": "assessment_pcq"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    if callback == "pcq_time":
        _track(state, "Joined Late", "PCQ")
        return _resp(
            "**Joined Late**\n\n"
            "Since you joined late, you won't be able to access the exam.\n\n"
            "The PCQ is only accessible during the scheduled time window. "
            "Late entries are not permitted by the system.\n\n"
            "If you believe this is an error, you can talk to our support team.\n\n"
            "Select an option below if you need further help.",
            [
                {"text": "Talk to Support", "cb": "assessment_still_not_working"},
                {"text": "⬅️ Back", "cb": "assessment_pcq"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    if callback == "pcq_other":
        state.assessment_other_mode = {"active": True, "type": "PCQ"}
        _track(state, "Other PCQ Issue", "PCQ")
        return _resp(
            "**Other PCQ Issue**\n\n"
            "Please briefly describe the PCQ issue you are facing.\n"
            "Our AI will analyze and provide help.",
            [
                {"text": "⬅️ Back", "cb": "assessment_pcq"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    # ========== POST ASSESSMENT ==========
    if callback in ("assessment_post", "post"):
        state.assessment_escalation["type"] = "Post Assessment"
        return _resp(
            "**Post Assessment Issue**\n\nWhat Post Assessment issue are you facing?",
            [
                {"text": "Assessment Not Visible", "cb": "post_not_visible"},
                {"text": "Test Not Loading", "cb": "post_not_loading"},
                {"text": "Unable to Submit", "cb": "post_submit"},
                {"text": "Exited Midway", "cb": "post_exited"},
                {"text": "Time Window Issue", "cb": "post_time"},
                {"text": "Other Post Assessment Issue", "cb": "post_other"},
                {"text": "⬅️ Back", "cb": "assessment"},
            ]
        )

    if callback == "post_not_visible":
        _track(state, "Assessment Not Visible", "Post Assessment")
        return _resp(
            "**Assessment Not Visible**\n\n"
            "To access the Post Assessment on Skillserv:\n\n"
            "1. Login to the Skillserv portal.\n"
            "2. Go to your dashboard.\n"
            "3. Look for the Assessment / Test section.\n"
            "4. Ensure the assessment time window is active.\n"
            "5. Press Ctrl+F5 to hard refresh.\n"
            "6. Or close and reopen the browser, then login again.\n\n"
            "Select an option below if you need further help.",
            [
                {"text": "Still Not Visible", "cb": "assessment_still_not_working"},
                {"text": "⬅️ Back", "cb": "assessment_post"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    if callback == "post_not_loading":
        _track(state, "Test Not Loading", "Post Assessment")
        return _resp(
            "**Test Not Loading**\n\n"
            "If the Post Assessment is not loading, please try:\n\n"
            "1. Refresh the page once.\n"
            "2. Clear browser cache and cookies.\n"
            "3. Try in Incognito/Private mode.\n"
            "4. Try accessing from another device or browser.\n"
            "5. Check your internet connection.\n\n"
            "Select an option below if you need further help.",
            [
                {"text": "Tried All Steps", "cb": "assessment_still_not_working"},
                {"text": "⬅️ Back", "cb": "assessment_post"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    if callback == "post_submit":
        _track(state, "Unable to Submit", "Post Assessment")
        return _resp(
            "**Unable to Submit**\n\n"
            "If you are unable to submit the Post Assessment:\n\n"
            "1. Ensure all questions are attempted.\n"
            "2. Check your internet connection.\n"
            "3. Wait for a few seconds and try submitting again.\n"
            "4. Avoid refreshing the page repeatedly.\n"
            "5. Check if you are within the allowed time window.\n\n"
            "Select an option below if you need further help.",
            [
                {"text": "Still Unable to Submit", "cb": "assessment_still_not_working"},
                {"text": "⬅️ Back", "cb": "assessment_post"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    if callback == "post_exited":
        _track(state, "Exited Midway", "Post Assessment")
        return _resp(
            "**Exited Midway**\n\n"
            "If you exited the Post Assessment midway:\n\n"
            "1. Login again and check if the test resumes automatically.\n"
            "2. In most cases, re-entry depends on system rules.\n\n"
            "If the test does not resume, you may need support assistance.\n\n"
            "Select an option below if you need further help.",
            [
                {"text": "Cannot Rejoin", "cb": "assessment_still_not_working"},
                {"text": "⬅️ Back", "cb": "assessment_post"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    if callback == "post_time":
        _track(state, "Time Window Issue", "Post Assessment")
        return _resp(
            "**Time Window Issue**\n\n"
            "Post Assessments are only accessible within a specific time window.\n\n"
            "Please check:\n"
            "1. Is your assessment time window currently active?\n"
            "2. Check the scheduled time in your course calendar.\n"
            "3. Ensure you are attempting within the allowed hours.\n"
            "4. If active, try refreshing the page (Ctrl+F5).\n"
            "5. Clear browser cache and try a different browser.\n\n"
            "Select an option below if you need further help.",
            [
                {"text": "Still Facing Issue", "cb": "assessment_still_not_working"},
                {"text": "⬅️ Back", "cb": "assessment_post"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    if callback == "post_other":
        state.assessment_other_mode = {"active": True, "type": "Post Assessment"}
        _track(state, "Other Post Assessment Issue", "Post Assessment")
        return _resp(
            "**Other Post Assessment Issue**\n\n"
            "Please briefly describe the Post Assessment issue you are facing.\n"
            "Our AI will analyze and provide help.",
            [
                {"text": "⬅️ Back", "cb": "assessment_post"},
                {"text": "🏠 Main Menu", "cb": "main_menu"},
            ]
        )

    # ========== STILL NOT WORKING (escalation) ==========
    if callback in ("assessment_still_not_working", "pcq_still_not_working"):
        state.assessment_escalation["count"] = state.assessment_escalation.get("count", 0) + 1
        attempts = state.assessment_escalation["count"]
        assessment_type = state.assessment_escalation.get("type", "Assessment")

        if attempts >= 2:
            return {
                "text": "", "buttons": [],
                "_trigger_escalation": True,
                "_issue": state.assessment_escalation.get("issue", "Assessment Issue"),
                "_type": assessment_type,
            }
        else:
            back_cb = "assessment_pcq" if assessment_type == "PCQ" else "assessment_post"
            return _resp(
                "**Let's try once more**\n\n"
                "Please try the following:\n"
                "1. Clear your browser cache\n"
                "2. Try in Incognito/Private mode\n"
                "3. Use a different browser or device\n\n"
                f"_Attempt {attempts}/2 - After 2 attempts, we'll connect you with support._\n\n"
                "Select an option below if you need further help.",
                [
                    {"text": "Still Not Working", "cb": "assessment_still_not_working"},
                    {"text": "⬅️ Back", "cb": back_cb},
                    {"text": "🏠 Main Menu", "cb": "main_menu"},
                ]
            )

    # ========== FIXED ==========
    if callback in ("assessment_fixed", "pcq_fixed", "post_fixed"):
        state.assessment_escalation = {"count": 0, "issue": "", "type": ""}
        return _resp("Great! Your assessment issue is resolved.\n\nBest of luck with your assessment!",
                      [{"text": "🏠 Main Menu", "cb": "main_menu"}])

    # ========== BACK ==========
    if callback in ("assessment_back_menu", "pcq_back_menu"):
        from core.flows.menu import get_menu
        return get_menu()

    return handle_menu(state)


def _track(state: UserState, issue: str, assessment_type: str):
    state.assessment_escalation["issue"] = issue
    state.assessment_escalation["type"] = assessment_type
