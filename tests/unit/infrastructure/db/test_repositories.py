"""Tests for database repositories"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from domain.user.entities import User, UserCreateRequest, UserUpdateRequest
from infrastructure.db.models.user import UserModel
from infrastructure.db.repositories.user_repository import UserRepository


class TestUserRepository:
    """Test UserRepository"""

    @pytest.fixture
    def mock_session(self):
        """Mock async session"""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture  
    def user_repository(self, mock_session):
        """UserRepository instance with mocked session"""
        return UserRepository(mock_session)

    @pytest.fixture
    def sample_user_model(self):
        """Sample user model"""
        return UserModel(
            id=uuid4(),
            telegram_id=123456789,
            username="testuser",
            language_code="en",
            is_active=True
        )

    @pytest.fixture
    def sample_user_create_request(self):
        """Sample user create request"""
        return UserCreateRequest(
            telegram_id=123456789,
            username="testuser",
            language_code="en"
        )

    async def test_find_by_telegram_id_success(self, user_repository, mock_session, sample_user_model):
        """Test finding user by Telegram ID successfully"""
        # Setup mock
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user_model
        mock_session.execute.return_value = mock_result

        # Execute
        result = await user_repository.find_by_telegram_id(123456789)

        # Verify
        assert result == sample_user_model
        mock_session.execute.assert_called_once()

    async def test_find_by_telegram_id_not_found(self, user_repository, mock_session):
        """Test finding user by Telegram ID when not found"""
        # Setup mock
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Execute
        result = await user_repository.find_by_telegram_id(999999999)

        # Verify
        assert result is None
        mock_session.execute.assert_called_once()

    async def test_create_from_telegram_user(self, user_repository, sample_user_create_request, sample_user_model):
        """Test creating user from Telegram user data"""
        # Mock the create method from base repository
        user_repository.create = AsyncMock(return_value=sample_user_model)

        # Execute
        result = await user_repository.create_from_telegram_user(sample_user_create_request)

        # Verify
        assert result == sample_user_model
        user_repository.create.assert_called_once()

    async def test_update_profile_success(self, user_repository, sample_user_model):
        """Test updating user profile successfully"""
        # Setup mocks
        user_repository.find_by_telegram_id = AsyncMock(return_value=sample_user_model)
        user_repository.update = AsyncMock(return_value=sample_user_model)

        update_request = UserUpdateRequest(
            username="newusername",
            language_code="ru"
        )

        # Execute
        result = await user_repository.update_profile(123456789, update_request)

        # Verify
        assert result == sample_user_model
        user_repository.find_by_telegram_id.assert_called_once_with(123456789)
        user_repository.update.assert_called_once()

    async def test_update_profile_user_not_found(self, user_repository):
        """Test updating profile when user not found"""
        # Setup mock
        user_repository.find_by_telegram_id = AsyncMock(return_value=None)

        update_request = UserUpdateRequest(username="newusername")

        # Execute
        result = await user_repository.update_profile(999999999, update_request)

        # Verify
        assert result is None
        user_repository.find_by_telegram_id.assert_called_once_with(999999999)

    async def test_get_or_create_user_existing(self, user_repository, sample_user_create_request, sample_user_model):
        """Test getting existing user"""
        # Setup mock
        user_repository.find_by_telegram_id = AsyncMock(return_value=sample_user_model)

        # Execute
        result = await user_repository.get_or_create_user(sample_user_create_request)

        # Verify
        assert result == sample_user_model
        user_repository.find_by_telegram_id.assert_called_once_with(123456789)

    async def test_get_or_create_user_new(self, user_repository, sample_user_create_request, sample_user_model):
        """Test creating new user"""
        # Setup mocks
        user_repository.find_by_telegram_id = AsyncMock(return_value=None)
        user_repository.create_from_telegram_user = AsyncMock(return_value=sample_user_model)

        # Execute
        result = await user_repository.get_or_create_user(sample_user_create_request)

        # Verify
        assert result == sample_user_model
        user_repository.find_by_telegram_id.assert_called_once_with(123456789)
        user_repository.create_from_telegram_user.assert_called_once_with(sample_user_create_request)

    async def test_deactivate_user_success(self, user_repository, sample_user_model):
        """Test deactivating user successfully"""
        # Setup mocks
        user_repository.find_by_telegram_id = AsyncMock(return_value=sample_user_model)
        user_repository.update = AsyncMock(return_value=sample_user_model)

        # Execute
        result = await user_repository.deactivate_user(123456789)

        # Verify
        assert result is True
        user_repository.find_by_telegram_id.assert_called_once_with(123456789)
        user_repository.update.assert_called_once()

    async def test_deactivate_user_not_found(self, user_repository):
        """Test deactivating user when not found"""
        # Setup mock
        user_repository.find_by_telegram_id = AsyncMock(return_value=None)

        # Execute
        result = await user_repository.deactivate_user(999999999)

        # Verify
        assert result is False
        user_repository.find_by_telegram_id.assert_called_once_with(999999999)

    def test_to_domain_entity(self, user_repository, sample_user_model):
        """Test converting database model to domain entity"""
        # Execute
        result = user_repository._to_domain_entity(sample_user_model)

        # Verify
        assert isinstance(result, User)
        assert result.id == sample_user_model.id
        assert result.telegram_id == sample_user_model.telegram_id
        assert result.username == sample_user_model.username
        assert result.language_code == sample_user_model.language_code
        assert result.is_active == sample_user_model.is_active