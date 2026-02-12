"""Tests for escalation module."""
import pytest
from core.state import UserState
from core.escalation import start_collection, process_input


def test_start_collection_login():
    """Test starting escalation collection for login."""
    state = UserState()
    
    result = start_collection(state, "login", "Can't access portal", portal="LMS")
    
    assert state.detail_collection is not None
    assert state.detail_collection["step"] == "name"
    assert state.detail_collection["category"] == "login"
    assert state.detail_collection["issue"] == "Can't access portal"
    assert state.detail_collection["portal"] == "LMS"
    assert "Step 1/3" in result["text"]
    assert "Full Name" in result["text"]
    assert len(result["buttons"]) == 1
    assert result["buttons"][0]["cb"] == "login_cancel_escalation"


def test_start_collection_assessment():
    """Test starting escalation collection for assessment (has describe step)."""
    state = UserState()
    
    result = start_collection(state, "assessment", "Quiz not loading", 
                             assessment_type="PCQ")
    
    assert state.detail_collection is not None
    assert state.detail_collection["step"] == "describe"
    assert state.detail_collection["category"] == "assessment"
    assert state.detail_collection["assessment_type"] == "PCQ"
    assert "briefly describe" in result["text"]


def test_process_input_describe_step():
    """Test processing describe step (assessment only)."""
    state = UserState()
    state.detail_collection = {
        "step": "describe",
        "category": "assessment",
        "issue": "Quiz error",
        "portal": "",
        "assessment_type": "PCQ",
        "name": "", "email": "", "bfsi": "", "description": ""
    }
    
    result = process_input(state, "I tried refreshing but it didn't work")
    
    assert state.detail_collection["description"] == "I tried refreshing but it didn't work"
    assert state.detail_collection["step"] == "name"
    assert "Step 1/3" in result["text"]


def test_process_input_name_step():
    """Test processing name input."""
    state = UserState()
    state.detail_collection = {
        "step": "name",
        "category": "login",
        "issue": "Login error",
        "portal": "LMS",
        "assessment_type": "",
        "name": "", "email": "", "bfsi": "", "description": ""
    }
    
    result = process_input(state, "John Doe")
    
    assert state.detail_collection["name"] == "John Doe"
    assert state.detail_collection["step"] == "email"
    assert "Step 2/3" in result["text"]
    assert "Email ID" in result["text"]


def test_process_input_name_too_short():
    """Test rejecting name that's too short."""
    state = UserState()
    state.detail_collection = {
        "step": "name",
        "category": "login",
        "issue": "Login error",
        "portal": "LMS",
        "assessment_type": "",
        "name": "", "email": "", "bfsi": "", "description": ""
    }
    
    result = process_input(state, "A")
    
    assert state.detail_collection["step"] == "name"  # Still on name step
    assert "at least 2 characters" in result["text"]


def test_process_input_email_step():
    """Test processing email input."""
    state = UserState()
    state.detail_collection = {
        "step": "email",
        "category": "login",
        "issue": "Login error",
        "portal": "LMS",
        "assessment_type": "",
        "name": "John Doe", "email": "", "bfsi": "", "description": ""
    }
    
    result = process_input(state, "john@example.com")
    
    assert state.detail_collection["email"] == "john@example.com"
    assert state.detail_collection["step"] == "bfsi"
    assert "Step 3/3" in result["text"]
    assert "BFSI ID" in result["text"]


def test_process_input_email_invalid():
    """Test rejecting invalid email."""
    state = UserState()
    state.detail_collection = {
        "step": "email",
        "category": "login",
        "issue": "Login error",
        "portal": "LMS",
        "assessment_type": "",
        "name": "John Doe", "email": "", "bfsi": "", "description": ""
    }
    
    result = process_input(state, "not-an-email")
    
    assert state.detail_collection["step"] == "email"  # Still on email step
    assert "valid email" in result["text"]


def test_process_input_bfsi_step():
    """Test processing BFSI ID (final step)."""
    state = UserState()
    state.detail_collection = {
        "step": "bfsi",
        "category": "login",
        "issue": "Login error",
        "portal": "LMS",
        "assessment_type": "",
        "name": "John Doe",
        "email": "john@example.com",
        "bfsi": "",
        "description": ""
    }
    
    result = process_input(state, "BFSI123456")
    
    assert state.detail_collection["bfsi"] == "BFSI123456"
    assert state.detail_collection["step"] is None
    assert state.detail_collection.get("_complete") is True
    # Email might fail since we don't have actual email config
    assert "Details Submitted" in result["text"] or "Email Could Not Be Sent" in result["text"]
