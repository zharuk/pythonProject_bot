from aiogram.types import InputMediaPhoto


class Product:
    def __init__(self, name: str, description: str, sku: str, colors: str, sizes: str, price: float):
        self.name = name
        self.description = description
        self.sku = sku
        self.colors = colors.split()
        self.sizes = sizes.split()
        self.price = price
        self.variants = self.generate_variants()

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


def format_main_info(json_value: dict):
    response_text = f"➡ Название: {json_value['name']}\n" \
                    f"➡ Описание: {json_value['description']}\n" \
                    f"➡ Артикул: {json_value['sku']}\n" \
                    f"➡ Цвета: {', '.join(json_value['colors'])}\n" \
                    f"➡ Размеры: {', '.join(json_value['sizes'])}\n" \
                    f"➡ Цена: {json_value['price']}\n"
    return response_text


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
        message += f"✅ На складе: <b>{stock}</b>\n\n" if stock > 0 else '<b>❌ Нет в наличии</b>\n\n'
    return message


def generate_photos(variants: list) -> list:
    photos = [photo_id['id'] for photo_id in variants]
    media = [InputMediaPhoto(media=photo_id) for photo_id in photos]
    return media
