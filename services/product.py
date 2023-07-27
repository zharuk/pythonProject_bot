import datetime
from services.redis_server import check_and_create_structure_reports, get_data_from_redis, save_data_to_redis
from aiogram.types import InputMediaPhoto


# Класс для создания экземпляров товаров
# При создании экземпляра класса Product, мы передаем в него все необходимые параметры
# и он генерирует список вариантов товара
class Product:
    def __init__(self, name: str, description: str, sku: str, colors: str, sizes: str, price: float | int | str,
                 photo_ids: list) -> None:
        self.name = name
        self.description = description
        self.sku = sku
        self.colors = colors.split()
        self.sizes = sizes.split()
        self.price = price
        self.variants = self.generate_variants()
        self.photo_ids = photo_ids

    def generate_variants(self) -> list[dict[str, [str, float, int]]]:
        variants = []
        i = 1
        for color in self.colors:
            for size in self.sizes:
                variant_sku = f"{self.sku}-{i}"
                variant_name = f"{self.name} {self.sku} ({size} {color})"
                variant = {
                    "name": variant_name,
                    "sku": variant_sku,
                    "color": color,
                    "size": size,
                    "price": self.price,
                    "stock": 0,
                }
                variants.append(variant)
                i += 1
        return variants


# Функция для формирования основной информации о товаре
# На вход функция принимает словарь с информацией о товаре и формирует текстовое сообщение
async def format_main_info(product: dict, currency: str) -> str:
    response_text = f"➡ Название: {product['name']}\n" \
                    f"➡ Описание: {product['description']}\n" \
                    f"➡ Артикул: {product['sku']}\n" \
                    f"➡ Цвета: {', '.join(product['colors'])}\n" \
                    f"➡ Размеры: {', '.join(product['sizes'])}\n" \
                    f"➡ Цена: {product['price']} {currency}\n"
    return response_text


# Функция получения товара по sku в словаре user_data.
async def get_product_from_data(main_sku: str, user_data: dict) -> dict or bool:
    # Поиск товара по sku в user_data
    for product in user_data['products']:
        d_key = list(product.keys())[0]
        if d_key == main_sku:
            return product[main_sku]
    return False


# Функция проверки товара по ключу "products" в Redis
async def check_product_in_redis(user_id: str | int, main_sku: str) -> bool:
    # Получение данных из Redis
    data_user = await get_data_from_redis(user_id)
    # Проверка наличия sku в data_user
    for product in data_user['products']:
        d_key = list(product.keys())[0]
        if d_key == main_sku:
            return True
    return False


# Функция замены товара по артикулу из словаря user_data, обновляет артикул и удаляет старый артикул
async def remove_product_from_data(old_sku: str, new_sku: str, user_data: dict) -> dict:
    # Поиск товара по sku в user_data
    for product in user_data['products']:
        d_key = list(product.keys())[0]
        print(d_key)
        if d_key == old_sku:
            # Создаем копию товара
            product_copy = product[old_sku].copy()
            print(product_copy)
            # Удаляем товар из user_data по старому sku
            user_data['products'].remove(product)
            # Добавляем товар в user_data по новому sku
            user_data['products'].append({new_sku: product_copy})
            print(user_data)
            return user_data


# Функция удаления товара по артикулу из словаря user_data
async def delete_product_from_data(sku: str, user_data: dict) -> dict:
    # Поиск товара по sku в user_data
    for product in user_data['products']:
        d_key = list(product.keys())[0]
        if d_key == sku:
            # Удаляем товар из user_data по старому sku
            user_data['products'].remove(product)
            return user_data


# Функция для формирования сообщения со списком вариантов товара
# На вход функция принимает список вариантов товара и формирует текстовое сообщение
async def format_variants_message(variants: list, currency: str) -> str:
    message = "Список вариантов:\n\n"
    for variant in variants:
        color = variant['color']
        size = variant['size']
        sku = variant['sku']
        price = variant['price']
        stock = variant['stock']
        message += f"➡️ Комплектация: {color} {size}\n"
        message += f"Артикул: {sku}\n"
        message += f"Цена: {price}{currency} \n"
        message += f"✅ На складе: <b>{stock}</b>\n\n" if int(stock) > 0 else '<b>❌ Нет в наличии</b>\n\n'
    return message


# Функция для формирования списка фотографий товара
# На вход функция принимает список вариантов товара и формирует список фотографий
async def generate_photos(variants: list) -> list:
    photos = [photo_id['id'] for photo_id in variants[:10]]  # Используем срез [:10] для получения максимум 10 элементов
    media = [InputMediaPhoto(media=photo_id) for photo_id in photos]
    return media


# Функция для добавления товара в проданные
async def sell_product(user_id: int, variant_sku: str, quantity: int):
    # Обрезаем артикул до основного значения
    main_sku = variant_sku.split('-')[0]
    required = None

    # Получаем data_user из Redis
    data_user = await get_data_from_redis(user_id)
    # Получаем нужный товар из data_user
    product = await get_product_from_data(main_sku, data_user)

    # Проверяем наличие товара в базе данных
    if product is None:
        return False

    # Получаем варианты товара
    variants = product['variants']

    # Находим нужную комплектацию из всех вариантов
    for variant in variants:
        if variant['sku'] == variant_sku:
            # Получаем нужную комплектацию товара
            required = variant

    # Проверяем наличие достаточного количества товара
    required['stock'] = int(required['stock'])
    if required['stock'] < quantity:
        return False
    else:
        # Вычитаем проданный товар из остатков
        required['stock'] -= quantity
        # Обновляем остатки товара в базе данных
        await save_data_to_redis(user_id, data_user)

    # Получаем текущую дату и время
    current_date = datetime.datetime.now().strftime('%d.%m.%Y')
    current_time = datetime.datetime.now().strftime('%H:%M:%S')

    # Проверяем структуру reports функцией check_and_create_structure_reports
    await check_and_create_structure_reports(user_id)

    # Получаем текущий отчет sold_products из базы данных
    report_data_sold_today = data_user['reports'][current_date]['sold_products']

    report_data_sold_today.append({
        'name': required['name'],
        'sku': variant_sku,
        'color': required['color'],
        'size': required['size'],
        'quantity': quantity,
        'price': int(required['price']),
        'total': int(quantity) * int(required['price']),
        'time': current_time
    })

    # Cохраняем отчет в базе данных
    await save_data_to_redis(user_id, data_user)

    return True


# Функция для возврата товара и формирования отчета работает по принципу функции sell_product
async def return_product(user_id: int, variant_sku: str, quantity: int):
    # Обрезаем артикул до основного значения
    main_sku = variant_sku.split('-')[0]
    required = None

    # Получаем data_user из Redis
    data_user = await get_data_from_redis(user_id)
    # Получаем нужный товар из data_user
    product = await get_product_from_data(main_sku, data_user)

    # Проверяем наличие товара в базе данных
    if product is None:
        return False

    # Получаем варианты товара
    variants = product['variants']

    # Находим нужную комплектацию из всех вариантов
    for variant in variants:
        if variant['sku'] == variant_sku:
            # Получаем нужную комплектацию товара
            required = variant

    # Добавляем возвращенный товар в остатки
    required['stock'] += quantity
    # Обновляем остатки товара в базе данных
    await save_data_to_redis(user_id, data_user)

    # Получаем текущую дату и время
    current_date = datetime.datetime.now().strftime('%d.%m.%Y')
    current_time = datetime.datetime.now().strftime('%H:%M:%S')

    # Проверяем структуру reports функцией check_and_create_structure_reports
    await check_and_create_structure_reports(user_id)

    # Получаем текущий отчет return_products из базы данных
    report_data_return_today = data_user['reports'][current_date]['return_products']

    report_data_return_today.append({
        'name': required['name'],
        'sku': variant_sku,
        'color': required['color'],
        'size': required['size'],
        'quantity': quantity,
        'price': int(required['price']),
        'total': int(quantity) * int(required['price']),
        'time': current_time
    })

    # Cохраняем отчет в базе данных
    await save_data_to_redis(user_id, data_user)

    return True


# Функция проверки строки на целое число в диапазоне от 1 до 100
async def check_int(value):
    try:
        # Преобразуем введенное значение в целое число
        number = int(value)
        # Проверяем, что число находится в диапазоне от 1 до 100
        if 1 <= number <= 100:
            return True
        else:
            return False
    except ValueError:
        # Если введено не число или оно не является целым числом, вернем False
        return False
