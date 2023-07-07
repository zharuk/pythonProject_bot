from aiogram.filters.state import State, StatesGroup


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM для события добавления товара /add_handlers
class FSMAddProduct(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем при добавлении товара
    fill_name = State()  # Состояние ожидания ввода названия товара
    fill_description = State()  # Состояние ожидания ввода описания товара
    fill_sku = State()  # Состояние ожидания ввода артикула товара
    fill_colors = State()  # Состояние ожидания ввода цветов товара
    fill_sizes = State()  # Состояние ожидания ввода размеров товара
    fill_price = State()  # Состояние ожидания ввода цены товара
    fill_photo = State()  # Состояние ввода загрузки фото


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM для события показа товара /show_handlers
# Создаем класс состояний FSM
class SellItemStates(StatesGroup):
    quantity = State()


class ReturnItemStates(StatesGroup):
    quantity = State()
