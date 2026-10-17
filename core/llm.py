import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_core.rate_limiters import InMemoryRateLimiter

load_dotenv()

# Stay well under free-tier request limits
_rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.4,
    check_every_n_seconds=0.1,
    max_bucket_size=1,
)


@lru_cache(maxsize=1)
def get_llm():
    """Shared chat model. Set LLM_PROVIDER=groq or mistral in .env."""
    provider = os.getenv("LLM_PROVIDER", "groq").lower()

    if provider == "groq":
        if not os.getenv("GROQ_API_KEY"):
            raise EnvironmentError("GROQ_API_KEY is missing. Add it to your .env file.")
        from langchain_groq import ChatGroq

        llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=0.2,
            rate_limiter=_rate_limiter,
        )

    elif provider == "mistral":
        if not os.getenv("MISTRAL_API_KEY"):
            raise EnvironmentError("MISTRAL_API_KEY is missing. Add it to your .env file.")
        from langchain_mistralai import ChatMistralAI

        llm = ChatMistralAI(
            model=os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
            temperature=0.2,
            rate_limiter=_rate_limiter,
        )

    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}. Use 'groq' or 'mistral'.")

    # If a 429 still happens, wait and retry instead of failing the pipeline
    return llm.with_retry(stop_after_attempt=6, wait_exponential_jitter=True)


def split_text(text: str, chunk_size: int = 6000, overlap: int = 300) -> list[str]:
    """Split long text into overlapping chunks that fit comfortably in a prompt."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.split_text(text)