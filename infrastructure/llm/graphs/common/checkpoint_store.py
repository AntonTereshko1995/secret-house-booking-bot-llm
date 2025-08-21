from core.config import settings
from langgraph.checkpoint.memory import MemorySaver

def create_checkpointer():
    """Создать checkpointer для сохранения состояния"""
    return MemorySaver()
