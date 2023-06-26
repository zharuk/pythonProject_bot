import redis

# Подключение к Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Вывод всех ключей
keys = r.keys('*')
print("All Keys:")
for key in keys:
    print(key.decode())

# Удаление одного ключа
key_to_delete = 'платье супер хайк147'
result = r.delete(key_to_delete)
if result == 1:
    print(f"Key '{key_to_delete}' deleted successfully.")
else:
    print(f"Key '{key_to_delete}' does not exist or could not be deleted.")