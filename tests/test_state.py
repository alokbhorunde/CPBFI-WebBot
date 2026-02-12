"""Tests for UserState class."""
import pytest
from core.state import UserState


def test_user_state_creation():
    """Test creating a new UserState."""
    state = UserState()
    assert state.login_escalation == {"count": 0, "portal": "", "issue": ""}
    assert state.assessment_escalation == {"count": 0, "issue": "", "type": ""}
    assert state.lms_escalation == {"count": 0, "issue": ""}
    assert state.detail_collection is None
    assert state.login_other_mode is None
    assert state.assessment_other_mode is None
    assert state.lms_other_mode is False
    assert state.ai_chat_mode is False
    assert state.other_issue_mode is False


def test_clear_all():
    """Test clearing all state."""
    state = UserState()
    # Set some values
    state.login_escalation = {"count": 2, "portal": "LMS", "issue": "Can't login"}
    state.detail_collection = {"step": "name", "category": "login"}
    state.ai_chat_mode = True
    
    # Clear all
    state.clear_all()
    
    # Verify reset
    assert state.login_escalation == {"count": 0, "portal": "", "issue": ""}
    assert state.detail_collection is None
    assert state.ai_chat_mode is False


def test_to_dict():
    """Test converting state to dict."""
    state = UserState()
    state.ai_chat_mode = True
    state.login_escalation = {"count": 1, "portal": "PCQ", "issue": "Login error"}
    
    state_dict = state.to_dict()
    
    assert isinstance(state_dict, dict)
    assert state_dict["ai_chat_mode"] is True
    assert state_dict["login_escalation"]["count"] == 1


def test_from_dict():
    """Test creating state from dict."""
    data = {
        "ai_chat_mode": True,
        "login_escalation": {"count": 2, "portal": "LMS", "issue": "Issue"},
        "detail_collection": {"step": "email", "category": "assessment"}
    }
    
    state = UserState.from_dict(data)
    
    assert state.ai_chat_mode is True
    assert state.login_escalation["count"] == 2
    assert state.detail_collection["step"] == "email"


def test_from_dict_empty():
    """Test creating state from empty dict."""
    state = UserState.from_dict({})
    assert state.login_escalation == {"count": 0, "portal": "", "issue": ""}


def test_from_dict_none():
    """Test creating state from None."""
    state = UserState.from_dict(None)
    assert state.login_escalation == {"count": 0, "portal": "", "issue": ""}


def test_is_collecting_details():
    """Test is_collecting_details method."""
    state = UserState()
    
    # No collection
    assert state.is_collecting_details() is False
    
    # Collection started
    state.detail_collection = {"step": "name", "category": "login"}
    assert state.is_collecting_details() is True
    
    # Collection complete (step is None)
    state.detail_collection = {"step": None, "category": "login"}
    assert state.is_collecting_details() is False


def test_is_collecting_details_edge_cases():
    """Test is_collecting_details edge cases."""
    state = UserState()
    
    # Empty dict
    state.detail_collection = {}
    assert state.is_collecting_details() is False
    
    # Missing step key
    state.detail_collection = {"category": "login"}
    assert state.is_collecting_details() is False
