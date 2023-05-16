import redis
import json

from aiogram.dispatcher import router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message

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


@router.message(Command(commands='show'))
async def process_show_command(message: Message):
    await message.answer(text='Список товаров:')
    # Устанавливаем состояние ожидания ввода имени
