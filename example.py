from jinja2 import Environment, FileSystemLoader

from main import JinjaRenderError, render

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("example.html")

PRODUCTS = [
    {"id": 1, "name": "Wireless Headphones Pro", "sku": "WH-1001", "category": "Audio", "price": "49.99", "original_price": "79.99", "tags": ["NEW", "WIRELESS", "BESTSELLER"], "image_url": "https://cdn.example.com/img/wh1001.jpg", "url": "https://shop.example.com/p/wh-1001"},
    {"id": 2, "name": "Mechanical Keyboard TKL", "sku": "KB-2048", "category": "Peripherals", "price": "89.99", "original_price": None, "tags": ["SALE", "LIMITED"], "image_url": "https://cdn.example.com/img/kb2048.jpg", "url": "https://shop.example.com/p/kb-2048"},
    {"id": 3, "name": "USB-C Hub 7-in-1", "sku": "HB-0731", "category": "Accessories", "price": "34.99", "original_price": "49.99", "tags": ["SALE"], "image_url": "https://cdn.example.com/img/hb0731.jpg", "url": "https://shop.example.com/p/hb-0731"},
    {"id": 4, "name": "27\" 4K Monitor", "sku": "MN-2700", "category": "Displays", "price": "299.99", "original_price": "399.99", "tags": ["NEW", "4K"], "image_url": "https://cdn.example.com/img/mn2700.jpg", "url": "https://shop.example.com/p/mn-2700"},
]

BASE_CTX = {
    "store_name": "TechDeals",
    "campaign_title": "Summer Sale — Up to 40% Off",
    "year": 2026,
    "unsubscribe_url": "https://shop.example.com/unsubscribe",
    "avg_rating": 4.3,
    "featured_ids": [1, 3],
    "highlight_tags": ["SALE", "NEW"],
    "products": PRODUCTS,
}

cases = [
    # for-loop: products list is None (e.g. DB query returned nothing)
    ("for-loop:   products=None",        {**BASE_CTX, "products": None}),
    # membership test: featured_ids set is None (e.g. feature-flag query failed)
    ("membership: featured_ids=None",    {**BASE_CTX, "featured_ids": None}),
    # filter mismatch: avg_rating is a string from the API instead of a float
    ("filter:     avg_rating='4.3'",     {**BASE_CTX, "avg_rating": "4.3"}),
    # include: highlight_tags is None — error surfaces inside the included snippet
    ("include:    highlight_tags=None",  {**BASE_CTX, "highlight_tags": None}),
]

for label, ctx in cases:
    print(f"=== {label} ===")
    try:
        render(template, **ctx)
    except JinjaRenderError as e:
        print(e)
    print()
