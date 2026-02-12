"""Tests for router module."""
import pytest
from core.state import UserState
from core.router import route_callback, route_text, _resp


def test_route_callback_main_menu():
    """Test routing to main menu."""
    state = UserState()
    state.ai_chat_mode = True  # Set some state
    
    result = route_callback(state, "main_menu")
    
    # Should clear state
    assert state.ai_chat_mode is False
    assert "text" in result
    assert "buttons" in result


def test_route_callback_login():
    """Test routing to login menu."""
    state = UserState()
    
    result = route_callback(state, "login")
    
    assert state.detail_collection is None
    assert "text" in result
    assert "buttons" in result


def test_route_callback_assessment():
    """Test routing to assessment menu."""
    state = UserState()
    
    result = route_callback(state, "assessment")
    
    assert state.detail_collection is None
    assert "text" in result
    assert "buttons" in result


def test_route_callback_lms():
    """Test routing to LMS menu."""
    state = UserState()
    
    result = route_callback(state, "lms")
    
    assert state.detail_collection is None
    assert "text" in result
    assert "buttons" in result


def test_route_callback_ai_chat():
    """Test entering AI chat mode."""
    state = UserState()
    
    result = route_callback(state, "ai_chat")
    
    assert state.ai_chat_mode is True
    assert "text" in result
    assert "buttons" in result


def test_route_callback_exit_ai_chat():
    """Test exiting AI chat mode."""
    state = UserState()
    state.ai_chat_mode = True
    
    result = route_callback(state, "exit_ai_chat")
    
    assert state.ai_chat_mode is False
    assert "text" in result
    assert "buttons" in result


def test_route_callback_other():
    """Test entering other issue mode."""
    state = UserState()
    
    result = route_callback(state, "other")
    
    assert state.other_issue_mode is True
    assert "text" in result
    assert "buttons" in result


def test_route_callback_fixed():
    """Test marking issues as fixed."""
    state = UserState()
    state.detail_collection = {"some": "data"}
    
    for callback in ["login_fixed", "assessment_fixed", "lms_fixed"]:
        result = route_callback(state, callback)
        
        # Should clear state
        assert state.detail_collection is None
        assert "resolved" in result["text"].lower() or "happy learning" in result["text"].lower()


def test_route_callback_cancel_escalation():
    """Test canceling escalation."""
    state = UserState()
    state.detail_collection = {"step": "name", "category": "login"}
    
    result = route_callback(state, "login_cancel_escalation")
    
    assert state.detail_collection is None
    assert "text" in result
    assert "buttons" in result


def test_route_callback_unknown():
    """Test handling unknown callback."""
    state = UserState()
    
    result = route_callback(state, "unknown_callback_xyz")
    
    # Should return main menu
    assert "text" in result
    assert "buttons" in result


@pytest.mark.asyncio
async def test_route_text_greeting():
    """Test routing greeting message."""
    state = UserState()
    state.ai_chat_mode = True
    
    result = await route_text(state, "hello")
    
    # Should clear state
    assert state.ai_chat_mode is False
    assert "Welcome" in result["text"]
    assert len(result["buttons"]) > 0


@pytest.mark.asyncio
async def test_route_text_greetings():
    """Test various greeting messages."""
    greetings = ["hi", "hello", "hey", "start", "menu", "help", "/start"]
    
    for greeting in greetings:
        state = UserState()
        result = await route_text(state, greeting)
        
        assert "Welcome" in result["text"]
        assert len(result["buttons"]) > 0


@pytest.mark.asyncio
async def test_route_text_detail_collection():
    """Test routing when collecting details."""
    state = UserState()
    state.detail_collection = {
        "step": "name",
        "category": "login",
        "issue": "Can't login",
        "portal": "LMS",
        "assessment_type": "",
        "name": "", "email": "", "bfsi": "", "description": ""
    }
    
    result = await route_text(state, "John Doe")
    
    # Should process as name input
    assert state.detail_collection["name"] == "John Doe"
    assert state.detail_collection["step"] == "email"


def test_resp_helper():
    """Test _resp helper function."""
    result = _resp("Test message", [{"text": "Button", "cb": "callback"}])
    
    assert result["text"] == "Test message"
    assert result["buttons"] == [{"text": "Button", "cb": "callback"}]
