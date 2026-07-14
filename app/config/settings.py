from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    db_driver: str
    db_engine: str
    db_name: str
    db_host: str
    db_port: int
    db_user: str
    db_pass: SecretStr

    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_pass: SecretStr
    smtp_from: str

    s3_endpoint: str
    s3_access_key: str
    s3_secret_key: str
    s3_secure: bool
    s3_bucket: str

    frontend_url: str

    cors_origins: str
    cors_methods: str
    cors_headers: str
    cors_credentials: bool

    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def cors_methods_list(self) -> list[str]:
        return [m.strip() for m in self.cors_methods.split(",") if m.strip()]

    def cors_headers_list(self) -> list[str]:
        return [h.strip() for h in self.cors_headers.split(",") if h.strip()]

    def database_url(self) -> str:
        engine = f"{self.db_engine}+{self.db_driver}" if self.db_driver else self.db_engine
        url = f"{engine}://{self.db_user}:{self.db_pass.get_secret_value()}@{self.db_host}:{self.db_port}/{self.db_name}"
        print(f"INFO:\tDatabase URL: {url}")
        return url


settings = Settings()