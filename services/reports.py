import datetime
import json

from services.redis_server import create_redis_client

# Подключение к базе данных Redis
redis_db = create_redis_client()


# Функция для добавления товара в проданные
def sell_product(sku: str, quantity: int):
    # Обрезаем артикул до основного значения
    main_sku = sku.split('-')[0]

    # Получаем данные из базы данных
    product_data = redis_db.get(main_sku)
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
    if required['stock'] < quantity:
        return 'Недостаточное количество товара на складе!'
    else:
        # Вычитаем проданный товар из остатков
        required['stock'] -= quantity

    # Обновляем остатки товара в базе данных
    redis_db.set(main_sku, json.dumps(main_product))

    # Добавляем отчет
    today = datetime.date.today().strftime('%d.%m.%Y')
    report_data = {
        'date': today,
        'sold_products': [[sku, quantity, int(required['price']), quantity * int(required['price'])]],
        'returned_products': {}
    }

    reports_data = redis_db.get('reports')
    if reports_data is not None:
        reports = json.loads(reports_data)
    else:
        reports = {}

    if 'sold_products' in reports:
        reports['sold_products'].append(report_data['sold_products'])
    else:
        reports['sold_products'] = report_data['sold_products']

    redis_db.set('reports', json.dumps(reports))

    return 'Товар успешно продан!'


# Функция для возврата товара
# Функция для возврата товара
def return_product(sku: str, quantity: int):
    # Обрезаем артикул до основного значения
    main_sku = sku.split('-')[0]

    # Получаем данные из базы данных
    product_data = redis_db.get(main_sku)
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

    # Увеличиваем остаток товара на складе
    required['stock'] += quantity

    # Обновляем остатки товара в базе данных
    redis_db.set(main_sku, json.dumps(main_product))

    # Добавляем отчет о возвращенных товарах
    today = datetime.date.today().strftime('%d.%m.%Y')
    report_data = {
        'date': today,
        'sold_products': {},
        'returned_products': [[sku, quantity, int(required['price']), quantity * int(required['price'])]]
    }

    reports_data = redis_db.get('reports')
    if reports_data is not None:
        reports = json.loads(reports_data)
    else:
        reports = {}

    if 'returned_products' in reports:
        reports['returned_products'].append(report_data['returned_products'][0])
    else:
        reports['returned_products'] = report_data['returned_products']

    redis_db.set('reports', json.dumps(reports))

    return 'Товар успешно возвращен на склад!'


print(return_product('001-1', 5))
print(sell_product('001-1', 2))
print(return_product('001-2', 5))
print(sell_product('001-2', 2))
