import json

import redis
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

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

# Создаем список списков с кнопками
keyboard: list[list[KeyboardButton]] = [[KeyboardButton(text=str(i)) for i in range(1, 4)],
                                        [KeyboardButton(text=str(i)) for i in range(4, 7)], KeyboardButton(text='7')]

# Создаем объект клавиатуры, добавляя в него кнопки
my_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=keyboard,
    resize_keyboard=True)
# Создаем список списков с кнопками
keyboard: list[KeyboardButton] = [
    KeyboardButton(text=str(i)) for i in range(1, 8)]

# Инициализируем билдер
builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()

builder.row(*keyboard)

# Создаем объект клавиатуры, добавляя в него кнопки
my_keyboard: ReplyKeyboardMarkup = builder.as_markup(resize_keyboard=True)
# Создаем список списков с кнопками
keyboard: list[list[KeyboardButton]] = [[KeyboardButton(
    text=str(i)) for i in range(1, 8)]]

# Создаем объект клавиатуры, добавляя в него кнопки
my_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=keyboard,
    resize_keyboard=True)
# Создаем список списков с кнопками
keyboard: list[KeyboardButton] = [
    KeyboardButton(text=str(i)) for i in range(1, 8)]

# Инициализируем билдер
builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()

# Добавляем кнопки в билдер
builder.row(*keyboard, width=3)

# Создаем объект клавиатуры, добавляя в него кнопки
my_keyboard: ReplyKeyboardMarkup = builder.as_markup(resize_keyboard=True)
# Создаем список списков с кнопками
keyboard: list[list[KeyboardButton]] = [
    [KeyboardButton(text=str(i)) for i in range(1, 4)],
    [KeyboardButton(text=str(i)) for i in range(4, 7)],
    [KeyboardButton(text=str(i)) for i in range(7, 9)]]

# Создаем объект клавиатуры, добавляя в него кнопки
my_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=keyboard,
    resize_keyboard=True)
# Создаем список списков с кнопками
keyboard: list[list[KeyboardButton]] = [[KeyboardButton(text=str(i)) for i in range(1, 4)],
                                        [KeyboardButton(text=str(i)) for i in range(4, 7)], [KeyboardButton(text='7')]]

# Создаем объект клавиатуры, добавляя в него кнопки
my_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=keyboard,
    resize_keyboard=True)