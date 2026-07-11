from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Phase 1 - dataset paths
    dataset_dir: Path = Path("dataset")
    claims_filename: str = "claims.csv"
    sample_claims_filename: str = "sample_claims.csv"
    user_history_filename: str = "user_history.csv"
    evidence_requirements_filename: str = "evidence_requirements.csv"
    log_level: str = "INFO"

    # Phase 2 - Groq
    groq_api_key: str = ""
    model_name: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    temperature: float = 0.0
    max_output_tokens: int = 1024
    image_max_dimension: int = 1024
    image_jpeg_quality: int = 85
    max_images_per_request: int = 5
    max_retries: int = 3
    retry_delay_seconds: float = 5.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def claims_path(self) -> Path:
        return self.dataset_dir / self.claims_filename

    @property
    def sample_claims_path(self) -> Path:
        return self.dataset_dir / self.sample_claims_filename

    @property
    def user_history_path(self) -> Path:
        return self.dataset_dir / self.user_history_filename

    @property
    def evidence_requirements_path(self) -> Path:
        return self.dataset_dir / self.evidence_requirements_filename


@lru_cache
def get_settings() -> Settings:
    return Settings()