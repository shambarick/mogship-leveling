from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    es_hosts: str = "localhost:9200"
    es_user: str
    es_password: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
