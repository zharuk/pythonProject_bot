import redis
import json
from services.product import Product
from config_data.config import load_config

config = load_config()
r: redis.Redis = redis.Redis(host=config.redis.host, port=config.redis.port, db=0, decode_responses=True)


def add_product_to_redis(product):
    key = product.sku  # Ключ, который будет использоваться для хранения товара в Redis
    value = json.dumps(product.__dict__)  # Сериализация объекта товара в формат JSON
    r.set(key, value)  # Добавление товара в Redis




# p = Product('Платье', 'Платье изо льна', '001', 'Красный, Белый', '42, 44', 150)
# add_product_to_redis(p)
#
# product = r.get('001')
# product = json.loads(product)
# print(product)
