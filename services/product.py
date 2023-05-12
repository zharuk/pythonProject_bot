class Product:
    def __init__(self, name: str, description: str, sku: str, colors: str, sizes: str, price: float):
        self.name = name
        self.description = description
        self.sku = sku
        self.colors = colors.split()
        self.sizes = sizes.split()
        self.price = price
        self.photo_ids = None
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
