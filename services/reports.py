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

    # Получаем текущую дату и время
    current_date = datetime.datetime.now().strftime('%d.%m.%Y')
    current_time = datetime.datetime.now().strftime('%H:%M:%S')

    # Создаем словарь для отчета
    report = {
        'sku': sku,
        'quantity': quantity,
        'price': int(required['price']),
        'total': int(quantity) * int(required['price']),
        'time': current_time
    }

    # Получаем текущий отчет из базы данных
    report_data = redis_db.get('reports')
    if report_data is not None:
        # Если отчет уже существует, конвертируем его из JSON в словарь
        existing_report = json.loads(report_data)
        if current_date in existing_report:
            # Если для текущей даты уже есть запись в отчете, добавляем проданный товар к существующей записи
            existing_report[current_date]['sold_products'].append(report)
        else:
            # Если для текущей даты нет записи в отчете, создаем новую запись
            existing_report[current_date] = {'sold_products': [report]}
        # Обновляем отчет в базе данных
        redis_db.set('reports', json.dumps(existing_report))
    else:
        # Если отчет не существует, создаем новый отчет с текущей датой и проданным товаром
        new_report = {current_date: {'sold_products': [report]}}
        # Сохраняем отчет в базе данных
        redis_db.set('reports', json.dumps(new_report))

    return True


# Функция для возврата товара и формирования отчета
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

    # Добавляем возвращаемый товар на остатки
    required['stock'] += quantity

    # Обновляем остатки товара в базе данных
    redis_db.set(main_sku, json.dumps(main_product))

    # Получаем текущую дату и время
    current_date = datetime.datetime.now().strftime('%d.%m.%Y')
    current_time = datetime.datetime.now().strftime('%H:%M:%S')

    # Создаем словарь для отчета
    report = {
        'sku': sku,
        'quantity': quantity,
        'price': int(required['price']),
        'total': int(quantity) * int(required['price']),
        'time': current_time
    }

    # Получаем текущий отчет return_products из базы данных
    report_data = redis_db.get('reports')
    if report_data is not None:
        # Если отчет уже существует, конвертируем его из JSON в словарь
        existing_report = json.loads(report_data)
        if 'return_products' in existing_report:
            # Если есть запись return_products, добавляем возвращаемый товар к существующей записи
            existing_report['return_products'].append(report)
        else:
            # Если записи return_products нет, создаем новую запись
            existing_report['return_products'] = [report]
        # Обновляем отчет в базе данных
        redis_db.set('reports', json.dumps(existing_report))
    else:
        # Если отчет не существует, создаем новый отчет с записью return_products
        new_report = {'return_products': [report]}
        # Сохраняем отчет в базе данных
        redis_db.set('reports', json.dumps(new_report))

    return 'Товар успешно возвращен на остатки и добавлен в отчет return_products!'


# print(return_product('001-1', 5))
# print(return_product('001-2', 5))
#print(sell_product('001-2', 3))
# print(sell_product('001-1', 2))
# print(sell_product('001-1', 2))