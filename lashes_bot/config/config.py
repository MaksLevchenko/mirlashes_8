from pathlib import Path

from pydantic import model_validator, PostgresDsn, Field

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    # Конфигурация модели
    model_config = SettingsConfigDict(
        env_file="../.env",  # Файл с переменными окружения
        extra="ignore",  # Игнорируем лишние значения в env файле
        # env_file_encoding="utf-8",
    )

    # Postgres
    pg_scheme: str = "postgresql+psycopg"
    pg_host: str = "127.0.0.1"
    pg_port: int = 5432
    pg_db: str | None = None
    pg_user: str | None = None
    pg_password: str | None = None

    pg_engine_echo: bool = False  # # Вывод сгенерированных запросов в логи

    postgres_url: str | None = None

    # Телеграм бот
    bot_token: str = Field(..., env="BOT_TOKEN")
    # bot_token: str = "BOT_TOKEN"

    # Yclients
    yclients_token: str = Field(...)
    yclients_token_key: str = Field(...)
    yclients_token_partner: str = Field(...)

    @model_validator(mode="after")
    def setting_validator(self) -> "Config":
        file_version = ".version"
        if Path(file_version).exists():
            with open(file_version, "r") as fp:
                self.app_version = fp.readline()

        if not self.postgres_url:
            self.postgres_url = str(
                PostgresDsn.build(
                    scheme=self.pg_scheme,
                    username=self.pg_user,
                    password=self.pg_password,
                    host=self.pg_host,
                    # host="database",
                    port=self.pg_port,
                    path=self.pg_db,
                )
            )

        return self


config = Config()
