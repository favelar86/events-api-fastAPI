from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Pydantic Settings lê automaticamente do arquivo .env ou do ambiente.
    Nunca coloque senhas no código — use variáveis de ambiente.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    database_url: str = "postgresql://postgres:postgres@localhost:5432/events_db"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"


settings = Settings()