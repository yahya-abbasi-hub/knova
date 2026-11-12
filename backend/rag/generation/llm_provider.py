from abc import ABC, abstractmethod

from groq import Groq

from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)


class LLMProvider(ABC):
    """
    Abstract base class every LLM provider must implement.
    This is what makes it possible to swap Groq for OpenAI/Gemini/local models
    later without changing any code that CALLS the LLM — only this file
    and its subclasses would need to change.
    """

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        ...


class GroqProvider(LLMProvider):
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.LLM_MODEL

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content


def get_llm_provider() -> LLMProvider:
    """
    Factory function — returns the configured provider.
    Everything else in the app calls THIS function, never GroqProvider directly.
    """
    if settings.LLM_PROVIDER == "groq":
        return GroqProvider()
    raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")