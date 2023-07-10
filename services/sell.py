import re


# Проверяет что в строке только цифры и цифра не больше 100.
def check_int(quantity):
    if re.search(r'\D', quantity) or int(quantity) > 100:
        return False
    else:
        return True
