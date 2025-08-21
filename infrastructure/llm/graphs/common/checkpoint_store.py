from core.config import settings
from langgraph.checkpoint.memory import MemorySaver

def create_checkpointer():
    """Create checkpointer for state persistence"""
    return MemorySaver()
