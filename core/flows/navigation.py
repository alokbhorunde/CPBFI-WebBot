"""Navigation flow — all 7 student guides ported from TG bot handlers/navigation.py."""
from core.state import UserState


def _resp(text, buttons):
    return {"text": text, "buttons": buttons}


def handle_callback(state: UserState, callback: str) -> dict:
    """Handle all navhelp/nav_* callbacks."""

    if callback == "navhelp":
        return _resp(
            "**Navigation Help**\n\nSelect a guide to learn how to use the platform:",
            [
                {"text": "How to Use Platform (Student)", "cb": "nav_student"},
                {"text": "⬅️ Back to Main Menu", "cb": "main_menu"},
            ]
        )

    if callback == "nav_student":
        return _resp(
            "**How to Use Platform — Student Guide**\n\nSelect what you want to learn:",
            [
                {"text": "How to Login", "cb": "nav_how_login"},
                {"text": "How to Attempt PCQ", "cb": "nav_how_pcq"},
                {"text": "How to Attempt Post Assessment", "cb": "nav_how_post"},
                {"text": "How to Submit Feedback", "cb": "nav_how_feedback"},
                {"text": "How to Complete Profile", "cb": "nav_how_profile"},
                {"text": "How to Download HR Certificate", "cb": "nav_how_hr_cert"},
                {"text": "How to Download Completion Certificate", "cb": "nav_how_comp_cert"},
                {"text": "⬅️ Back", "cb": "navhelp"},
            ]
        )

    if callback == "nav_how_login":
        return _resp(
            "**How to Login**\n\n"
            "1. Open the student portal\n"
            "2. Enter your Student ID and Password\n"
            "3. Click on Login\n"
            "4. You will land on the Dashboard\n\n"
            "You're logged in!",
            [{"text": "⬅️ Back", "cb": "nav_student"}]
        )

    if callback == "nav_how_pcq":
        return _resp(
            "**How to Attempt PCQ**\n\n"
            "1. Login to the student portal\n"
            "2. You will land on the Dashboard\n"
            "3. Scroll down on the dashboard\n"
            "4. Look for the Session cards\n"
            "5. Click on your Mobilization Session\n"
            "6. Inside the session, click on PCQ\n"
            "7. Click on Begin PCQ\n"
            "8. Answer all questions\n"
            "9. Click Submit\n"
            "10. Your PCQ score will be displayed\n\n"
            "PCQ completed successfully!",
            [{"text": "⬅️ Back", "cb": "nav_student"}]
        )

    if callback == "nav_how_post":
        return _resp(
            "**How to Attempt Post Assessment**\n\n"
            "1. Login to the portal\n"
            "2. Go to Dashboard\n"
            "3. Scroll and open your Mobilization Session\n"
            "4. Click on Post Assessment\n"
            "5. Click Begin\n"
            "6. Submit the assessment\n"
            "7. View your score\n\n"
            "Post Assessment completed!",
            [{"text": "⬅️ Back", "cb": "nav_student"}]
        )

    if callback == "nav_how_feedback":
        return _resp(
            "**How to Submit Feedback**\n\n"
            "1. Login to the portal\n"
            "2. Go to Dashboard\n"
            "3. Scroll to the last session card\n"
            "4. Click on Feedback\n"
            "5. Click Begin\n"
            "6. Fill the feedback form\n"
            "7. Click Submit\n\n"
            "Feedback submitted successfully!",
            [{"text": "⬅️ Back", "cb": "nav_student"}]
        )

    if callback == "nav_how_profile":
        return _resp(
            "**How to Complete Your Profile**\n\n"
            "1. Login to the portal\n"
            "2. After login, you will be redirected to Profile\n"
            "3. Complete Basic Details\n"
            "4. Click Save & Continue\n"
            "5. Complete Advanced Details\n"
            "6. Click Save & Continue\n"
            "7. Complete Resume Details\n"
            "8. Click Save\n"
            "9. You will be redirected to Dashboard\n\n"
            "Profile completed successfully!",
            [{"text": "⬅️ Back", "cb": "nav_student"}]
        )

    if callback == "nav_how_hr_cert":
        return _resp(
            "**How to Download HR Certificate**\n\n"
            "1. Login to the portal\n"
            "2. Go to Dashboard\n"
            "3. Scroll down\n"
            "4. Click on Certificates section\n"
            "5. Click on HR Certificate\n"
            "6. Certificate will download automatically\n\n"
            "HR Certificate downloaded!",
            [{"text": "⬅️ Back", "cb": "nav_student"}]
        )

    if callback == "nav_how_comp_cert":
        return _resp(
            "**How to Download Completion Certificate**\n\n"
            "1. Login to the portal\n"
            "2. Go to Dashboard\n"
            "3. Scroll down\n"
            "4. Click on Certificates section\n"
            "5. Click on Completion Certificate\n"
            "6. Certificate will download automatically\n\n"
            "Completion Certificate downloaded!",
            [{"text": "⬅️ Back", "cb": "nav_student"}]
        )

    if callback == "nav_back_menu":
        from core.flows.menu import get_menu
        return get_menu()

    # Fallback
    return _resp("**Navigation Help**\n\nSelect a guide:", [
        {"text": "How to Use Platform (Student)", "cb": "nav_student"},
        {"text": "⬅️ Back to Main Menu", "cb": "main_menu"},
    ])
