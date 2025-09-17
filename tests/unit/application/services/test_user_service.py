"""Tests for UserService"""

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from domain.user.entities import User
from application.services.user_service import UserService


class TestUserService:
    """Test UserService"""

    @pytest.fixture
    def mock_user_repository(self):
        """Mock user repository"""
        return AsyncMock()

    @pytest.fixture
    def user_service(self, mock_user_repository):
        """UserService instance with mocked repository"""
        return UserService(mock_user_repository)

    @pytest.fixture
    def sample_user(self):
        """Sample user entity"""
        return User(
            id=uuid4(),
            telegram_id=123456789,
            username="testuser",
            language_code="en",
            is_active=True
        )

    async def test_create_user(self, user_service, mock_user_repository, sample_user):
        """Test creating a user"""
        # Setup mock
        mock_user_repository.create.return_value = sample_user

        # Execute
        result = await user_service.create_user(sample_user)

        # Verify
        assert result == sample_user
        mock_user_repository.create.assert_called_once_with(sample_user)

    async def test_get_user_by_id(self, user_service, mock_user_repository, sample_user):
        """Test getting user by ID"""
        # Setup mock
        user_id = sample_user.id
        mock_user_repository.get_by_id.return_value = sample_user

        # Execute
        result = await user_service.get_user_by_id(user_id)

        # Verify
        assert result == sample_user
        mock_user_repository.get_by_id.assert_called_once_with(user_id)

    async def test_get_user_by_telegram_id(self, user_service, mock_user_repository, sample_user):
        """Test getting user by Telegram ID"""
        # Setup mock
        mock_user_repository.get_by_telegram_id.return_value = sample_user

        # Execute
        result = await user_service.get_user_by_telegram_id(123456789)

        # Verify
        assert result == sample_user
        mock_user_repository.get_by_telegram_id.assert_called_once_with(123456789)

    async def test_update_user(self, user_service, mock_user_repository, sample_user):
        """Test updating a user"""
        # Setup mock
        mock_user_repository.update.return_value = sample_user

        # Execute
        result = await user_service.update_user(sample_user)

        # Verify
        assert result == sample_user
        mock_user_repository.update.assert_called_once_with(sample_user)

    async def test_deactivate_user_success(self, user_service, mock_user_repository, sample_user):
        """Test deactivating a user successfully"""
        # Setup mock
        user_id = sample_user.id
        mock_user_repository.get_by_id.return_value = sample_user
        mock_user_repository.update.return_value = sample_user

        # Execute
        result = await user_service.deactivate_user(user_id)

        # Verify
        assert result is True
        mock_user_repository.get_by_id.assert_called_once_with(user_id)
        mock_user_repository.update.assert_called_once()
        # Verify that user was deactivated
        assert sample_user.is_active is False

    async def test_deactivate_user_not_found(self, user_service, mock_user_repository):
        """Test deactivating a non-existent user"""
        # Setup mock
        user_id = uuid4()
        mock_user_repository.get_by_id.return_value = None

        # Execute
        result = await user_service.deactivate_user(user_id)

        # Verify
        assert result is False
        mock_user_repository.get_by_id.assert_called_once_with(user_id)
        mock_user_repository.update.assert_not_called()

    async def test_find_user_by_username(self, user_service, mock_user_repository, sample_user):
        """Test finding user by username"""
        # Setup mock
        mock_user_repository.find_by_username.return_value = sample_user

        # Execute
        result = await user_service.find_user_by_username("testuser")

        # Verify
        assert result == sample_user
        mock_user_repository.find_by_username.assert_called_once_with("testuser")

    async def test_get_all_users(self, user_service, mock_user_repository, sample_user):
        """Test getting all users"""
        # Setup mock
        users = [sample_user]
        mock_user_repository.get_all.return_value = users

        # Execute
        result = await user_service.get_all_users()

        # Verify
        assert result == users
        mock_user_repository.get_all.assert_called_once()

    async def test_register_or_update_telegram_user_new(self, user_service, mock_user_repository, sample_user):
        """Test registering a new Telegram user"""
        # Setup mock
        mock_user_repository.get_by_telegram_id.return_value = None
        mock_user_repository.create.return_value = sample_user

        # Execute
        result = await user_service.register_or_update_telegram_user(
            telegram_id=123456789,
            username="testuser",
            language_code="en"
        )

        # Verify
        assert result == sample_user
        mock_user_repository.get_by_telegram_id.assert_called_once_with(123456789)
        mock_user_repository.create.assert_called_once()

    async def test_register_or_update_telegram_user_existing(self, user_service, mock_user_repository, sample_user):
        """Test updating an existing Telegram user"""
        # Setup mock
        mock_user_repository.get_by_telegram_id.return_value = sample_user
        mock_user_repository.update.return_value = sample_user

        # Execute
        result = await user_service.register_or_update_telegram_user(
            telegram_id=123456789,
            username="newusername",
            language_code="ru"
        )

        # Verify
        assert result == sample_user
        mock_user_repository.get_by_telegram_id.assert_called_once_with(123456789)
        mock_user_repository.update.assert_called_once_with(sample_user)
        # Verify that user was updated
        assert sample_user.username == "newusername"
        assert sample_user.language_code == "ru"