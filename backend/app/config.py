from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    test_database_url: str = ""

    # frontend URLs allowed to call this API, comma-separated.
    # loaded from the CORS_ORIGINS env var — on Render this is set to the Vercel URL.
    # default = localhost, so local dev works without setting anything.
    cors_origins: str = "http://localhost:5173,http://localhost,http://localhost:80"

    model_config = SettingsConfigDict(env_file=".env")

    @property  # read as settings.cors_origin_list (no parentheses), like the other settings
    def cors_origin_list(self) -> list[str]:
        """Converts the comma-separated CORS_ORIGINS text into the list CORSMiddleware needs.

        e.g. "https://a.com, https://b.com," -> ["https://a.com", "https://b.com"]
        strip() removes stray spaces; `if o.strip()` drops empty pieces from a trailing comma.
        """
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
