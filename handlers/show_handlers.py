import redis
import json

# Подключение к базе данных Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Получение всех ключей
keys = r.keys('*')

# Вывод всех ключей
print("Все ключи:")
for key in keys:
    print(key.decode())  # Преобразование байтовой строки в строку

# Получение и преобразование данных для каждого ключа
print("\nДанные:")
for key in keys:
    data = r.get(key)
    if data is not None:
        decoded_data = json.loads(data.decode())
        print(key.decode(), decoded_data)
