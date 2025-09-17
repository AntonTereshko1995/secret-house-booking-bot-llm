"""Integration tests for database layer"""

import pytest
import asyncio
from uuid import uuid4
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from infrastructure.db.models.base import Base
from infrastructure.db.repositories.user_repository import UserRepositoryImpl
from infrastructure.db.repositories.booking_repository import BookingRepositoryImpl
from infrastructure.db.repositories.chat_repository import ChatRepositoryImpl
from application.services.user_service import UserService
from application.services.chat_service import ChatService
from domain.user.entities import User, UserProfile
from domain.booking.entities import Booking
from domain.chat.entities import ChatSession


class TestDatabaseIntegration:
    """Integration tests for the full database stack"""

    @pytest.fixture(scope="function")
    async def async_engine(self):
        """Create async test database engine"""
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        yield engine
        await engine.dispose()

    @pytest.fixture
    async def async_session(self, async_engine):
        """Create async database session"""
        async_session_maker = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        async with async_session_maker() as session:
            yield session

    @pytest.fixture
    def user_repository(self):
        """User repository instance"""
        return UserRepositoryImpl()

    @pytest.fixture
    def booking_repository(self):
        """Booking repository instance"""
        return BookingRepositoryImpl()

    @pytest.fixture
    def chat_repository(self):
        """Chat repository instance"""
        return ChatRepositoryImpl()

    @pytest.fixture
    def user_service(self, user_repository):
        """User service instance"""
        return UserService(user_repository)

    @pytest.fixture
    def chat_service(self, chat_repository):
        """Chat service instance"""
        return ChatService(chat_repository)


class TestUserIntegration(TestDatabaseIntegration):
    """Test user-related integration scenarios"""

    async def test_complete_user_lifecycle(self, async_session, user_repository, user_service):
        """Test complete user lifecycle from creation to deletion"""
        # Override repository session
        user_repository._session = async_session

        # 1. Create user through service
        telegram_user = await user_service.register_or_update_telegram_user(
            telegram_id=123456789,
            username="testuser",
            language_code="en"
        )

        assert telegram_user is not None
        assert telegram_user.telegram_id == 123456789
        assert telegram_user.username == "testuser"

        # 2. Retrieve user by ID
        retrieved_user = await user_service.get_user_by_id(telegram_user.id)
        assert retrieved_user is not None
        assert retrieved_user.id == telegram_user.id
        assert retrieved_user.username == "testuser"

        # 3. Retrieve user by Telegram ID
        telegram_retrieved = await user_service.get_user_by_telegram_id(123456789)
        assert telegram_retrieved is not None
        assert telegram_retrieved.id == telegram_user.id

        # 4. Update user profile
        updated_user = await user_service.register_or_update_telegram_user(
            telegram_id=123456789,
            username="updated_username",
            language_code="ru"
        )
        assert updated_user.username == "updated_username"
        assert updated_user.language_code == "ru"

        # 5. Deactivate user
        deactivated = await user_service.deactivate_user(telegram_user.id)
        assert deactivated is True

        # 6. Verify user is deactivated
        final_user = await user_service.get_user_by_id(telegram_user.id)
        assert final_user.is_active is False

    async def test_user_not_found_scenarios(self, async_session, user_repository, user_service):
        """Test scenarios where user is not found"""
        # Override repository session
        user_repository._session = async_session

        # Non-existent user by ID
        non_existent = await user_service.get_user_by_id(uuid4())
        assert non_existent is None

        # Non-existent user by Telegram ID
        non_existent_telegram = await user_service.get_user_by_telegram_id(999999999)
        assert non_existent_telegram is None

        # Try to deactivate non-existent user
        deactivated = await user_service.deactivate_user(uuid4())
        assert deactivated is False


class TestChatIntegration(TestDatabaseIntegration):
    """Test chat session integration scenarios"""

    async def test_complete_chat_session_lifecycle(self, async_session, user_repository, chat_repository, user_service, chat_service):
        """Test complete chat session lifecycle"""
        # Override repository sessions
        user_repository._session = async_session
        chat_repository._session = async_session

        # 1. Create user first
        user = await user_service.register_or_update_telegram_user(
            telegram_id=123456789,
            username="chatuser"
        )

        # 2. Initialize chat session
        chat_session = await chat_service.initialize_or_get_session(
            chat_id=123456,
            user_id=user.id,
            session_type="user"
        )

        assert chat_session is not None
        assert chat_session.chat_id == 123456
        assert chat_session.user_id == user.id
        assert chat_session.is_active is True

        # 3. Save LangGraph state
        state_data = {
            "current_step": "booking",
            "booking_data": {
                "check_in": "2024-01-15",
                "guests": 2
            }
        }
        await chat_service.save_langgraph_state(123456, state_data)

        # 4. Retrieve LangGraph state
        retrieved_state = await chat_service.get_langgraph_state(123456)
        assert retrieved_state["current_step"] == "booking"
        assert retrieved_state["booking_data"]["guests"] == 2

        # 5. Add messages to conversation history
        await chat_service.add_message_to_history(
            123456, 
            "I want to book a room", 
            "user",
            {"source": "telegram"}
        )
        await chat_service.add_message_to_history(
            123456,
            "I can help you with that",
            "assistant"
        )

        # 6. Get conversation history
        history = await chat_service.get_conversation_history(123456)
        assert len(history["messages"]) == 2
        assert history["messages"][0]["role"] == "user"
        assert history["messages"][1]["role"] == "assistant"

        # 7. Update conversation context
        context_update = {"intent": "booking", "current_state": "collecting_dates"}
        await chat_service.update_conversation_context(123456, context_update)

        updated_history = await chat_service.get_conversation_history(123456)
        assert updated_history["intent"] == "booking"
        assert updated_history["current_state"] == "collecting_dates"

        # 8. End session
        ended = await chat_service.end_session(123456)
        assert ended is True

        # 9. Verify session is inactive
        final_session = await chat_service.get_session_by_chat_id(123456)
        assert final_session.is_active is False

        # 10. Verify state is cleared
        cleared_state = await chat_service.get_langgraph_state(123456)
        assert cleared_state == {} or cleared_state is None

    async def test_multiple_chat_sessions_for_user(self, async_session, user_repository, chat_repository, user_service, chat_service):
        """Test multiple chat sessions for the same user"""
        # Override repository sessions
        user_repository._session = async_session
        chat_repository._session = async_session

        # Create user
        user = await user_service.register_or_update_telegram_user(
            telegram_id=987654321,
            username="multiuser"
        )

        # Create multiple chat sessions
        session1 = await chat_service.initialize_or_get_session(
            chat_id=111111,
            user_id=user.id
        )
        session2 = await chat_service.initialize_or_get_session(
            chat_id=222222,
            user_id=user.id
        )

        # Verify both sessions exist
        assert session1.chat_id == 111111
        assert session2.chat_id == 222222
        assert session1.user_id == session2.user_id == user.id

        # Get active sessions for user
        active_sessions = await chat_service.get_user_active_sessions(user.id)
        assert len(active_sessions) == 2

        # End one session
        await chat_service.end_session(111111)

        # Verify only one active session remains
        remaining_sessions = await chat_service.get_user_active_sessions(user.id)
        assert len(remaining_sessions) == 1
        assert remaining_sessions[0].chat_id == 222222


class TestBookingIntegration(TestDatabaseIntegration):
    """Test booking-related integration scenarios"""

    async def test_complete_booking_lifecycle(self, async_session, user_repository, booking_repository, user_service):
        """Test complete booking lifecycle"""
        # Override repository sessions
        user_repository._session = async_session
        booking_repository._session = async_session

        # 1. Create user
        user = await user_service.register_or_update_telegram_user(
            telegram_id=555666777,
            username="bookinguser"
        )

        # 2. Create booking
        booking = Booking(
            user_id=user.id,
            check_in_date=date(2024, 2, 15),
            check_out_date=date(2024, 2, 17),
            num_guests=2,
            guest_names="John Doe, Jane Doe",
            contact_phone="+1234567890",
            special_requests="Late checkout",
            status="pending",
            total_amount=Decimal("200.00"),
            rate_type="standard",
            payment_status="unpaid"
        )

        created_booking = await booking_repository.create(booking)
        assert created_booking is not None
        assert created_booking.user_id == user.id
        assert created_booking.status == "pending"

        # 3. Retrieve booking by ID
        retrieved_booking = await booking_repository.get_by_id(created_booking.id)
        assert retrieved_booking is not None
        assert retrieved_booking.check_in_date == date(2024, 2, 15)
        assert retrieved_booking.num_guests == 2

        # 4. Get user bookings
        user_bookings = await booking_repository.get_by_user_id(user.id)
        assert len(user_bookings) == 1
        assert user_bookings[0].id == created_booking.id

        # 5. Update booking status
        created_booking.status = "confirmed"
        created_booking.payment_status = "paid"
        updated_booking = await booking_repository.update(created_booking)
        assert updated_booking.status == "confirmed"
        assert updated_booking.payment_status == "paid"

        # 6. Find bookings by status
        confirmed_bookings = await booking_repository.find_by_status("confirmed")
        assert len(confirmed_bookings) == 1
        assert confirmed_bookings[0].id == created_booking.id

        # 7. Find bookings by date range
        date_range_bookings = await booking_repository.find_by_date_range("2024-02-01", "2024-02-28")
        assert len(date_range_bookings) == 1
        assert date_range_bookings[0].id == created_booking.id

        # 8. Modify booking level with audit trail
        modified_booking = await booking_repository.modify_booking_level(
            created_booking.id,
            "premium",
            "Customer upgrade request"
        )
        assert modified_booking.rate_type == "premium"
        assert "upgrade request" in modified_booking.notes

        # 9. Get booking modifications
        modifications = await booking_repository.get_booking_modifications(created_booking.id)
        assert len(modifications) >= 1

        # 10. Delete booking
        deleted = await booking_repository.delete(created_booking.id)
        assert deleted is True

        # 11. Verify booking is deleted
        deleted_booking = await booking_repository.get_by_id(created_booking.id)
        assert deleted_booking is None


class TestCrossServiceIntegration(TestDatabaseIntegration):
    """Test integration between multiple services"""

    async def test_user_chat_booking_integration(self, async_session, user_repository, chat_repository, booking_repository, user_service, chat_service):
        """Test integration scenario with user, chat, and booking"""
        # Override repository sessions
        user_repository._session = async_session
        chat_repository._session = async_session
        booking_repository._session = async_session

        # 1. Register Telegram user
        user = await user_service.register_or_update_telegram_user(
            telegram_id=888999000,
            username="integrated_user",
            language_code="en"
        )

        # 2. Start chat session
        chat_session = await chat_service.initialize_or_get_session(
            chat_id=888999,
            user_id=user.id
        )

        # 3. Simulate booking conversation
        await chat_service.add_message_to_history(
            888999,
            "I want to book a room for 2 guests",
            "user"
        )

        # 4. Save booking state in chat
        booking_state = {
            "flow": "booking",
            "step": "payment",
            "booking_data": {
                "check_in": "2024-03-15",
                "check_out": "2024-03-17",
                "guests": 2,
                "rate_type": "standard"
            }
        }
        await chat_service.save_langgraph_state(888999, booking_state)

        # 5. Create actual booking
        booking = Booking(
            user_id=user.id,
            check_in_date=date(2024, 3, 15),
            check_out_date=date(2024, 3, 17),
            num_guests=2,
            rate_type="standard",
            status="pending",
            payment_status="unpaid"
        )
        created_booking = await booking_repository.create(booking)

        # 6. Update chat context with booking ID
        context_update = {
            "booking_id": str(created_booking.id),
            "intent": "booking",
            "status": "booking_created"
        }
        await chat_service.update_conversation_context(888999, context_update)

        # 7. Verify all data is connected
        # Check user
        final_user = await user_service.get_user_by_id(user.id)
        assert final_user.profile.username == "integrated_user"

        # Check chat
        final_chat = await chat_service.get_session_by_chat_id(888999)
        assert final_chat.user_id == user.id
        
        chat_state = await chat_service.get_langgraph_state(888999)
        assert chat_state["booking_data"]["guests"] == 2

        chat_context = await chat_service.get_conversation_history(888999)
        assert chat_context["booking_id"] == str(created_booking.id)

        # Check booking
        final_booking = await booking_repository.get_by_id(created_booking.id)
        assert final_booking.user_id == user.id
        assert final_booking.num_guests == 2

        # 8. Cleanup - end chat and verify relationships
        await chat_service.end_session(888999)
        ended_chat = await chat_service.get_session_by_chat_id(888999)
        assert ended_chat.is_active is False

        # Booking should still exist
        persistent_booking = await booking_repository.get_by_id(created_booking.id)
        assert persistent_booking is not None