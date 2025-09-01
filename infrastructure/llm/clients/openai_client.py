from langchain_openai import ChatOpenAI

from core.config import settings


def get_llm():
    return ChatOpenAI(
        model=getattr(settings, "OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        api_key=settings.openai_api_key,
    )
