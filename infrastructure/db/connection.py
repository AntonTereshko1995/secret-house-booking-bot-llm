"""
Database connection and session management

Provides async database engine and session management using SQLAlchemy 2.x
with asyncpg driver for PostgreSQL.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


class DatabaseConnection:
    """Async database connection management"""
    
    def __init__(self, database_url: str | None = None):
        """Initialize database connection
        
        Args:
            database_url: Database URL. If None, uses settings.database_url
        """
        self.database_url = database_url or settings.database_url
        
        # Create async engine with connection pooling
        self.engine = create_async_engine(
            self.database_url,
            echo=settings.database_echo,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_timeout=settings.database_pool_timeout,
            pool_recycle=settings.database_pool_recycle,
            pool_pre_ping=True,  # Verify connections before use
            # Use NullPool for testing to avoid connection issues
            poolclass=NullPool if "test" in self.database_url else None
        )
        
        # Create async session factory
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Allow access to objects after commit
            autoflush=True,
            autocommit=False
        )
        
        logger.info(
            "Database connection initialized",
            extra={
                "database_url": self.database_url.split("@")[-1] if "@" in self.database_url else self.database_url,
                "pool_size": settings.database_pool_size
            }
        )
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session with automatic cleanup
        
        Usage:
            async with db_connection.get_session() as session:
                # Use session for database operations
                # Transaction automatically commits or rolls back
        """
        async with self.session_factory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error, rolling back: {e}")
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    async def get_transaction(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session with explicit transaction management
        
        Usage:
            async with db_connection.get_transaction() as session:
                # All operations in this block are part of one transaction
                # Automatically commits on success, rolls back on error
        """
        async with self.session_factory() as session:
            async with session.begin():
                try:
                    yield session
                except Exception as e:
                    logger.error(f"Database transaction error, rolling back: {e}")
                    raise
    
    async def close(self) -> None:
        """Close database connections and cleanup resources"""
        await self.engine.dispose()
        logger.info("Database connections closed")
    
    async def health_check(self) -> bool:
        """Check database connectivity
        
        Returns:
            True if database is accessible, False otherwise
        """
        try:
            async with self.get_session() as session:
                await session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database connection instance
_db_connection: DatabaseConnection | None = None


def get_database_connection() -> DatabaseConnection:
    """Get global database connection instance"""
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session - convenience function
    
    Usage:
        async with get_session() as session:
            # Use session for database operations
    """
    db_connection = get_database_connection()
    async with db_connection.get_session() as session:
        yield session


@asynccontextmanager
async def get_transaction() -> AsyncGenerator[AsyncSession, None]:
    """Get database transaction - convenience function
    
    Usage:
        async with get_transaction() as session:
            # All operations are part of one transaction
    """
    db_connection = get_database_connection()
    async with db_connection.get_transaction() as session:
        yield session


async def close_database_connection() -> None:
    """Close global database connection"""
    global _db_connection
    if _db_connection is not None:
        await _db_connection.close()
        _db_connection = None