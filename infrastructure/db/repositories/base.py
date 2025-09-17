"""
Base repository with common CRUD operations

Provides generic database operations using SQLAlchemy 2.x async patterns.
All specific repositories should inherit from this base class.
"""

from abc import ABC
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.logging import get_logger
from infrastructure.db.models.base import BaseModel

logger = get_logger(__name__)

# Generic type for domain entities
DomainEntity = TypeVar("DomainEntity")
# Generic type for database models
DatabaseModel = TypeVar("DatabaseModel", bound=BaseModel)


class BaseRepository(Generic[DomainEntity, DatabaseModel], ABC):
    """Base repository with common CRUD operations"""
    
    def __init__(self, session: AsyncSession, model_class: Type[DatabaseModel]):
        """Initialize repository
        
        Args:
            session: Async SQLAlchemy session
            model_class: Database model class
        """
        self.session = session
        self.model_class = model_class
    
    async def create(self, entity_data: Dict[str, Any]) -> DatabaseModel:
        """Create new entity in database
        
        Args:
            entity_data: Dictionary with entity data
            
        Returns:
            Created database model instance
        """
        try:
            db_entity = self.model_class(**entity_data)
            self.session.add(db_entity)
            await self.session.flush()
            await self.session.refresh(db_entity)
            
            logger.info(
                f"Created {self.model_class.__name__}",
                extra={"entity_id": str(db_entity.id)}
            )
            
            return db_entity
            
        except Exception as e:
            logger.error(
                f"Error creating {self.model_class.__name__}: {e}",
                extra={"entity_data": entity_data}
            )
            raise
    
    async def find_by_id(self, entity_id: UUID) -> Optional[DatabaseModel]:
        """Find entity by ID
        
        Args:
            entity_id: Entity UUID
            
        Returns:
            Database model instance or None if not found
        """
        try:
            result = await self.session.get(self.model_class, entity_id)
            return result
            
        except Exception as e:
            logger.error(
                f"Error finding {self.model_class.__name__} by ID: {e}",
                extra={"entity_id": str(entity_id)}
            )
            raise
    
    async def find_all(
        self, 
        limit: Optional[int] = None, 
        offset: Optional[int] = None
    ) -> List[DatabaseModel]:
        """Find all entities with optional pagination
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of database model instances
        """
        try:
            stmt = select(self.model_class)
            
            if offset:
                stmt = stmt.offset(offset)
            if limit:
                stmt = stmt.limit(limit)
                
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Error finding all {self.model_class.__name__}: {e}")
            raise
    
    async def update(self, entity_id: UUID, updates: Dict[str, Any]) -> Optional[DatabaseModel]:
        """Update entity with partial data
        
        Args:
            entity_id: Entity UUID
            updates: Dictionary with fields to update
            
        Returns:
            Updated database model instance or None if not found
        """
        try:
            stmt = (
                update(self.model_class)
                .where(self.model_class.id == entity_id)
                .values(**updates)
            )
            
            result = await self.session.execute(stmt)
            
            if result.rowcount == 0:
                return None
                
            await self.session.commit()
            
            # Fetch updated entity
            updated_entity = await self.find_by_id(entity_id)
            
            logger.info(
                f"Updated {self.model_class.__name__}",
                extra={"entity_id": str(entity_id), "updates": updates}
            )
            
            return updated_entity
            
        except Exception as e:
            logger.error(
                f"Error updating {self.model_class.__name__}: {e}",
                extra={"entity_id": str(entity_id), "updates": updates}
            )
            raise
    
    async def delete(self, entity_id: UUID) -> bool:
        """Delete entity by ID
        
        Args:
            entity_id: Entity UUID
            
        Returns:
            True if entity was deleted, False if not found
        """
        try:
            stmt = delete(self.model_class).where(self.model_class.id == entity_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            deleted = result.rowcount > 0
            
            if deleted:
                logger.info(
                    f"Deleted {self.model_class.__name__}",
                    extra={"entity_id": str(entity_id)}
                )
            
            return deleted
            
        except Exception as e:
            logger.error(
                f"Error deleting {self.model_class.__name__}: {e}",
                extra={"entity_id": str(entity_id)}
            )
            raise
    
    async def exists(self, entity_id: UUID) -> bool:
        """Check if entity exists
        
        Args:
            entity_id: Entity UUID
            
        Returns:
            True if entity exists, False otherwise
        """
        try:
            stmt = select(self.model_class.id).where(self.model_class.id == entity_id)
            result = await self.session.execute(stmt)
            return result.first() is not None
            
        except Exception as e:
            logger.error(
                f"Error checking existence of {self.model_class.__name__}: {e}",
                extra={"entity_id": str(entity_id)}
            )
            raise
    
    async def count(self) -> int:
        """Count total number of entities
        
        Returns:
            Total count of entities
        """
        try:
            stmt = select(self.model_class.id)
            result = await self.session.execute(stmt)
            return len(list(result.scalars().all()))
            
        except Exception as e:
            logger.error(f"Error counting {self.model_class.__name__}: {e}")
            raise