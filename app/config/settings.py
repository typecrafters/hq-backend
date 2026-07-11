from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

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

    def database_url(self) -> str:
        engine = f"{self.db_engine}+{self.db_driver}" if self.db_driver else self.db_engine
        return f"{engine}://{self.db_user}:{self.db_pass.get_secret_value()}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()