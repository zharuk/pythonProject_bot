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
    finish = State()  # Состояние завершения добавления товара


# Класс для создания компании
class FSMCreateCompany(StatesGroup):
    name = State()
    currency = State()


# Класс для редактирования настроек компании
class FSMEditCompany(StatesGroup):
    name = State()
    currency = State()


class SellItemStates(StatesGroup):
    quantity = State()


class ReturnItemStates(StatesGroup):
    quantity = State()


class FSMEditProduct(StatesGroup):
    edit_name = State()
    edit_description = State()
    edit_sku = State()
    edit_color = State()
    edit_size = State()
    edit_price = State()
    edit_stock = State()
    edit_photo = State()
    edit_delete = State()


class FSMAddProductOne(StatesGroup):
    data = State()
    photo = State()