from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_PROTO: str
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int

    @property
    def DB_DSN(self):
        db_dsn: str = f"{self.DB_PROTO}://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return db_dsn

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore
