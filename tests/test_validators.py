"""Tests for validators module."""
import pytest
from utils.validators import is_valid_email


def test_valid_emails():
    """Test valid email addresses."""
    valid_emails = [
        "test@example.com",
        "user.name@example.com",
        "user+tag@example.com",
        "user_name@example.com",
        "user123@example.com",
        "test@subdomain.example.com",
        "test@example.co.uk",
        "a@b.co",
    ]
    
    for email in valid_emails:
        assert is_valid_email(email), f"Expected {email} to be valid"


def test_invalid_emails():
    """Test invalid email addresses."""
    invalid_emails = [
        "",
        "notanemail",
        "@example.com",
        "user@",
        "user @example.com",
        "user@.com",
        "user@example.",
        "user@example",
        "user@-example.com",
        "user@example-.com",
    ]
    
    for email in invalid_emails:
        assert not is_valid_email(email), f"Expected {email} to be invalid"


def test_edge_cases():
    """Test edge cases for email validation."""
    # Very long but valid
    assert is_valid_email("a" * 50 + "@example.com")
    
    # Multiple subdomains
    assert is_valid_email("test@a.b.c.example.com")
    
    # Numbers in domain
    assert is_valid_email("test@123example.com")
    
    # Single character parts
    assert is_valid_email("a@b.co")
