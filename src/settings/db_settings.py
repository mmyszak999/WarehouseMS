from pydantic import BaseSettings


class DatabaseSettings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int
    TEST_POSTGRES_DB: str
    ASYNC: bool = True
    TESTING: bool = False

    class Config:
        env_file = ".env"
        
    @property
    def postgres_url(self) -> str:
        db_name = self.TEST_POSTGRES_DB if self.TESTING else self.POSTGRES_DB
        db_driver = "postgresql+asyncpg" if self.ASYNC else "postgresql"
        return (
            f"{db_driver}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{db_name}"
        )

settings = DatabaseSettings()

