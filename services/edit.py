# Функция редактирования имени товара, принимает на вход словарь с товаром товара и новое имя
import re

from lexicon.lexicon import LEXICON_RUSSIAN_SIZES


async def edit_name(product, new_name):
    # Меняем имя основного товара
    product['name'] = new_name
    # Меняем имя вариантов товара. Новое имя вараинта товара должно формироваться по следующему шаблону:
    # <Название товара> <Артикул> (<Цвет> <Размер>)
    for variant in product['variants']:
        variant['name'] = f"{new_name} {variant['sku']} ({variant['color']} {variant['size']})"
    # Возвращаем измененный товар
    return product


# Функция редактирования описания товара, принимает на вход словарь с товаром и новое описание
async def edit_description(product, new_description):
    # Меняем описание основного товара
    product['description'] = new_description
    # Возвращаем измененный товар
    return product


# Меняем артикул вариантов товара.
async def edit_sku(product, new_sku):
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
async def edit_color(product, old_color, new_color):
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
async def edit_size(product, old_size, new_size):
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
async def edit_price(product, new_price):
    # Меняем цену основного товара
    product['price'] = new_price
    # Меняем цену вариантов товара
    for variant in product['variants']:
        variant['price'] = new_price
    # Возвращаем измененный товар
    return product


# Функция изменения остатка определенной комплектации товара, принимает на вход словарь с товаром,
# артикул комплектации и новый остаток
async def edit_stock(product, sku, new_quantity):
    # Меняем остаток комплектации товара
    for variant in product['variants']:
        if variant['sku'] == sku:
            variant['stock'] = new_quantity
    # Возвращаем измененный товар
    return product


# Функция выводящая остаток товара комплектации, принимает на вход словарь с товаром и артикул комплектации
async def get_stock(product, variant_sku):
    # Выводим остаток комплектации товара
    for variant in product['variants']:
        if variant['sku'] == variant_sku:
            return variant['stock']


# Функция проверки строки на цифры и спецсимволы, принимает на вход строку. Для проверки корректности ввода цвета.
async def check_color(color):
    # Проверяем строку на наличие цифр и спецсимволов
    if re.search(r'\d', color) or re.search(r'[!@#$%^&*()_+=]', color):
        return False
    else:
        return True


# Функция проверки цветов на корректность, принимает на вход список цветов. Для проверки корректности ввода цветов.
async def check_colors(colors):
    # Проверяем каждый цвет в списке на наличие цифр и спецсимволов
    for color in colors:
        if re.search(r'\d', color) or re.search(r'[!@#$%^&*()_+=]', color):
            return False
    return True


# Функция валидности размера, принимает на вход строку. Просто проверяет а есть ли размер в списке размеров
# LEXICON_RUSSIAN_SIZES
async def check_size(size):
    if size in LEXICON_RUSSIAN_SIZES:
        return True
    else:
        return False


# Функция валидности размеров, принимает на вход список размеров. Просто проверяет а есть ли размеры в списке
# размеров LEXICON_RUSSIAN_SIZES
async def check_sizes(sizes):
    for size in sizes:
        if size not in LEXICON_RUSSIAN_SIZES:
            return False
    return True


# Функция валидности цены, принимает на вход строку. Проверяет что в строке только цифры.
async def check_price(price):
    if re.search(r'\D', price):
        return False
    else:
        return True


# Функция валидности остатка, принимает на вход строку. Проверяет что в строке только цифры и цифра не больше 100.
async def check_stock(quantity):
    if re.search(r'\D', quantity) or int(quantity) > 100:
        return False
    else:
        return True
