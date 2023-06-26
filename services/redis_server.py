import redis
from config_data.config import Config, load_config


def create_redis_client():
    config: Config = load_config()
    r = redis.Redis(host=config.redis.host, port=config.redis.port)
    return r
