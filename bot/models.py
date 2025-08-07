from dataclasses import dataclass

PRODUCTS = {
    "ABSOLUTE #1": 1990,
    "КОННЫЙ ДВОРЪ": 1990,
}

@dataclass
class Order:
    id: str
    telegram_id: int
    product_name: str
    size: str
    contact: str
    status: str
    created_at: str
