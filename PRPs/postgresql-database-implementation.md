name: "PostgreSQL Database Implementation - Complete Data Persistence Layer"
description: |

## Purpose

Implement a complete PostgreSQL database layer for The Secret House booking bot to store and manage bookings, users, and chat conversation data. This includes creating SQLAlchemy models, repositories, migrations, and services to persist all booking information, handle user management, and maintain chat conversation history for LangGraph state persistence.

## Core Principles

1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Be sure to follow all rules in CLAUDE.md

---

## Goal

Build a complete PostgreSQL database layer that persists all critical application data including bookings, users, and chat conversations. The system will handle booking creation and modification workflows for users without prepayment, support booking level changes, and maintain conversation state for LangGraph continuity. All data operations will follow Clean Architecture principles with proper repository patterns and database transactions.

## Why

- **Business value**: Ensures data persistence and reliability for all booking operations
- **User experience**: Enables booking modifications, history tracking, and conversation continuity
- **Integration**: Seamlessly integrates with existing LangGraph state management and booking flows
- **Scalability**: Foundation for advanced features like analytics, reporting, and multi-tenant support
- **Data integrity**: Ensures consistent state management and prevents data loss
- **Compliance**: Provides audit trail and data backup capabilities for business operations

## What

Implement a complete database persistence layer that:

- Creates PostgreSQL database models for Bookings, Users, and Chat conversations
- Implements SQLAlchemy 2.x repository pattern with Clean Architecture boundaries
- Provides database migrations using Alembic for schema management
- Handles booking creation and modification workflows for users without prepayment
- Supports booking level changes with proper state transitions
- Maintains chat conversation history for LangGraph state persistence
- Integrates with existing domain entities and application services
- Includes comprehensive error handling and transaction management
- Supports database seeding and development data setup

### Success Criteria

- [ ] PostgreSQL database properly configured with SQLAlchemy 2.x async support
- [ ] All domain entities (Booking, User, Chat) have corresponding database models
- [ ] Repository pattern implemented following Clean Architecture principles
- [ ] Alembic migrations created and tested for all schema changes
- [ ] Booking creation workflow saves to database without prepayment requirement
- [ ] Booking modification workflow handles level changes with proper state management
- [ ] Chat conversation state persisted for LangGraph continuity
- [ ] All database operations are transactional and error-safe
- [ ] Comprehensive test coverage including repository and integration tests
- [ ] Database connection pooling and performance optimization configured

## All Needed Context

### Documentation & References (list all context needed to implement the feature)

```yaml
# MUST READ - Include these in your context window
- url: https://docs.sqlalchemy.org/en/20/
  why: SQLAlchemy 2.x ORM patterns, async support, and best practices
  section: Async ORM, declarative mapping, repository patterns
  critical: AsyncSession usage, proper async patterns, modern SQLAlchemy syntax

- url: https://alembic.sqlalchemy.org/en/latest/
  why: Database migrations and schema management
  critical: Migration generation, environment configuration, revision management

- url: https://docs.python.org/3/library/asyncio.html
  why: Async programming patterns for database operations
  critical: async/await patterns, connection management, transaction handling

- file: domain/booking/entities.py
  why: Existing domain models that need database mapping
  critical: Booking, BookingRequest models with UUID, payment status, dates

- file: domain/booking/payment.py
  why: Payment status and proof models for database representation
  pattern: PaymentStatus enum, PaymentProof with file metadata

- file: core/config.py
  why: Database configuration patterns and environment setup
  critical: database_url setting, existing configuration patterns

- file: infrastructure/llm/graphs/common/graph_state.py
  why: LangGraph state structure that needs persistence
  pattern: AppState with conversation context, user_id tracking

- file: apps/telegram_bot/handlers/payments.py
  why: Current booking creation patterns and user_id usage
  pattern: _create_booking_from_context function, payment proof handling

- file: infrastructure/llm/graphs/booking/booking_graph.py
  why: Booking workflow and state management patterns
  critical: Booking field enums, tariff handling, validation logic

- docfile: PRPs/CLAUDE.md
  why: Code style, UV usage, Clean Architecture patterns, testing standards
  critical: UV commands, async patterns, repository pattern guidelines
```

### Current Codebase tree (run `tree` in the root of the project) to get an overview of the codebase

```bash
/Users/a/secret-house-booking-bot-llm/
├── apps/
│   └── telegram_bot/
│       ├── main.py                     # Bot entry point with Redis storage
│       ├── handlers/
│       │   ├── messages.py             # Message handling with user_id usage
│       │   ├── payments.py             # Payment proof handling and booking creation
│       │   └── callbacks.py            # Admin callbacks with user tracking
│       └── middlewares/
│           └── rate_limit.py           # Rate limiting with user_id
├── core/
│   ├── config.py                       # Database URL configuration ready
│   ├── logging.py                      # Structured logging
│   └── utils/
├── domain/
│   └── booking/
│       ├── entities.py                 # Booking domain model ready for DB mapping
│       ├── payment.py                  # Payment status and proof models
│       ├── ports.py                    # Domain interfaces
│       └── availability.py            # Availability domain logic
├── application/
│   ├── services/
│   │   ├── booking_service.py          # Service layer needing repository integration
│   │   ├── faq_service.py              # FAQ service with conversation context
│   │   ├── pricing_service.py          # Pricing calculations
│   │   └── availability_service.py     # Availability checking
│   └── workflows/
├── infrastructure/
│   ├── llm/                           # LangGraph implementation with state management
│   ├── kv/                            # Redis for FSM (exists)
│   ├── vector/                        # ChromaDB (exists)
│   ├── db/                            # EMPTY - Database layer to be created
│   ├── notifications/                 # Admin notifications
│   └── telemetry/
└── tests/
    ├── unit/                          # Unit test patterns to follow
    ├── integration/                   # Integration test patterns
    └── e2e/                          # End-to-end tests
```

### Desired Codebase tree with files to be added and responsibility of file

```bash
# NEW FILES TO CREATE:
infrastructure/db/
├── __init__.py                        # Database module init
├── connection.py                      # Database connection and session management
├── models/
│   ├── __init__.py                   # Models module init
│   ├── base.py                       # Base model class with common fields
│   ├── booking.py                    # Booking SQLAlchemy model
│   ├── user.py                       # User SQLAlchemy model
│   └── chat.py                       # Chat conversation SQLAlchemy model
├── repositories/
│   ├── __init__.py                   # Repositories module init
│   ├── base.py                       # Base repository with common CRUD operations
│   ├── booking_repository.py         # Booking-specific repository operations
│   ├── user_repository.py            # User-specific repository operations
│   └── chat_repository.py            # Chat conversation repository operations
└── migrations/
    └── env.py                        # Alembic environment configuration

alembic/
├── env.py                            # Alembic migration environment
├── script.py.mako                    # Migration template
└── versions/                         # Generated migration files

# NEW DOMAIN FILES:
domain/user/
├── __init__.py                       # User domain module
└── entities.py                       # User domain entities

domain/chat/
├── __init__.py                       # Chat domain module  
└── entities.py                       # Chat conversation domain entities

# FILES TO MODIFY:
core/config.py                        # Add database pool and connection settings
application/services/booking_service.py  # Integrate with booking repository
domain/booking/ports.py                # Add repository interfaces
infrastructure/llm/graphs/common/graph_state.py  # Add database persistence hooks

# NEW TEST FILES:
tests/unit/infrastructure/db/
├── test_connection.py                # Database connection tests
├── test_models.py                    # Model validation tests
└── repositories/
    ├── test_booking_repository.py    # Booking repository unit tests
    ├── test_user_repository.py       # User repository unit tests
    └── test_chat_repository.py       # Chat repository unit tests

tests/integration/db/
├── test_database_integration.py      # Full database workflow tests
├── test_booking_persistence.py       # Booking CRUD integration tests
└── test_migration_tests.py           # Migration testing
```

### Known Gotchas of our codebase & Library Quirks

```python
# CRITICAL: SQLAlchemy 2.x Async Patterns
# Use AsyncSession and async/await throughout
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# CRITICAL: Proper async session management
async with session() as db_session:
    async with db_session.begin():
        # Transaction automatically commits or rolls back

# CRITICAL: UUID Primary Keys
# Follow existing domain pattern with UUID primary keys for bookings
import uuid
from sqlalchemy.dialects.postgresql import UUID

# CRITICAL: Clean Architecture Repository Pattern
# Repositories belong in infrastructure layer, interfaces in domain/ports
# Domain services inject repository interfaces via dependency injection

# CRITICAL: Existing Booking Domain Model
# Map exactly to existing domain/booking/entities.py Booking class
# Preserve all field names, types, and validation rules

# CRITICAL: User ID Tracking Pattern
# Throughout codebase, user_id is int (Telegram user ID)
# Chat conversations use thread_id = f"{chat_id}:{user_id}" pattern

# CRITICAL: Payment Status Integration
# Existing PaymentStatus enum and PaymentProof model must be preserved
# Database model should match domain model exactly

# CRITICAL: LangGraph State Persistence
# Chat table should store conversation context for LangGraph continuity
# JSON column for storing complex state objects

# CRITICAL: Database Connection Configuration
# Database URL from environment: DATABASE_URL = "postgresql+asyncpg://..."
# Use asyncpg driver for PostgreSQL with SQLAlchemy async

# CRITICAL: Alembic Integration
# Migration environment must work with async engine
# Use UV for running migrations: `uv run alembic upgrade head`

# CRITICAL: Existing Booking Creation Pattern
# Follow pattern from apps/telegram_bot/handlers/payments.py
# _create_booking_from_context creates Booking from conversation context

# CRITICAL: Async Service Integration  
# All application services are async, repository operations must be async
async def create_booking(self, booking_request: BookingRequest) -> Booking:
    # Implementation

# CRITICAL: Error Handling Patterns
# Follow existing error handling with structured logging
# Use proper database transaction rollback on errors

# CRITICAL: Testing with UV
# Always use uv run pytest for testing
# Database tests need test database and proper teardown

# CRITICAL: Booking Modification Workflow
# Support changing booking levels (tariff, dates, options)
# Maintain audit trail of changes for business tracking
```

## Implementation Blueprint

### Data models and structure

Create comprehensive database models that map domain entities to PostgreSQL tables with proper relationships and constraints.

```python
# Database models with SQLAlchemy 2.x async patterns
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

class BaseModel(Base):
    """Base model with common audit fields"""
    __abstract__ = True
  
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class User(BaseModel):
    """User model for Telegram bot users"""
    __tablename__ = "users"
  
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)  # Telegram user ID
    contact = Column(String(255), nullable=True)  # @contact
    language_code = Column(String(10), default="ru")
    is_active = Column(Boolean, default=True)
  
    # Relationships
    bookings = relationship("Booking", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")

class Booking(BaseModel):
    """Booking model mapping to domain entity"""
    __tablename__ = "bookings"
  
    # User relationship
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    telegram_user_id = Column(Integer, nullable=False, index=True)  # Direct Telegram ID
  
    # Booking details (exact mapping to domain entity)
    tariff = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    start_time = Column(String(10), nullable=False)  # HH:MM format
    finish_date = Column(DateTime, nullable=False)  
    finish_time = Column(String(10), nullable=False)
    price = Column(int, nullable=0)
    is_rescedule = Column(Boolean, default=False)
  
    # Room and service selections
    white_bedroom = Column(Boolean, default=False)
    green_bedroom = Column(Boolean, default=False)
    sauna = Column(Boolean, default=False)
    photoshoot = Column(Boolean, default=False)
    secret_room = Column(Boolean, default=False)
  
    # Guest and contact info
    number_guests = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
  
    # Status management
    status = Column(String(50), default="pending")  # waiting_payment, waiting_approved, confirmed, cancelled, finished (use enum)
  
    # Audit and modification tracking
    modification_count = Column(Integer, default=0)
    last_modified_by = Column(Integer, nullable=True)  # Admin user who modified
  
    # Relationships
    user = relationship("User", back_populates="bookings")

class ChatSession(BaseModel):
    """Chat conversation session for LangGraph state persistence"""
    __tablename__ = "chat_sessions"
  
    # Session identification
    thread_id = Column(String(255), unique=True, nullable=False, index=True)  # "{chat_id}:{user_id}"
    chat_id = Column(Integer, nullable=False)  # Telegram chat ID
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    telegram_user_id = Column(Integer, nullable=False, index=True)  # Direct Telegram ID
  
    # LangGraph state management
    current_intent = Column(String(50), nullable=True)  # booking, faq, pricing, etc.
    state_data = Column(JSON, nullable=True)  # Complete LangGraph state
    conversation_context = Column(JSON, nullable=True)  # Conversation history for LLM
  
    # Session metadata  
    last_message_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=True)
    session_end_reason = Column(String(100), nullable=True)  # completed, timeout, cancelled
  
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
```

### list of tasks to be completed to fullfill the PRP in the order they should be completed

```yaml
Task 1: Create Database Infrastructure Foundation
CREATE infrastructure/db/__init__.py:
  - IMPLEMENT database module initialization
  - EXPORT key database components and utilities

CREATE infrastructure/db/connection.py:
  - IMPLEMENT async database engine and session management
  - USE asyncpg driver for PostgreSQL with SQLAlchemy 2.x
  - CONFIGURE connection pooling and async session factory
  - FOLLOW patterns from core/config.py for database_url

Task 2: Create Domain Entities for User and Chat
CREATE domain/user/entities.py:
  - IMPLEMENT User domain entity with Telegram user data
  - USE Pydantic v2 with proper validation and serialization
  - INCLUDE telegram_id, username, profile information
  - FOLLOW patterns from: domain/booking/entities.py

CREATE domain/chat/entities.py:
  - IMPLEMENT ChatSession domain entity for conversation state
  - INCLUDE thread_id, state_data, conversation context
  - SUPPORT LangGraph state persistence requirements
  - USE JSON serialization for complex state objects

Task 3: Implement SQLAlchemy Database Models
CREATE infrastructure/db/models/base.py:
  - IMPLEMENT BaseModel with common audit fields (id, created_at, updated_at)
  - USE UUID primary keys following existing booking pattern
  - CONFIGURE SQLAlchemy 2.x declarative_base and common patterns

CREATE infrastructure/db/models/user.py:
  - IMPLEMENT User SQLAlchemy model mapping to domain entity
  - CONFIGURE relationships with bookings and chat sessions
  - USE proper indexes for telegram_id lookups
  - INCLUDE user metadata and preferences

CREATE infrastructure/db/models/booking.py:
  - IMPLEMENT Booking SQLAlchemy model mapping to existing domain entity
  - PRESERVE all existing fields from domain/booking/entities.py
  - CONFIGURE foreign key relationships and indexes
  - USE JSON column for payment_proof storage

CREATE infrastructure/db/models/chat.py:
  - IMPLEMENT ChatSession SQLAlchemy model for LangGraph state
  - USE JSON columns for state_data and conversation_context
  - CONFIGURE thread_id unique constraints and indexes
  - INCLUDE session lifecycle management fields

Task 4: Create Repository Pattern Implementation
CREATE infrastructure/db/repositories/base.py:
  - IMPLEMENT BaseRepository with common CRUD operations
  - USE AsyncSession for all database operations
  - INCLUDE generic type support for model classes
  - IMPLEMENT transaction management and error handling

CREATE infrastructure/db/repositories/user_repository.py:
  - IMPLEMENT UserRepository extending BaseRepository
  - ADD find_by_telegram_id method for user lookup
  - INCLUDE user creation and profile update operations
  - FOLLOW async patterns and proper error handling

CREATE infrastructure/db/repositories/booking_repository.py:
  - IMPLEMENT BookingRepository extending BaseRepository
  - ADD booking creation, modification, and query operations
  - INCLUDE find_by_user_id and status filtering methods
  - SUPPORT booking level changes with audit tracking

CREATE infrastructure/db/repositories/chat_repository.py:
  - IMPLEMENT ChatRepository extending BaseRepository
  - ADD state persistence and retrieval for LangGraph
  - INCLUDE find_by_thread_id and active session management
  - SUPPORT conversation context storage and cleanup

Task 5: Setup Alembic Database Migrations
SETUP alembic configuration:
  - INITIALIZE Alembic in project root
  - CONFIGURE async engine support in alembic/env.py
  - SETUP migration environment with proper imports
  - USE UV commands for migration management

CREATE initial migration:
  - GENERATE migration for all database models
  - INCLUDE proper indexes and constraints
  - VALIDATE migration rollback capabilities
  - TEST migration execution with test database

Task 6: Update Domain Ports and Repository Interfaces
MODIFY domain/booking/ports.py:
  - ADD BookingRepository interface for dependency injection
  - DEFINE async method signatures for booking operations
  - INCLUDE modification and query operation interfaces
  - FOLLOW Clean Architecture repository patterns

CREATE domain/user/ports.py:
  - ADD UserRepository interface for user operations
  - DEFINE async method signatures for user management
  - INCLUDE Telegram user lookup and profile management
  - SUPPORT user creation and authentication workflows

CREATE domain/chat/ports.py:
  - ADD ChatRepository interface for conversation state
  - DEFINE async method signatures for state persistence
  - INCLUDE LangGraph state management operations
  - SUPPORT session lifecycle and cleanup operations

Task 7: Integrate Repositories with Application Services
MODIFY application/services/booking_service.py:
  - INJECT BookingRepository via dependency injection
  - REPLACE in-memory booking creation with database persistence
  - IMPLEMENT booking modification workflow with level changes
  - MAINTAIN existing service interface and error handling

CREATE application/services/user_service.py:
  - IMPLEMENT UserService with UserRepository integration
  - ADD user creation and profile management operations
  - INCLUDE Telegram user authentication and lookup
  - SUPPORT user preference and settings management

CREATE application/services/chat_service.py:
  - IMPLEMENT ChatService with ChatRepository integration
  - ADD LangGraph state persistence and retrieval
  - INCLUDE conversation context management
  - SUPPORT session cleanup and archival operations

Task 8: Update Core Configuration
MODIFY core/config.py:
  - ADD database connection pool settings
  - INCLUDE migration and development database configuration
  - ADD database performance and timeout settings
  - CONFIGURE async connection parameters

Task 9: Update Payment Handlers for Database Integration
MODIFY apps/telegram_bot/handlers/payments.py:
  - INTEGRATE with UserService and BookingService repositories
  - REPLACE _create_booking_from_context with database persistence
  - MAINTAIN existing payment proof handling workflow
  - ENSURE proper user creation and lookup

Task 10: Implement Comprehensive Unit Tests
CREATE tests/unit/infrastructure/db/test_connection.py:
  - TEST database connection and session management
  - TEST async session lifecycle and transaction handling
  - INCLUDE connection pool testing and error scenarios
  - FOLLOW pytest async patterns from existing tests

CREATE tests/unit/infrastructure/db/repositories/test_booking_repository.py:
  - TEST booking CRUD operations and query methods
  - TEST booking modification workflow and level changes
  - INCLUDE booking status transitions and audit tracking
  - MOCK database session and test business logic

CREATE tests/unit/infrastructure/db/repositories/test_user_repository.py:
  - TEST user creation, lookup, and profile management
  - TEST Telegram user ID mapping and authentication
  - INCLUDE user state management and preferences
  - VALIDATE async patterns and error handling

CREATE tests/unit/infrastructure/db/repositories/test_chat_repository.py:
  - TEST LangGraph state persistence and retrieval
  - TEST conversation context storage and management
  - INCLUDE session lifecycle and cleanup operations
  - VALIDATE JSON serialization and deserialization

Task 11: Integration Testing
CREATE tests/integration/db/test_database_integration.py:
  - TEST complete booking creation and modification workflow
  - TEST user registration and authentication with real database
  - INCLUDE LangGraph state persistence across conversation turns
  - USE test database with proper setup and teardown

CREATE tests/integration/db/test_booking_persistence.py:
  - TEST end-to-end booking workflow from conversation to database
  - TEST booking modification with level changes and audit trail
  - INCLUDE payment proof storage and retrieval
  - VALIDATE data consistency and transaction integrity

Task 12: Migration Testing and Database Seeding
CREATE tests/integration/db/test_migration_tests.py:
  - TEST Alembic migration execution and rollback
  - VALIDATE schema changes and data preservation
  - INCLUDE migration performance and consistency testing
  - TEST migration scripts with sample data

CREATE infrastructure/db/seeds.py:
  - IMPLEMENT development data seeding for testing
  - CREATE sample users, bookings, and chat sessions
  - INCLUDE realistic test scenarios and edge cases
  - SUPPORT test database initialization for development
```

### Per task pseudocode as needed added to each task

```python
# Task 1: Database Infrastructure Foundation
class DatabaseConnection:
    """Async database connection management"""
    def __init__(self, database_url: str):
        self.engine = create_async_engine(
            database_url,
            echo=settings.log_level == "DEBUG",
            pool_size=20,
            max_overflow=30,
            pool_timeout=30,
            pool_recycle=3600
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
  
    async def get_session(self) -> AsyncSession:
        """Get async database session"""
        async with self.session_factory() as session:
            yield session
  
    async def close(self):
        """Close database connections"""
        await self.engine.dispose()

# Task 4: Repository Pattern Implementation
class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations"""
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model
  
    async def create(self, entity: T) -> T:
        """Create new entity in database"""
        db_entity = self.model(**entity.dict())
        self.session.add(db_entity)
        await self.session.flush()
        await self.session.refresh(db_entity)
        return self._to_domain_entity(db_entity)
  
    async def find_by_id(self, entity_id: UUID) -> Optional[T]:
        """Find entity by ID"""
        result = await self.session.get(self.model, entity_id)
        return self._to_domain_entity(result) if result else None
  
    async def update(self, entity_id: UUID, updates: Dict[str, Any]) -> T:
        """Update entity with partial data"""
        stmt = update(self.model).where(self.model.id == entity_id).values(**updates)
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.find_by_id(entity_id)
  
    async def delete(self, entity_id: UUID) -> bool:
        """Delete entity by ID"""
        stmt = delete(self.model).where(self.model.id == entity_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

class BookingRepository(BaseRepository[Booking]):
    """Booking-specific repository operations"""
  
    async def find_by_user_telegram_id(self, telegram_user_id: int) -> List[Booking]:
        """Find all bookings for a Telegram user"""
        stmt = select(BookingModel).where(BookingModel.telegram_user_id == telegram_user_id)
        result = await self.session.execute(stmt)
        return [self._to_domain_entity(booking) for booking in result.scalars()]
  
    async def create_booking(self, booking_request: BookingRequest, telegram_user_id: int) -> Booking:
        """Create booking from domain request"""
        # Convert domain request to database model
        booking_data = {
            **booking_request.dict(),
            "telegram_user_id": telegram_user_id,
            "status": "pending",
            "payment_status": PaymentStatus.PENDING.value
        }
      
        db_booking = BookingModel(**booking_data)
        self.session.add(db_booking)
        await self.session.flush()
        await self.session.refresh(db_booking)
      
        return self._to_domain_entity(db_booking)
  
    async def modify_booking_level(
        self, 
        booking_id: UUID, 
        new_tariff: str,
        modified_by: int
    ) -> Booking:
        """Modify booking tariff level with audit tracking"""
        async with self.session.begin():
            # Get current booking
            booking = await self.session.get(BookingModel, booking_id)
            if not booking:
                raise ValueError(f"Booking {booking_id} not found")
          
            # Update booking with new level
            booking.tariff = new_tariff
            booking.modification_count += 1
            booking.last_modified_by = modified_by
            booking.updated_at = datetime.now()
          
            await self.session.flush()
            await self.session.refresh(booking)
          
            return self._to_domain_entity(booking)

# Task 7: Application Service Integration
class BookingService:
    """Enhanced booking service with database persistence"""
  
    def __init__(
        self, 
        booking_repo: BookingRepository,
        user_repo: UserRepository,
        chat_repo: ChatRepository
    ):
        self.booking_repo = booking_repo
        self.user_repo = user_repo
        self.chat_repo = chat_repo
  
    async def create_booking_without_prepayment(
        self,
        booking_request: BookingRequest,
        telegram_user_id: int
    ) -> Booking:
        """Create booking without prepayment requirement"""
        async with self.booking_repo.session.begin():
            # Ensure user exists
            user = await self.user_repo.find_by_telegram_id(telegram_user_id)
            if not user:
                user = await self.user_repo.create_from_telegram_id(telegram_user_id)
          
            # Create booking in pending state
            booking = await self.booking_repo.create_booking(booking_request, telegram_user_id)
          
            # Log creation for audit
            logger.info(
                "Booking created without prepayment",
                extra={
                    "booking_id": str(booking.id),
                    "user_id": telegram_user_id,
                    "tariff": booking.tariff
                }
            )
          
            return booking
  
    async def modify_booking_level(
        self,
        booking_id: UUID,
        new_tariff: str,
        telegram_user_id: int
    ) -> Booking:
        """Modify booking level with proper authorization"""
        # Verify user owns booking or is admin
        booking = await self.booking_repo.find_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found")
      
        if booking.telegram_user_id != telegram_user_id:
            raise PermissionError("User not authorized to modify this booking")
      
        # Apply level change
        modified_booking = await self.booking_repo.modify_booking_level(
            booking_id, 
            new_tariff, 
            telegram_user_id
        )
      
        logger.info(
            "Booking level modified",
            extra={
                "booking_id": str(booking_id),
                "old_tariff": booking.tariff,
                "new_tariff": new_tariff,
                "user_id": telegram_user_id
            }
        )
      
        return modified_booking

# Task 5: Alembic Migration Setup
# alembic/env.py configuration for async support
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

async def run_migrations_online():
    """Run migrations in 'online' mode with async engine"""
    configuration = config.get_section(config.config_ini_section)
  
    # Use async engine for migrations
    engine = create_async_engine(
        configuration["sqlalchemy.url"],
        echo=True,
    )
  
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
  
    await engine.dispose()

def do_run_migrations(connection):
    """Execute migrations with sync connection"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
  
    with context.begin_transaction():
        context.run_migrations()

# Migration command usage with UV
# uv run alembic revision --autogenerate -m "Create initial tables"
# uv run alembic upgrade head
# uv run alembic downgrade -1
```

### Integration Points

```yaml
DATABASE_CONNECTION:
  - modify: core/config.py
  - pattern: "DATABASE_URL = postgresql+asyncpg://user:pass@host:port/dbname"
  - add: "DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '20'))"
  - add: "DB_POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', '30'))"

SERVICE_INJECTION:
  - modify: apps/telegram_bot/main.py
  - pattern: "Initialize repository instances and inject into services"
  - integration: "Setup database session dependency injection"

LANGGRAPH_STATE:
  - modify: infrastructure/llm/graphs/common/graph_state.py
  - pattern: "Add database persistence hooks for conversation state"
  - integration: "ChatRepository for state persistence and retrieval"

PAYMENT_WORKFLOW:
  - modify: apps/telegram_bot/handlers/payments.py
  - pattern: "Replace in-memory booking creation with database persistence"
  - integration: "BookingService and UserService with repository injection"

MIGRATION_COMMANDS:
  - add: "Makefile targets for database operations"
  - pattern: "make migrate, make migrate-create, make db-reset"
  - tools: "UV integration for Alembic commands"
```

## Validation Loop

### Level 1: Syntax & Style

```bash
# Run these FIRST - fix any errors before proceeding
uv run ruff check . --fix              # Auto-fix what's possible
uv run ruff format .                   # Format code
uv run mypy .                          # Type checking

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests each new feature/file/function use existing test patterns

```python
# CREATE test_booking_repository.py with these test cases:
@pytest.mark.asyncio
async def test_create_booking_success():
    """Test booking creation with valid data"""
    # Setup
    mock_session = AsyncMock()
    booking_repo = BookingRepository(mock_session, BookingModel)
  
    booking_request = BookingRequest(
        user_id=123456789,
        tariff="DAY",
        start_date=datetime(2024, 6, 1),
        start_time="14:00",
        finish_date=datetime(2024, 6, 2),
        finish_time="12:00",
        first_bedroom=True,
        second_bedroom=False,
        sauna=True,
        photoshoot=False,
        secret_room=False,
        number_guests=2,
        contact="+375291234567",
        comment="Test booking"
    )
  
    # Execute
    booking = await booking_repo.create_booking(booking_request, 123456789)
  
    # Verify
    assert booking.telegram_user_id == 123456789
    assert booking.tariff == "DAY"
    assert booking.status == "pending"
    assert booking.payment_status == "PENDING"
    mock_session.add.assert_called_once()
    mock_session.flush.assert_called_once()

@pytest.mark.asyncio
async def test_modify_booking_level_success():
    """Test booking level modification with audit tracking"""
    # Setup
    mock_session = AsyncMock()
    booking_repo = BookingRepository(mock_session, BookingModel)
  
    booking_id = uuid.uuid4()
    existing_booking = BookingModel(
        id=booking_id,
        telegram_user_id=123456789,
        tariff="DAY",
        modification_count=0
    )
    mock_session.get.return_value = existing_booking
  
    # Execute
    modified_booking = await booking_repo.modify_booking_level(
        booking_id, 
        "HOURS_12", 
        123456789
    )
  
    # Verify
    assert modified_booking.tariff == "HOURS_12"
    assert modified_booking.modification_count == 1
    assert modified_booking.last_modified_by == 123456789
    mock_session.flush.assert_called_once()

@pytest.mark.asyncio
async def test_find_by_user_telegram_id():
    """Test finding bookings by Telegram user ID"""
    # Setup
    mock_session = AsyncMock()
    booking_repo = BookingRepository(mock_session, BookingModel)
  
    mock_bookings = [
        BookingModel(id=uuid.uuid4(), telegram_user_id=123456789, tariff="DAY"),
        BookingModel(id=uuid.uuid4(), telegram_user_id=123456789, tariff="HOURS_12")
    ]
    mock_session.execute.return_value.scalars.return_value = mock_bookings
  
    # Execute
    bookings = await booking_repo.find_by_user_telegram_id(123456789)
  
    # Verify
    assert len(bookings) == 2
    assert all(booking.telegram_user_id == 123456789 for booking in bookings)

@pytest.mark.asyncio  
async def test_chat_repository_state_persistence():
    """Test LangGraph state persistence and retrieval"""
    # Setup
    mock_session = AsyncMock()
    chat_repo = ChatRepository(mock_session, ChatSessionModel)
  
    state_data = {
        "intent": "booking",
        "booking_context": {"tariff": "DAY", "guests": 2},
        "conversation_step": "collecting_dates"
    }
  
    thread_id = "chat123:user456"
  
    # Execute - Save state
    await chat_repo.save_state(thread_id, state_data)
  
    # Setup retrieval mock
    mock_session.execute.return_value.scalar_one_or_none.return_value = ChatSessionModel(
        thread_id=thread_id,
        state_data=state_data,
        is_active=True
    )
  
    # Execute - Retrieve state
    retrieved_state = await chat_repo.get_state(thread_id)
  
    # Verify
    assert retrieved_state["intent"] == "booking"
    assert retrieved_state["booking_context"]["tariff"] == "DAY"
    assert retrieved_state["conversation_step"] == "collecting_dates"

def test_user_repository_telegram_lookup():
    """Test user lookup by Telegram ID"""
    # Setup
    mock_session = AsyncMock()
    user_repo = UserRepository(mock_session, UserModel)
  
    telegram_user_id = 123456789
    mock_user = UserModel(
        telegram_id=telegram_user_id,
        username="testuser",
        first_name="Test",
        is_active=True
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = mock_user
  
    # Execute
    user = await user_repo.find_by_telegram_id(telegram_user_id)
  
    # Verify
    assert user.telegram_id == telegram_user_id
    assert user.username == "testuser"
    assert user.is_active is True

def test_database_connection_session_management():
    """Test async session lifecycle"""
    # Setup
    database_url = "postgresql+asyncpg://test:test@localhost:5432/testdb"
    db_connection = DatabaseConnection(database_url)
  
    # Test session creation
    async with db_connection.get_session() as session:
        assert isinstance(session, AsyncSession)
        assert session.is_active
  
    # Test connection cleanup
    await db_connection.close()
```

```bash
# Run and iterate until passing:
uv run pytest tests/unit/infrastructure/db/ -v
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3: Integration Test

```bash
# Setup test database
export TEST_DATABASE_URL="postgresql+asyncpg://test:test@localhost:5432/secret_house_test"

# Run migrations on test database
uv run alembic upgrade head

# Test the complete database integration
uv run pytest tests/integration/db/ -v

# Test booking workflow end-to-end
# 1. Create user from Telegram interaction
# 2. Create booking without prepayment
# 3. Modify booking level
# 4. Persist LangGraph conversation state
# 5. Retrieve booking history

# Expected: All operations succeed with proper data consistency
```

## Final validation Checklist

- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] No linting errors: `uv run ruff check .`
- [ ] No type errors: `uv run mypy .`
- [ ] No format issues: `uv run ruff format . --check`
- [ ] Database migrations run successfully: `uv run alembic upgrade head`
- [ ] Database rollback works: `uv run alembic downgrade -1`
- [ ] Booking creation without prepayment works correctly
- [ ] Booking level modification workflow functions properly
- [ ] LangGraph state persistence maintains conversation continuity
- [ ] User registration and lookup via Telegram ID works
- [ ] Repository pattern follows Clean Architecture principles
- [ ] All database operations are properly transactional
- [ ] Connection pooling and async patterns perform efficiently
- [ ] Integration tests pass with real database connections

---

## Anti-Patterns to Avoid

- ❌ Don't use sync SQLAlchemy patterns - use AsyncSession throughout
- ❌ Don't bypass repository pattern - maintain Clean Architecture boundaries
- ❌ Don't ignore transaction management - ensure proper rollback on errors
- ❌ Don't hardcode database connections - use dependency injection
- ❌ Don't skip migration testing - ensure rollback capabilities work
- ❌ Don't mix domain and infrastructure concerns - keep layers separate
- ❌ Don't ignore async patterns - all database operations must be async
- ❌ Don't skip audit trails - track booking modifications for business needs
- ❌ Don't use raw SQL unless necessary - prefer SQLAlchemy ORM patterns
- ❌ Don't ignore connection pooling - configure for production performance

## Score Assessment

**Confidence Level: 9.5/10**

This comprehensive PRP provides exceptional context for one-pass implementation:

- ✅ Complete analysis of existing domain entities and their database mapping requirements
- ✅ Detailed SQLAlchemy 2.x async patterns with proper repository implementation
- ✅ Comprehensive schema design covering bookings, users, and chat conversation state
- ✅ Clear task breakdown following Clean Architecture principles with dependency injection
- ✅ Proper Alembic migration setup with async engine support and UV integration
- ✅ Booking modification workflow with audit tracking and level change support
- ✅ LangGraph state persistence for conversation continuity across sessions
- ✅ Extensive test coverage including unit tests, integration tests, and migration testing
- ✅ Performance optimization with connection pooling and async patterns
- ✅ Transaction management and error handling for data consistency
- ✅ User management integration with Telegram ID mapping and authentication
- ✅ Business workflow support for bookings without prepayment requirements

**Key Implementation Advantages:**

- **Data Persistence**: Complete booking and user data preservation with audit trails
- **Conversation Continuity**: LangGraph state persistence enables seamless multi-turn conversations
- **Business Flexibility**: Support for booking modifications and level changes without data loss
- **Scalability**: Proper database design with indexes, constraints, and connection pooling
- **Clean Architecture**: Repository pattern maintains clear separation of concerns
- **Development Workflow**: Alembic migrations enable safe schema evolution

The implementation should succeed with very high confidence given the existing SQLAlchemy configuration, detailed domain entities, clear async patterns, and comprehensive database design. This approach will provide robust data persistence while maintaining the existing Clean Architecture principles and supporting all current and future business requirements.
