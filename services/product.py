import datetime
import json
from services.redis_server import check_and_create_structure_reports, get_data_from_redis
from aiogram.types import InputMediaPhoto


# Класс для создания экземпляров товаров
# При создании экземпляра класса Product, мы передаем в него все необходимые параметры
# и он генерирует список вариантов товара
class Product:
    def __init__(self, name: str, description: str, sku: str, colors: str, sizes: str, price: float, photo_ids: list) -> None:
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
def format_main_info(product: dict) -> str:
    response_text = f"➡ Название: {product['name']}\n" \
                    f"➡ Описание: {product['description']}\n" \
                    f"➡ Артикул: {product['sku']}\n" \
                    f"➡ Цвета: {', '.join(product['colors'])}\n" \
                    f"➡ Размеры: {', '.join(product['sizes'])}\n" \
                    f"➡ Цена: {product['price']}\n"
    return response_text


# Функция получения товара по sku в словаре user_data.
def get_product_from_data(main_sku: str, user_data: dict) -> dict or bool:
    # Поиск товара по sku в user_data
    for product in user_data['products']:
        d_key = list(product.keys())[0]
        if d_key == main_sku:
            return product[main_sku]
    return False


# Функция проверки товара по ключу "products" в Redis
def check_product_in_redis(user_id: str, main_sku: str) -> bool:
    # Получение данных из Redis
    data_user = get_data_from_redis(user_id)
    # Проверка наличия sku в data_user
    for product in data_user['products']:
        d_key = list(product.keys())[0]
        if d_key == main_sku:
            return True
    return False


# Функция для формирования сообщения со списком вариантов товара
# На вход функция принимает список вариантов товара и формирует текстовое сообщение
def format_variants_message(variants: list) -> str:
    message = "Список вариантов:\n\n"
    for variant in variants:
        color = variant['color']
        size = variant['size']
        sku = variant['sku']
        price = variant['price']
        stock = variant['stock']
        message += f"➡️ Комплектация: {color} {size}\n"
        message += f"Артикул: {sku}\n"
        message += f"Цена: {price} \n"
        message += f"✅ На складе: <b>{stock}</b>\n\n" if int(stock) > 0 else '<b>❌ Нет в наличии</b>\n\n'
    return message


# Функция для формирования списка фотографий товара
# На вход функция принимает список вариантов товара и формирует список фотографий
def generate_photos(variants: list) -> list:
    photos = [photo_id['id'] for photo_id in variants[:10]]  # Используем срез [:10] для получения максимум 10 элементов
    media = [InputMediaPhoto(media=photo_id) for photo_id in photos]
    return media


# Функция для добавления товара в проданные
def sell_product(sku: str, quantity: int):
    # Обрезаем артикул до основного значения
    main_sku = sku.split('-')[0]
    required = None

    # Получаем данные из базы данных
    product_data = r.get(main_sku)
    if product_data is None:
        return 'Товар не найден в базе данных!'

    # Конвертируем данные из JSON в словарь
    main_product = json.loads(product_data)

    # Получаем варианты товара
    variants = main_product['variants']

    # Находим нужную комплектацию из всех вариантов
    for variant in variants:
        if variant['sku'] == sku:
            # Получаем нужную комплектацию товара
            required = variant

    # Проверяем наличие достаточного количества товара
    required['stock'] = int(required['stock'])
    if required['stock'] < quantity:
        return 'Недостаточное количество товара на складе!'
    else:
        # Вычитаем проданный товар из остатков
        required['stock'] -= quantity

    # Обновляем остатки товара в базе данных
    r.set(main_sku, json.dumps(main_product))

    # Получаем текущую дату и время
    current_date = datetime.datetime.now().strftime('%d.%m.%Y')
    current_time = datetime.datetime.now().strftime('%H:%M:%S')

    # Проверяем структуру reports функцией check_and_create_structure_reports
    check_and_create_structure_reports()

    # Получаем текущий отчет sold_products из базы данных
    report_data = r.get('reports')
    if report_data is not None:
        # Если отчет уже существует, конвертируем его из JSON в словарь
        existing_report = json.loads(report_data)
        if 'sold_products' in existing_report:
            # Если есть запись sold_products, добавляем проданный товар к существующей записи
            existing_report['sold_products'][current_date].append({
                'sku': sku,
                'quantity': quantity,
                'price': int(required['price']),
                'total': int(quantity) * int(required['price']),
                'time': current_time
            })
        else:
            # Если записи sold_products нет, создаем новую запись
            existing_report['sold_products'] = {current_date: [{
                'sku': sku,
                'quantity': quantity,
                'price': int(required['price']),
                'total': int(quantity) * int(required['price']),
                'time': current_time
            }]}
        # Обновляем отчет в базе данных
        r.set('reports', json.dumps(existing_report))

    return True


# Функция для возврата товара и формирования отчета работает по принципу функции sell_product
def return_product(sku: str, quantity: int):
    # Обрезаем артикул до основного значения
    main_sku = sku.split('-')[0]
    required = None

    # Получаем данные из базы данных
    product_data = r.get(main_sku)
    if product_data is None:
        return 'Товар не найден в базе данных!'

    # Конвертируем данные из JSON в словарь
    main_product = json.loads(product_data)

    # Получаем варианты товара
    variants = main_product['variants']

    # Находим нужную комплектацию из всех вариантов
    for variant in variants:
        if variant['sku'] == sku:
            # Получаем нужную комплектацию товара
            required = variant

    # Прибавляем возвращенный товар к остаткам
    required['stock'] = int(required['stock'])
    required['stock'] += quantity

    # Обновляем остатки товара в базе данных
    r.set(main_sku, json.dumps(main_product))

    # Получаем текущую дату и время
    current_date = datetime.datetime.now().strftime('%d.%m.%Y')
    current_time = datetime.datetime.now().strftime('%H:%M:%S')

    # Проверяем структуру reports функцией check_and_create_structure_reports
    check_and_create_structure_reports()

    # Получаем текущий отчет return_products из базы данных
    report_data = r.get('reports')
    if report_data is not None:
        # Если отчет уже существует, конвертируем его из JSON в словарь
        existing_report = json.loads(report_data)
        if 'return_products' in existing_report:
            # Если есть запись return_products, добавляем проданный товар к существующей записи
            existing_report['return_products'][current_date].append({
                'sku': sku,
                'quantity': quantity,
                'price': int(required['price']),
                'total': int(quantity) * int(required['price']),
                'time': current_time
            })
        else:
            # Если записи return_products нет, создаем новую запись
            existing_report['return_products'] = {current_date: [{
                'sku': sku,
                'quantity': quantity,
                'price': int(required['price']),
                'total': int(quantity) * int(required['price']),
                'time': current_time
            }]}
        # Обновляем отчет в базе данных
        r.set('reports', json.dumps(existing_report))

    return True
