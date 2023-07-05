import datetime
import json

from services.redis_server import create_redis_client, check_and_create_structure_reports

# Подключение к базе данных Redis
r = create_redis_client()


# Функция get_sales_today_report() для получения отчета по продажам из словаря reports за текущий день. Словарь
# reports имеет следующую структуру: reports = {'sold_products': {'date': [{'sku': sku, 'quantity': quantity,
# 'price': price, 'total': total, 'time': time}]}}. Функция формирует f строки вида "{sku(комплектации товара)} -{
# color} {size} - { quantity}шт. - Цена {price}грн. - всего продано {total}грн.". Если например за день продано 2
# комплектации товара с артикулом 001-1, то функция должна суммировать их количество и вернуть строку вида "001-1 -
# 5шт. - Цена 1000 - всего продано 5000". По такому же принципу функция должна сформировать отчет по возвратам
# товара. Если за день например было продано 2 одинаковых товара в разное время, то функция должна их суммировать и
# выводить в одну строку.


def get_sales_today_report():
    # Функция для получения отчета по продажам за текущий день. Слаживает все одинаковые товары, их количество и
    # сумму продаж. Возвращает список словарей.
    def get_sales_report_by_date(date):
        # Получаем отчет по продажам за день
        report_data = r.get('reports')
        if report_data is not None:
            # Если отчет уже существует, конвертируем его из JSON в словарь
            existing_report = json.loads(report_data)
            if 'sold_products' in existing_report:
                # Если есть запись sold_products, получаем проданный товар за день
                if date in existing_report['sold_products']:
                    current_date_data = existing_report['sold_products'][date]
        # Проходимся циклом по current_date_data и суммируем количество проданного товара а также общую сумму продаж
        # для товара с одинаковым артикулом
        sales_report = []
        for product in current_date_data:
            if len(sales_report) == 0:
                sales_report.append(product)
            else:
                is_exist = False
                for report in sales_report:
                    if report['sku'] == product['sku']:
                        report['quantity'] += product['quantity']
                        report['total'] += product['total']
                        is_exist = True
                        break
                if not is_exist:
                    sales_report.append(product)
        return sales_report

    # Функция для получения отчета по возвратам за текущий день. Слаживает все одинаковые товары, их количество и
    # сумму продаж. Возвращает список словарей. Работает так же как и функция get_sales_report_by_date()
    def get_return_report_by_date(date):
        # Получаем отчет по возвратам за день
        report_data = r.get('reports')
        if report_data is not None:
            # Если отчет уже существует, конвертируем его из JSON в словарь
            existing_report = json.loads(report_data)
            if 'return_products' in existing_report:
                # Если есть запись return_products, получаем возвращенный товар за день
                if date in existing_report['return_products']:
                    current_date_data = existing_report['return_products'][date]
        # Проходимся циклом по current_date_data и суммируем количество возвращенного товара а также общую сумму
        # продаж для товара с одинаковым артикулом
        return_report = []
        for product in current_date_data:
            if len(return_report) == 0:
                return_report.append(product)
            else:
                is_exist = False
                for report in return_report:
                    if report['sku'] == product['sku']:
                        report['quantity'] += product['quantity']
                        report['total'] += product['total']
                        is_exist = True
                        break
                if not is_exist:
                    return_report.append(product)
        return return_report

    def get_sales_total_by_date(date):
        # Получаем сумму продаж за день
        sales_total = 0
        sales_report = get_sales_report_by_date(date)
        for product in sales_report:
            sales_total += product['total']
        return sales_total

    def get_return_total_by_date(date):
        # Получаем сумму возвратов за день
        return_total = 0
        return_report = get_return_report_by_date(date)
        for product in return_report:
            return_total += product['total']
        return return_total

    # Получаем текущую дату
    current_date = datetime.datetime.now().strftime('%d.%m.%Y')
    # Получаем отчет по продажам за текущий день
    sales_report = get_sales_report_by_date(current_date)
    # Получаем отчет по возвратам за текущий день
    return_report = get_return_report_by_date(current_date)
    # Получаем сумму продаж за текущий день
    sales_total = get_sales_total_by_date(current_date)
    # Получаем сумму возвратов за текущий день
    return_total = get_return_total_by_date(current_date)
    # Получаем общую сумму за текущий день
    total = sales_total - return_total
    # Подсчет общего количества проданного товара
    total_for_sale = 0
    # Подсчет общего количества возвращенного товара
    total_for_return = 0
    # Формируем отчет
    report = f'Отчет за сегодня {current_date}\n\n<b>Продажи:</b>\n\n'
    for sale in sales_report:
        report += f"{sale['sku']} - {sale['quantity']}шт. - Цена {sale['price']}грн. - всего {sale['total']}грн.\n"
        total_for_sale += sale['quantity']
    report += f'Всего продано {total_for_sale} товаров на сумму {sales_total}грн.\n\n<b>Возвраты:</b>\n\n'
    for return_product in return_report:
        report += f"{return_product['sku']} - {return_product['quantity']}шт. - Цена {return_product['price']}грн. - " \
                  f"всего {return_product['total']}грн.\n"
        total_for_return += return_product['quantity']
    report += f'Всего возвращено {total_for_return} товара на сумму {return_total}грн.\n\nИтого касса за день 💰 с ' \
              f'учетом возвратов: {total}грн.'
    return report
