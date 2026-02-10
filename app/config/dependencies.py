from functools import lru_cache
from app.config.env_settings import EnvSettings


@lru_cache
def get_env_settings() -> EnvSettings:
    return EnvSettings()
