from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
import os


load_dotenv()


class Settings(BaseModel):
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    docs_dir: Path = Path(os.getenv("DOCS_DIR", "docs"))
    mock_data_dir: Path = Path(os.getenv("MOCK_DATA_DIR", "mock_data"))
    vector_store_dir: Path = Path(os.getenv("VECTOR_STORE_DIR", "vector_store"))
    logs_dir: Path = Path(os.getenv("LOGS_DIR", "logs"))


settings = Settings()


def validate_settings() -> None:
    if settings.llm_provider == "openai" and not settings.openai_api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing. Add it to your .env file or switch LLM_PROVIDER to local."
        )

    settings.docs_dir.mkdir(exist_ok=True)
    settings.mock_data_dir.mkdir(exist_ok=True)
    settings.vector_store_dir.mkdir(exist_ok=True)
    settings.logs_dir.mkdir(exist_ok=True)