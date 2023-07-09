# Функция редактирования имени товара, принимает на вход словарь с товаром товара и новое имя
import re

from lexicon.lexicon import LEXICON_RUSSIAN_SIZES


def edit_name(product, new_name):
    # Меняем имя основного товара
    product['name'] = new_name
    # Меняем имя вариантов товара. Новое имя вараинта товара должно формироваться по следующему шаблону:
    # <Название товара> <Артикул> (<Цвет> <Размер>)
    for variant in product['variants']:
        variant['name'] = f"{new_name} {variant['sku']} ({variant['color']} {variant['size']})"
    # Возвращаем измененный товар
    return product


# Функция редактирования описания товара, принимает на вход словарь с товаром и новое описание
def edit_description(product, new_description):
    # Меняем описание основного товара
    product['description'] = new_description
    # Возвращаем измененный товар
    return product


# Меняем артикул вариантов товара. Новый артикул варианта товара должен формироваться по следующему шаблону:
# К каждой комплектации товара добавляем -1, -2, -3 итд, например: 1234-1, 1234-2, 1234-3 итд.
# Также меняем названия вариантов товара. Новое название варианта товара должно формироваться по следующему шаблону:
# <Название товара> <Артикул-1, -2 итд> (<Цвет> <Размер>)
# Например:
# "Куртка 1234-1 (Красный 42)"
# "Куртка 1234-2 (Красный 44)"
# "Куртка 1234-3 (белый 42)"
# "Куртка 1234-4 (белый 44)"
def edit_sku(product, new_sku):
    # Меняем артикул основного товара
    product['sku'] = new_sku
    # Меняем артикул вариантов товара и их названия
    i = 1
    for variant in product['variants']:
        variant['sku'] = f"{new_sku}-{i}"
        variant['name'] = f"{product['name']} {variant['sku']} ({variant['color']} {variant['size']})"
        i += 1
    # Возвращаем измененный товар
    return product


# Функция редактирования цветов товара, принимает на вход словарь с товаром, цвет для замены и новый цвет
def edit_color(product, old_color, new_color):
    # Меняем цвет основного товара
    for color in product['colors']:
        # Если находим цвет для замены, то удаляем его из списка цветов товара и добавляем новый цвет
        if color == old_color:
            product['colors'].remove(color)
            product['colors'].append(new_color)

    # Меняем цвет вариантов товара
    for variant in product['variants']:
        if variant['color'] == old_color:
            variant['color'] = new_color
    # Меняем название вариантов товара
    for variant in product['variants']:
        variant['name'] = f"{product['name']} {variant['sku']} ({variant['color']} {variant['size']})"
    # Возвращаем измененный товар
    return product


# Функция редактирования размеров товара, принимает на вход словарь с товаром, размер для замены и новый размер.
# Функция аналогична функции edit_color
def edit_size(product, old_size, new_size):
    for size in product['sizes']:
        if size == old_size:
            product['sizes'].remove(size)
            product['sizes'].append(new_size)

    for variant in product['variants']:
        if variant['size'] == old_size:
            variant['size'] = new_size

    for variant in product['variants']:
        variant['name'] = f"{product['name']} {variant['sku']} ({variant['color']} {variant['size']})"
    return product


# Функция редактирования цены товара, принимает на вход словарь с товаром и новую цену
def edit_price(product, new_price):
    # Меняем цену основного товара
    product['price'] = new_price
    # Меняем цену вариантов товара
    for variant in product['variants']:
        variant['price'] = new_price
    # Возвращаем измененный товар
    return product


# Функция изменения остатка определенной комплектации товара, принимает на вход словарь с товаром,
# артикул комплектации и новый остаток
def edit_stock(product, sku, new_quantity):
    # Меняем остаток комплектации товара
    for variant in product['variants']:
        if variant['sku'] == sku:
            variant['stock'] = new_quantity
    # Возвращаем измененный товар
    return product


# Функция выводящая остаток товара комплектации, принимает на вход словарь с товаром и артикул комплектации
def get_stock(product, variant_sku):
    # Выводим остаток комплектации товара
    for variant in product['variants']:
        if variant['sku'] == variant_sku:
            return variant['stock']


# Функция проверки строки на цифры и спецсимволы, принимает на вход строку. Для проверки корректности ввода цвета.
def check_color(color):
    # Проверяем строку на наличие цифр и спецсимволов
    if re.search(r'\d', color) or re.search(r'[!@#$%^&*()_+=]', color):
        return False
    else:
        return True


# Функция валидности размера, принимает на вход строку. Просто проверяет а есть ли размер в списке размеров
# LEXICON_RUSSIAN_SIZES
def check_size(size):
    if size in LEXICON_RUSSIAN_SIZES:
        return True
    else:
        return False


# Функция валидности цены, принимает на вход строку. Проверяет что в строке только цифры.
def check_price(price):
    if re.search(r'\D', price):
        return False
    else:
        return True


# Функция валидности остатка, принимает на вход строку. Проверяет что в строке только цифры и цифра не больше 100.
def check_stock(quantity):
    if re.search(r'\D', quantity) or int(quantity) > 100:
        return False
    else:
        return True
