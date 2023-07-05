from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту


@dataclass
class Redis:
    host: str
    port: int


@dataclass
class Config:
    tg_bot: TgBot
    redis: Redis


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(token=env('BOT_TOKEN')),
        redis=Redis(
            host=env('REDIS_HOST'),
            port=env.int('REDIS_PORT'),
        )
    )
