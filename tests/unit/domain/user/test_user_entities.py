"""Tests for user domain entities"""

import pytest
from uuid import uuid4
from datetime import datetime

from domain.user.entities import User, UserProfile, UserCreateRequest, UserUpdateRequest


class TestUser:
    """Test User entity"""

    def test_create_user_with_all_fields(self):
        """Test creating user with all fields"""
        user_id = uuid4()
        created_at = datetime.now()
        
        user = User(
            id=user_id,
            telegram_id=123456789,
            username="testuser",
            language_code="en",
            is_active=True,
            created_at=created_at,
            updated_at=created_at
        )
        
        assert user.id == user_id
        assert user.telegram_id == 123456789
        assert user.username == "testuser"
        assert user.language_code == "en"
        assert user.is_active is True
        assert user.created_at == created_at
        assert user.updated_at == created_at

    def test_create_user_with_minimal_fields(self):
        """Test creating user with minimal required fields"""
        user = User(telegram_id=123456789)
        
        assert user.telegram_id == 123456789
        assert user.username is None
        assert user.language_code == "ru"  # Default value
        assert user.is_active is True  # Default value
        assert user.id is not None  # Should be auto-generated
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_defaults(self):
        """Test user default values"""
        user = User(telegram_id=123456789)
        
        assert user.is_active is True
        assert user.language_code == "ru"
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_user_serialization(self):
        """Test User serialization"""
        user = User(
            telegram_id=123456789,
            username="testuser",
            language_code="en",
            is_active=True
        )
        
        data = user.model_dump()
        assert data["telegram_id"] == 123456789
        assert data["username"] == "testuser"
        assert data["language_code"] == "en"
        assert data["is_active"] is True

    def test_user_deserialization(self):
        """Test User deserialization"""
        data = {
            "telegram_id": 123456789,
            "username": "testuser",
            "language_code": "en",
            "is_active": True
        }
        
        user = User.model_validate(data)
        assert user.telegram_id == 123456789
        assert user.username == "testuser"
        assert user.language_code == "en"
        assert user.is_active is True

    def test_user_equality(self):
        """Test user equality comparison"""
        user_id = uuid4()
        
        user1 = User(
            id=user_id,
            telegram_id=123456789,
            username="testuser"
        )
        user2 = User(
            id=user_id,
            telegram_id=123456789,
            username="testuser"
        )
        
        # Users with same ID should be considered equal
        assert user1.id == user2.id


class TestUserProfile:
    """Test UserProfile entity"""

    def test_create_user_profile_with_all_fields(self):
        """Test creating user profile with all fields"""
        user_id = uuid4()
        profile = UserProfile(
            user_id=user_id,
            telegram_id=123456789,
            notification_preferences={"email": True},
            booking_preferences={"default_guests": 2},
            interaction_count=5,
            last_interaction_at=datetime.now()
        )
        
        assert profile.user_id == user_id
        assert profile.telegram_id == 123456789
        assert profile.notification_preferences == {"email": True}
        assert profile.booking_preferences == {"default_guests": 2}
        assert profile.interaction_count == 5
        assert profile.last_interaction_at is not None

    def test_create_user_profile_with_minimal_fields(self):
        """Test creating user profile with minimal fields"""
        user_id = uuid4()
        profile = UserProfile(
            user_id=user_id,
            telegram_id=123456789
        )
        
        assert profile.user_id == user_id
        assert profile.telegram_id == 123456789
        assert profile.notification_preferences == {}
        assert profile.booking_preferences == {}
        assert profile.interaction_count == 0
        assert profile.last_interaction_at is None


class TestUserCreateRequest:
    """Test UserCreateRequest entity"""

    def test_create_request_with_all_fields(self):
        """Test creating user create request with all fields"""
        request = UserCreateRequest(
            telegram_id=123456789,
            username="testuser",
            language_code="en"
        )
        
        assert request.telegram_id == 123456789
        assert request.username == "testuser"
        assert request.language_code == "en"

    def test_create_request_with_minimal_fields(self):
        """Test creating user create request with minimal fields"""
        request = UserCreateRequest(telegram_id=123456789)
        
        assert request.telegram_id == 123456789
        assert request.username is None
        assert request.language_code == "ru"  # Default value


class TestUserUpdateRequest:
    """Test UserUpdateRequest entity"""

    def test_update_request_with_all_fields(self):
        """Test creating user update request with all fields"""
        request = UserUpdateRequest(
            username="newusername",
            language_code="en",
            is_active=False
        )
        
        assert request.username == "newusername"
        assert request.language_code == "en"
        assert request.is_active is False

    def test_update_request_with_minimal_fields(self):
        """Test creating user update request with minimal fields"""
        request = UserUpdateRequest()
        
        assert request.username is None
        assert request.language_code is None
        assert request.is_active is None