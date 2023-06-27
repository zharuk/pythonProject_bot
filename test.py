import json

import redis

# Подключение к Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Получаем все значение из Redis

value = r.get('001')
json_value = json.loads(value)
value_variants = json_value['variants']
print(value_variants)
value_variants[0]['stock'] = 10  # Замените 10 на ваше новое значение
json_value['variants'] = value_variants
updated_value = json.dumps(json_value)
r.set('001', updated_value)