"""Tests for Alembic database migrations"""

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from alembic.config import Config
from alembic import command
import tempfile
import os


class TestAlembicMigrations:
    """Test Alembic migration functionality"""

    @pytest.fixture
    async def temp_db_url(self):
        """Create temporary SQLite database for migration testing"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name
        
        db_url = f"sqlite+aiosqlite:///{db_path}"
        yield db_url
        
        # Cleanup
        try:
            os.unlink(db_path)
        except FileNotFoundError:
            pass

    @pytest.fixture
    def alembic_config(self, temp_db_url):
        """Create Alembic configuration for testing"""
        config = Config("alembic.ini")
        config.set_main_option("sqlalchemy.url", temp_db_url.replace("+aiosqlite", ""))
        return config

    async def test_migration_upgrade(self, temp_db_url, alembic_config):
        """Test running migration upgrade"""
        # Run migration
        command.upgrade(alembic_config, "head")
        
        # Verify tables exist
        engine = create_async_engine(temp_db_url)
        async with engine.begin() as conn:
            # Check users table
            result = await conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
            ))
            users_table = result.fetchone()
            assert users_table is not None

            # Check bookings table
            result = await conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='bookings'"
            ))
            bookings_table = result.fetchone()
            assert bookings_table is not None

            # Check chat_sessions table
            result = await conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='chat_sessions'"
            ))
            chat_table = result.fetchone()
            assert chat_table is not None

            # Verify foreign key constraints exist
            result = await conn.execute(text("PRAGMA foreign_key_list(bookings)"))
            fk_constraints = result.fetchall()
            assert len(fk_constraints) > 0  # Should have FK to users table

        await engine.dispose()

    async def test_migration_downgrade(self, temp_db_url, alembic_config):
        """Test running migration downgrade"""
        # First upgrade
        command.upgrade(alembic_config, "head")
        
        # Then downgrade
        command.downgrade(alembic_config, "base")
        
        # Verify tables are removed
        engine = create_async_engine(temp_db_url)
        async with engine.begin() as conn:
            result = await conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('users', 'bookings', 'chat_sessions')"
            ))
            tables = result.fetchall()
            assert len(tables) == 0  # All tables should be dropped

        await engine.dispose()

    async def test_migration_idempotency(self, temp_db_url, alembic_config):
        """Test that running migrations multiple times is safe"""
        # Run migration twice
        command.upgrade(alembic_config, "head")
        command.upgrade(alembic_config, "head")  # Should not fail
        
        # Verify tables still exist and are functional
        engine = create_async_engine(temp_db_url)
        async with engine.begin() as conn:
            # Test inserting data
            await conn.execute(text(
                "INSERT INTO users (id, telegram_id, username, is_active, created_at, updated_at) "
                "VALUES ('550e8400-e29b-41d4-a716-446655440000', 123456789, 'testuser', 1, datetime('now'), datetime('now'))"
            ))
            
            result = await conn.execute(text("SELECT username FROM users WHERE telegram_id = 123456789"))
            user = result.fetchone()
            assert user[0] == "testuser"

        await engine.dispose()

    async def test_migration_indexes(self, temp_db_url, alembic_config):
        """Test that database indexes are created properly"""
        command.upgrade(alembic_config, "head")
        
        engine = create_async_engine(temp_db_url)
        async with engine.begin() as conn:
            # Check if indexes exist (SQLite specific)
            result = await conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'ix_%'"
            ))
            indexes = result.fetchall()
            
            # Should have several indexes
            index_names = [idx[0] for idx in indexes]
            expected_indexes = [
                "ix_users_telegram_id",
                "ix_bookings_user_id", 
                "ix_bookings_check_in_date",
                "ix_bookings_status",
                "ix_chat_sessions_chat_id",
                "ix_chat_sessions_user_id"
            ]
            
            for expected_idx in expected_indexes:
                assert expected_idx in index_names

        await engine.dispose()


class TestDatabaseSeeding:
    """Test database seeding functionality"""

    @pytest.fixture
    async def seeded_engine(self):
        """Create database with test data"""
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        
        # Import and create tables
        from infrastructure.db.models.base import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        yield engine
        await engine.dispose()

    async def test_seed_test_users(self, seeded_engine):
        """Test seeding test users"""
        from infrastructure.db.repositories.user_repository import UserRepositoryImpl
        from domain.user.entities import User, UserProfile
        
        # Create test users
        test_users = [
            User(
                telegram_id=111111111,
                username="testuser1",
                language_code="en"
            ),
            User(
                telegram_id=222222222,
                username="testuser2", 
                language_code="ru"
            )
        ]
        
        # Seed users
        user_repo = UserRepositoryImpl()
        async with seeded_engine.begin() as conn:
            async_session = AsyncSession(conn)
            user_repo._session = async_session
            
            for user in test_users:
                await user_repo.create(user)
            
            # Verify seeding
            all_users = await user_repo.get_all()
            assert len(all_users) == 2
            assert all_users[0].profile.username in ["testuser1", "testuser2"]

    async def test_seed_test_bookings(self, seeded_engine):
        """Test seeding test bookings"""
        from infrastructure.db.repositories.user_repository import UserRepositoryImpl
        from infrastructure.db.repositories.booking_repository import BookingRepositoryImpl
        from domain.user.entities import User, UserProfile
        from domain.booking.entities import Booking
        from datetime import date
        from decimal import Decimal
        
        # First create a user
        user_repo = UserRepositoryImpl()
        booking_repo = BookingRepositoryImpl()
        
        async with seeded_engine.begin() as conn:
            async_session = AsyncSession(conn)
            user_repo._session = async_session
            booking_repo._session = async_session
            
            user = User(
                telegram_id=333333333,
                profile=UserProfile(username="bookinguser")
            )
            created_user = await user_repo.create(user)
            
            # Create test bookings
            test_bookings = [
                Booking(
                    user_id=created_user.id,
                    check_in_date=date(2024, 3, 15),
                    check_out_date=date(2024, 3, 17),
                    num_guests=2,
                    guest_names="John Doe, Jane Doe",
                    contact_phone="+1234567890",
                    status="confirmed",
                    total_amount=Decimal("200.00"),
                    rate_type="standard",
                    payment_status="paid"
                ),
                Booking(
                    user_id=created_user.id,
                    check_in_date=date(2024, 4, 10),
                    check_out_date=date(2024, 4, 12),
                    num_guests=1,
                    guest_names="Solo Traveler",
                    contact_phone="+0987654321", 
                    status="pending",
                    total_amount=Decimal("120.00"),
                    rate_type="economy",
                    payment_status="unpaid"
                )
            ]
            
            # Seed bookings
            for booking in test_bookings:
                await booking_repo.create(booking)
            
            # Verify seeding
            user_bookings = await booking_repo.get_by_user_id(created_user.id)
            assert len(user_bookings) == 2
            
            confirmed_bookings = await booking_repo.find_by_status("confirmed")
            assert len(confirmed_bookings) == 1
            assert confirmed_bookings[0].total_amount == Decimal("200.00")

    async def test_seed_chat_sessions(self, seeded_engine):
        """Test seeding chat sessions"""
        from infrastructure.db.repositories.user_repository import UserRepositoryImpl
        from infrastructure.db.repositories.chat_repository import ChatRepositoryImpl
        from domain.user.entities import User, UserProfile
        from domain.chat.entities import ChatSession
        
        user_repo = UserRepositoryImpl()
        chat_repo = ChatRepositoryImpl()
        
        async with seeded_engine.begin() as conn:
            async_session = AsyncSession(conn)
            user_repo._session = async_session
            chat_repo._session = async_session
            
            # Create user
            user = User(
                telegram_id=444444444,
                profile=UserProfile(username="chatuser")
            )
            created_user = await user_repo.create(user)
            
            # Create test chat sessions
            test_sessions = [
                ChatSession(
                    chat_id=111222,
                    user_id=created_user.id,
                    session_type="user",
                    state_data={"flow": "booking", "step": "completed"},
                    conversation_context={
                        "messages": [
                            {"role": "user", "content": "I want to book a room"},
                            {"role": "assistant", "content": "Sure, I can help with that"}
                        ],
                        "intent": "booking"
                    }
                ),
                ChatSession(
                    chat_id=333444,
                    user_id=created_user.id,
                    session_type="user",
                    state_data={"flow": "faq", "step": "answered"},
                    conversation_context={
                        "messages": [
                            {"role": "user", "content": "What are your rates?"},
                            {"role": "assistant", "content": "Our rates start from $100 per night"}
                        ],
                        "intent": "faq"
                    },
                    is_active=False
                )
            ]
            
            # Seed chat sessions
            for session in test_sessions:
                await chat_repo.create(session)
            
            # Verify seeding
            active_sessions = await chat_repo.get_active_sessions_by_user(created_user.id)
            assert len(active_sessions) == 1
            assert active_sessions[0].state_data["flow"] == "booking"
            
            booking_session = await chat_repo.get_by_chat_id(111222)
            assert booking_session is not None
            assert len(booking_session.conversation_context["messages"]) == 2