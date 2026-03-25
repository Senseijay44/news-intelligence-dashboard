from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "News Intelligence Dashboard"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000
    database_url: str
    newsapi_key: str = ""
    default_news_query: str = "world OR politics OR economy OR conflict OR science"
    ingest_interval_minutes: int = 15
    ingest_page_size: int = 100
    ingest_max_pages: int = 5
    ingest_max_articles_per_run: int = 500

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def has_valid_newsapi_key(self) -> bool:
        return bool(self.newsapi_key.strip()) and self.newsapi_key.strip().lower() != "replace_me"


settings = Settings()
