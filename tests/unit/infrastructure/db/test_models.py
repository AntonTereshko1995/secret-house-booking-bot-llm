"""Tests for database models"""

import pytest
from uuid import uuid4
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from infrastructure.db.models.base import Base
from infrastructure.db.models.user import UserModel
from infrastructure.db.models.booking import BookingModel
from infrastructure.db.models.chat import ChatSessionModel
from domain.user.entities import User, UserProfile
from domain.booking.entities import Booking
from domain.chat.entities import ChatSession


class TestDatabaseModels:
    """Test database models"""

    @pytest.fixture(scope="function")
    def engine(self):
        """Create in-memory SQLite engine for testing"""
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
        Base.metadata.create_all(engine)
        return engine

    @pytest.fixture
    def session(self, engine):
        """Create database session"""
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()


class TestUserModel(TestDatabaseModels):
    """Test UserModel"""

    def test_create_user_model(self, session):
        """Test creating a user model"""
        user_id = uuid4()
        user = UserModel(
            id=user_id,
            telegram_id=123456789,
            username="testuser",
            language_code="en",
            is_active=True
        )

        session.add(user)
        session.commit()

        # Verify
        retrieved_user = session.query(UserModel).filter_by(id=user_id).first()
        assert retrieved_user is not None
        assert retrieved_user.telegram_id == 123456789
        assert retrieved_user.username == "testuser"
        assert retrieved_user.language_code == "en"
        assert retrieved_user.is_active is True
        assert retrieved_user.created_at is not None
        assert retrieved_user.updated_at is not None

    def test_user_model_defaults(self, session):
        """Test user model default values"""
        user = UserModel(
            telegram_id=123456789,
            username="testuser"
        )

        session.add(user)
        session.commit()

        # Verify defaults
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.id is not None

    def test_user_model_unique_telegram_id(self, session):
        """Test that telegram_id is unique"""
        # Create first user
        user1 = UserModel(
            telegram_id=123456789,
            username="user1"
        )
        session.add(user1)
        session.commit()

        # Try to create second user with same telegram_id
        user2 = UserModel(
            telegram_id=123456789,
            username="user2"
        )
        session.add(user2)

        # Should raise integrity error
        with pytest.raises(Exception):  # SQLite raises IntegrityError
            session.commit()

    def test_user_model_to_domain_entity(self):
        """Test converting user model to domain entity"""
        user_model = UserModel(
            id=uuid4(),
            telegram_id=123456789,
            username="testuser",
            language_code="en",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Convert to domain entity
        domain_user = User(
            id=user_model.id,
            telegram_id=user_model.telegram_id,
            username=user_model.username,
            language_code=user_model.language_code,
            is_active=user_model.is_active,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at
        )

        # Verify mapping
        assert domain_user.id == user_model.id
        assert domain_user.telegram_id == user_model.telegram_id
        assert domain_user.username == user_model.username
        assert domain_user.language_code == user_model.language_code
        assert domain_user.is_active == user_model.is_active

    def test_domain_entity_to_user_model(self):
        """Test converting domain entity to user model"""
        domain_user = User(
            telegram_id=123456789,
            username="testuser",
            language_code="en",
            is_active=True
        )

        # Convert to model
        user_model = UserModel(
            id=domain_user.id,
            telegram_id=domain_user.telegram_id,
            username=domain_user.username,
            language_code=domain_user.language_code,
            is_active=domain_user.is_active,
            created_at=domain_user.created_at,
            updated_at=domain_user.updated_at
        )

        # Verify mapping
        assert user_model.telegram_id == domain_user.telegram_id
        assert user_model.username == domain_user.username
        assert user_model.language_code == domain_user.language_code
        assert user_model.is_active == domain_user.is_active


class TestBookingModel(TestDatabaseModels):
    """Test BookingModel"""

    def test_create_booking_model(self, session):
        """Test creating a booking model"""
        # First create a user
        user_id = uuid4()
        user = UserModel(
            id=user_id,
            telegram_id=123456789,
            username="testuser"
        )
        session.add(user)
        session.commit()

        # Create booking
        booking_id = uuid4()
        booking = BookingModel(
            id=booking_id,
            user_id=user_id,
            check_in_date=date(2024, 1, 15),
            check_out_date=date(2024, 1, 17),
            num_guests=2,
            guest_names="John Doe, Jane Doe",
            contact_phone="+1234567890",
            special_requests="Late checkout",
            status="pending",
            total_amount=Decimal("150.00"),
            rate_type="standard",
            payment_status="unpaid",
            notes="Test booking",
            is_active=True
        )

        session.add(booking)
        session.commit()

        # Verify
        retrieved_booking = session.query(BookingModel).filter_by(id=booking_id).first()
        assert retrieved_booking is not None
        assert retrieved_booking.user_id == user_id
        assert retrieved_booking.check_in_date == date(2024, 1, 15)
        assert retrieved_booking.check_out_date == date(2024, 1, 17)
        assert retrieved_booking.num_guests == 2
        assert retrieved_booking.guest_names == "John Doe, Jane Doe"
        assert retrieved_booking.status == "pending"
        assert retrieved_booking.total_amount == Decimal("150.00")
        assert retrieved_booking.rate_type == "standard"
        assert retrieved_booking.payment_status == "unpaid"

    def test_booking_model_defaults(self, session):
        """Test booking model default values"""
        user_id = uuid4()
        user = UserModel(id=user_id, telegram_id=123456789, username="testuser")
        session.add(user)
        session.commit()

        booking = BookingModel(
            user_id=user_id,
            check_in_date=date(2024, 1, 15),
            check_out_date=date(2024, 1, 17),
            num_guests=2
        )

        session.add(booking)
        session.commit()

        # Verify defaults
        assert booking.status == "pending"
        assert booking.payment_status == "unpaid"
        assert booking.is_active is True
        assert booking.created_at is not None
        assert booking.updated_at is not None

    def test_booking_model_foreign_key_constraint(self, session):
        """Test foreign key constraint for user_id"""
        # Try to create booking with non-existent user_id
        booking = BookingModel(
            user_id=uuid4(),  # Non-existent user
            check_in_date=date(2024, 1, 15),
            check_out_date=date(2024, 1, 17),
            num_guests=2
        )

        session.add(booking)

        # Should raise foreign key constraint error
        with pytest.raises(Exception):
            session.commit()

    def test_booking_model_to_domain_entity(self):
        """Test converting booking model to domain entity"""
        user_id = uuid4()
        booking_model = BookingModel(
            id=uuid4(),
            user_id=user_id,
            check_in_date=date(2024, 1, 15),
            check_out_date=date(2024, 1, 17),
            num_guests=2,
            guest_names="John Doe",
            contact_phone="+1234567890",
            special_requests="Late checkout",
            status="confirmed",
            total_amount=Decimal("200.50"),
            rate_type="premium",
            payment_status="paid",
            notes="VIP guest",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Convert to domain entity
        domain_booking = Booking(
            id=booking_model.id,
            user_id=booking_model.user_id,
            check_in_date=booking_model.check_in_date,
            check_out_date=booking_model.check_out_date,
            num_guests=booking_model.num_guests,
            guest_names=booking_model.guest_names,
            contact_phone=booking_model.contact_phone,
            special_requests=booking_model.special_requests,
            status=booking_model.status,
            total_amount=booking_model.total_amount,
            rate_type=booking_model.rate_type,
            payment_status=booking_model.payment_status,
            notes=booking_model.notes,
            is_active=booking_model.is_active,
            created_at=booking_model.created_at,
            updated_at=booking_model.updated_at
        )

        # Verify mapping
        assert domain_booking.id == booking_model.id
        assert domain_booking.user_id == booking_model.user_id
        assert domain_booking.check_in_date == booking_model.check_in_date
        assert domain_booking.num_guests == booking_model.num_guests
        assert domain_booking.status == booking_model.status
        assert domain_booking.total_amount == booking_model.total_amount


class TestChatSessionModel(TestDatabaseModels):
    """Test ChatSessionModel"""

    def test_create_chat_session_model(self, session):
        """Test creating a chat session model"""
        # Create user first
        user_id = uuid4()
        user = UserModel(id=user_id, telegram_id=123456789, username="testuser")
        session.add(user)
        session.commit()

        # Create chat session
        session_id = uuid4()
        chat_session = ChatSessionModel(
            id=session_id,
            chat_id=123456,
            user_id=user_id,
            session_type="user",
            state_data={"step": 1, "flow": "booking"},
            conversation_context={
                "messages": [{"role": "user", "content": "Hello"}],
                "intent": "booking"
            },
            is_active=True,
            last_activity_at=datetime.utcnow()
        )

        session.add(chat_session)
        session.commit()

        # Verify
        retrieved_session = session.query(ChatSessionModel).filter_by(id=session_id).first()
        assert retrieved_session is not None
        assert retrieved_session.chat_id == 123456
        assert retrieved_session.user_id == user_id
        assert retrieved_session.session_type == "user"
        assert retrieved_session.state_data["step"] == 1
        assert retrieved_session.conversation_context["intent"] == "booking"
        assert retrieved_session.is_active is True

    def test_chat_session_model_defaults(self, session):
        """Test chat session model default values"""
        chat_session = ChatSessionModel(
            chat_id=123456,
            session_type="user"
        )

        session.add(chat_session)
        session.commit()

        # Verify defaults
        assert chat_session.session_type == "user"
        assert chat_session.is_active is True
        assert chat_session.state_data is None or chat_session.state_data == {}
        assert chat_session.created_at is not None
        assert chat_session.updated_at is not None
        assert chat_session.last_activity_at is not None

    def test_chat_session_unique_chat_id(self, session):
        """Test that chat_id is unique"""
        # Create first session
        session1 = ChatSessionModel(
            chat_id=123456,
            session_type="user"
        )
        session.add(session1)
        session.commit()

        # Try to create second session with same chat_id
        session2 = ChatSessionModel(
            chat_id=123456,
            session_type="group"
        )
        session.add(session2)

        # Should raise integrity error
        with pytest.raises(Exception):  # SQLite raises IntegrityError
            session.commit()

    def test_chat_session_jsonb_fields(self, session):
        """Test JSONB fields for state_data and conversation_context"""
        complex_state = {
            "current_step": "payment",
            "booking_data": {
                "check_in": "2024-01-15",
                "check_out": "2024-01-17",
                "guests": 2,
                "options": ["breakfast", "wifi"]
            },
            "user_preferences": {
                "language": "en",
                "notifications": True
            }
        }

        complex_context = {
            "messages": [
                {"role": "user", "content": "I want to book a room", "timestamp": "2024-01-01T10:00:00"},
                {"role": "assistant", "content": "I can help you with that", "timestamp": "2024-01-01T10:00:01"}
            ],
            "metadata": {
                "session_start": "2024-01-01T10:00:00",
                "user_agent": "TelegramBot/1.0"
            },
            "intent": "booking",
            "current_state": "collecting_dates"
        }

        chat_session = ChatSessionModel(
            chat_id=789123,
            session_type="user",
            state_data=complex_state,
            conversation_context=complex_context
        )

        session.add(chat_session)
        session.commit()

        # Retrieve and verify
        retrieved = session.query(ChatSessionModel).filter_by(chat_id=789123).first()
        assert retrieved.state_data["current_step"] == "payment"
        assert retrieved.state_data["booking_data"]["guests"] == 2
        assert "breakfast" in retrieved.state_data["booking_data"]["options"]
        assert len(retrieved.conversation_context["messages"]) == 2
        assert retrieved.conversation_context["intent"] == "booking"

    def test_chat_session_model_to_domain_entity(self):
        """Test converting chat session model to domain entity"""
        session_model = ChatSessionModel(
            id=uuid4(),
            chat_id=123456,
            user_id=uuid4(),
            session_type="user",
            state_data={"step": 1},
            conversation_context={"intent": "faq"},
            is_active=True,
            last_activity_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Convert to domain entity
        domain_session = ChatSession(
            id=session_model.id,
            chat_id=session_model.chat_id,
            user_id=session_model.user_id,
            session_type=session_model.session_type,
            state_data=session_model.state_data,
            conversation_context=session_model.conversation_context,
            is_active=session_model.is_active,
            last_activity_at=session_model.last_activity_at,
            created_at=session_model.created_at,
            updated_at=session_model.updated_at
        )

        # Verify mapping
        assert domain_session.id == session_model.id
        assert domain_session.chat_id == session_model.chat_id
        assert domain_session.user_id == session_model.user_id
        assert domain_session.session_type == session_model.session_type
        assert domain_session.state_data == session_model.state_data
        assert domain_session.conversation_context == session_model.conversation_context
        assert domain_session.is_active == session_model.is_active