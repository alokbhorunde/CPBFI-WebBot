"""UserState — replaces all module-level dicts from the Telegram bot.

Telegram bot had:
  login.py:      user_login_other_mode, user_escalation_attempts, user_detail_collection
  assessment.py: user_assessment_other_mode, user_assessment_escalation_attempts, user_assessment_detail_collection
  lms.py:        user_lms_other_mode, user_lms_escalation_attempts, user_lms_detail_collection
  other.py:      user_ai_mode
  ai_chat.py:    user_ai_chat_mode

This single class replaces ALL of them — serialized as JSON into sessions.state column.
"""
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class UserState:
    # Escalation counters (per category)
    login_escalation: dict = field(default_factory=lambda: {"count": 0, "portal": "", "issue": ""})
    assessment_escalation: dict = field(default_factory=lambda: {"count": 0, "issue": "", "type": ""})
    lms_escalation: dict = field(default_factory=lambda: {"count": 0, "issue": ""})

    # Detail collection (name → email → bfsi form)
    detail_collection: Optional[dict] = None

    # "Other" modes (free-text AI analysis)
    login_other_mode: Optional[str] = None        # portal name or None
    assessment_other_mode: Optional[dict] = None   # {"active": bool, "type": str} or None
    lms_other_mode: bool = False

    # Special modes
    ai_chat_mode: bool = False
    other_issue_mode: bool = False

    def clear_all(self):
        """Reset everything — same as clear_all_user_states() in general.py."""
        self.login_escalation = {"count": 0, "portal": "", "issue": ""}
        self.assessment_escalation = {"count": 0, "issue": "", "type": ""}
        self.lms_escalation = {"count": 0, "issue": ""}
        self.detail_collection = None
        self.login_other_mode = None
        self.assessment_other_mode = None
        self.lms_other_mode = False
        self.ai_chat_mode = False
        self.other_issue_mode = False

    def is_collecting_details(self) -> bool:
        return (self.detail_collection is not None
                and self.detail_collection.get("step") is not None)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "UserState":
        if not data:
            return cls()
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
