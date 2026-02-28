from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Groq LLM
    groq_api_key: str = ""
    groq_default_model: str = "llama-3.3-70b-versatile"

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "amd_web"

    # DigiKey
    digikey_client_id: str = ""
    digikey_client_secret: str = ""

    # Octopart
    octopart_api_key: str = ""

    # CORS
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


settings = Settings()
