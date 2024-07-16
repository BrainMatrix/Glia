from dataclasses import dataclass, field


@dataclass
class Product:
    name: str
    price: float
    category: str = field(default="fruit")  # 使用 field 来提供默认值

    def __post_init__(self):
        if self.price <= 0:
            raise ValueError("价格必须大于0")
        self.description = f"{self.name} ({self.category}) - ${self.price}"


# 创建一个实例
try:
    product = Product(name="苹果", price=0.75)
    print(product.description)
except ValueError as e:
    print(e)
