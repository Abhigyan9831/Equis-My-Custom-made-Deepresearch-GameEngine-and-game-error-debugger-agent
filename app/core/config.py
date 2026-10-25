
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    

   
    GROQ_API_KEY: str
    GROQ_MODEL_ID: str = "openai/gpt-oss-20b"

    
    GEMINI_API_KEY: str
    GEMINI_LLM_MODEL: str = "gemini-3-flash-preview"
    GEMINI_VLM_MODEL: str = "gemini-3.5-flash"
    GEMINI_EMBED_MODEL: str = "models/gemini-embedding-001"
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str = "gameengine-doctor"
    TAVILY_API_KEY: str
    UPSTASH_REDIS_REST_URL: str
    UPSTASH_REDIS_REST_TOKEN: str
    LANGCHAIN_TRACING_V2: str = "true"
    LANGCHAIN_API_KEY: str
    LANGCHAIN_PROJECT: str = "gameengine-doctor"

    
    DOCS_PATH: str = "./data/docs"
    TOP_K: int = 4
    CACHE_TTL_SECONDS: int = 3600

    VULKAN_URLS: list[str] = [
        "https://registry.khronos.org/vulkan/specs/1.3/html/vkspec.html",
        "https://vulkan-tutorial.com/Introduction",
    ]
    UE5_URLS: list[str] = [
        "https://docs.unrealengine.com/5.0/en-US/rendering-and-graphics-in-unreal-engine/",
        "https://docs.unrealengine.com/5.0/en-US/vulkan-mobile-renderer-for-unreal-engine/",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()