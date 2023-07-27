import datetime
from services.redis_server import create_redis_client, check_and_create_structure_reports, get_data_from_redis


# Функция get_sales_today_report() для получения отчета по продажам из словаря reports за текущий день.
async def get_sales_today_report(user_id: str | int):
    # Проверяем структуру reports функцией check_and_create_structure_reports
    await check_and_create_structure_reports(user_id)

    # Получаем данные пользователя из Redis
    data = await get_data_from_redis(user_id)
    reports_data = data['reports']

    # Получение сегодняшней даты
    today = datetime.datetime.today().strftime("%d.%m.%Y")

    # Получаем список проданных товаров за сегодня
    sold_products = reports_data[today]['sold_products']
    # Получаем список возвращенных товаров за сегодня
    return_products = reports_data[today]['return_products']

    # Формируем словарь по продажам
    report_sold = {}
    total_quantity = 0
    total_price = 0

    for product in sold_products:
        sku = product['sku']
        if sku not in report_sold:
            report_sold[sku] = {
                'name': product['name'],
                'sku': sku,
                'quantity': 0,
                'price': 0,
                'total': 0,
            }
        total_quantity += product['quantity']
        total_price += product['total']
        report_sold[sku]['quantity'] += product['quantity']
        report_sold[sku]['price'] = product['price']
        report_sold[sku]['total'] += product['total']

    # Формируем словарь по возвратам
    report_return = {}
    total_quantity_return = 0
    total_price_return = 0

    for product in return_products:
        sku = product['sku']
        if sku not in report_return:
            report_return[sku] = {
                'name': product['name'],
                'sku': sku,
                'quantity': 0,
                'price': 0,
                'total': 0,
            }
        total_quantity_return += product['quantity']
        total_price_return += product['total']
        report_return[sku]['quantity'] += product['quantity']
        report_return[sku]['price'] = product['price']
        report_return[sku]['total'] += product['total']

    # Формируем строку по продажам
    report_sold_str = f'<b>🫰 Продано товаров сегодня {today}</b>:\n\n'
    for product in report_sold.values():
        report_sold_str += f"{product['sku']} - {product['quantity']}шт. - Цена {product['price']}{data['currency']} - всего продано на {product['total']}{data['currency']}\n"
    report_sold_str += f'\nВсего продано товаров: {total_quantity}шт. на сумму {total_price}{data["currency"]}'

    # Формируем строку по возвратам
    report_return_str = f'\n\n<b>♻️ Возвращено товаров сегодня {today}</b>:\n\n'
    for product in report_return.values():
        report_return_str += f"{product['sku']} - {product['quantity']}шт. - Цена {product['price']}{data['currency']} - всего возвращено на {product['total']}{data['currency']}\n"
    report_return_str += f'\nВсего возвращено товаров: {total_quantity_return}шт. на сумму {total_price_return}{data["currency"]}'

    # Формируем строку "Чистая прибыль"
    report_profit_str = f'\n--------------------------------\n' \
                        f'\n\n💰 Чистая прибыль: <b>{total_price - total_price_return}{data["currency"]}</b>'
    # Возвращаем отчет по продажам и возвратам
    return report_sold_str + report_return_str + report_profit_str

