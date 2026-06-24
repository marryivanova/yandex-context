import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class DatabaseSettings(BaseSettings):
    host: str = os.getenv("DB_HOST")
    port: str = os.getenv("DB_PORT")
    user: str = os.getenv("DB_USER")
    password: str = os.getenv("DB_PASSWORD")
    database: str = os.getenv("DB_NAME")


class Settings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()


settings = Settings()
