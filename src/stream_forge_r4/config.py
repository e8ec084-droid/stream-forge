from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RocksDBSettings(BaseSettings):
    """Runtime configuration for the R4 state store."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db_path: str = Field(
        default="./rocksdb_state",
        alias="ROCKSDB_PATH",
    )

    create_if_missing: bool = Field(
        default=True,
        alias="ROCKSDB_CREATE_IF_MISSING",
    )


@lru_cache(maxsize=1)
def get_settings() -> RocksDBSettings:
    return RocksDBSettings()