from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category, Product

PRODUCTS = [
    ("Home", "Ribbed Ceramic Vase", "A sculptural stoneware vase with a soft matte glaze. Looks just as good holding a branch as it does on its own.", "1799.00", 18, "photo-1578500494198-246f612d3b3d"),
    ("Home", "Linen Table Runner", "A relaxed, washable flax-linen runner that brings a little texture to everyday meals.", "2299.00", 22, "photo-1600210492486-724fe5c67fb0"),
    ("Home", "Oak Desk Organizer", "Solid-oak compartments keep pens, notes, and small essentials neatly in reach.", "1499.00", 14, "photo-1494438639946-1ebd1d20bf85"),
    ("Home", "Scented Soy Candle", "A clean-burning soy candle with notes of cedar, citrus, and warm amber.", "899.00", 31, "photo-1602874801007-bd458bb1b8b6"),
    ("Home", "Woven Storage Basket", "A sturdy handwoven basket for throws, toys, or the things that never quite find a home.", "1799.00", 11, "photo-1595428774223-ef52624120d2"),
    ("Tech", "Wireless Headphones", "Comfort-first over-ear headphones with rich everyday sound and a fold-flat travel design.", "6999.00", 16, "photo-1505740420928-5e560c06d30e"),
    ("Tech", "Compact Bluetooth Speaker", "Room-filling sound in a small, easy-to-carry speaker with a tactile fabric finish.", "3999.00", 9, "photo-1608043152269-423dbba4e7e1"),
    ("Tech", "Minimal Desk Lamp", "A dimmable desk lamp with a focused warm beam and an uncluttered silhouette.", "4499.00", 13, "photo-1507473885765-e6ed057f782c"),
    ("Tech", "Everyday Smart Watch", "A lightweight activity watch with a clear display, daily movement tracking, and simple controls.", "8999.00", 8, "photo-1523275335684-37898b6baf30"),
    ("Tech", "USB-C Charging Hub", "A compact multi-port hub to make a laptop desk setup more useful without the cable sprawl.", "1999.00", 26, "photo-1583863788434-e58a36330cf0"),
    ("Style", "Canvas Weekender Bag", "A durable cotton-canvas overnight bag with room for a long weekend and pockets for the small stuff.", "4999.00", 12, "photo-1553062407-98eeb64c6a62"),
    ("Style", "Classic Leather Wallet", "A slim, full-grain leather wallet that carries the essentials and develops character over time.", "2999.00", 19, "photo-1627123424574-724758594e93"),
    ("Style", "Everyday Sunglasses", "Timeless rounded frames with UV400 lenses and a lightweight, comfortable fit.", "1999.00", 20, "photo-1511499767150-a48a237f0083"),
    ("Style", "Soft Knit Scarf", "A generously sized, soft-touch scarf that layers easily through cool mornings and late nights.", "2499.00", 17, "photo-1520903920243-00d872a2d1c9"),
    ("Style", "Canvas Low-Top Sneakers", "A clean, versatile canvas sneaker with a cushioned insole and sturdy rubber sole.", "3499.00", 15, "photo-1542291026-7eec264c27ff"),
    ("Wellness", "Insulated Water Bottle", "A double-wall stainless bottle that keeps cold drinks cold and fits comfortably in a day bag.", "999.00", 24, "photo-1602143407151-7111542de6e8"),
    ("Wellness", "Daily Journal", "An undated, lay-flat journal with a cloth cover and plenty of room to clear your head.", "599.00", 33, "photo-1544947950-fa07a98d237f"),
    ("Wellness", "Yoga Mat", "A supportive, non-slip mat with a steady grip for an unhurried stretch or a focused flow.", "1799.00", 10, "photo-1544367567-0f2fcb009e0b"),
    ("Wellness", "Ceramic Tea Cup Set", "Two easy-grip ceramic cups made for a proper pause and a second cup shared.", "1299.00", 21, "photo-1544787219-7f47ccb76574"),
    ("Wellness", "Cotton Sleep Mask", "A softly padded, breathable cotton eye mask that makes a little room for a better rest.", "499.00", 29, "photo-1520206183501-b80df61043c2"),
]


class Command(BaseCommand):
    help = "Load or refresh ShopEase's four-category INR sample catalog."

    def handle(self, *args, **options):
        category_cache = {}
        for category_name, name, description, price, stock, photo_id in PRODUCTS:
            if category_name not in category_cache:
                category_cache[category_name] = Category.objects.get_or_create(name=category_name)[0]
            category = category_cache[category_name]
            image = f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w=900&q=85"
            Product.objects.update_or_create(
                slug=slugify(name),
                defaults={"name": name, "description": description, "price": price,
                          "image": image, "category": category, "stock": stock},
            )
        self.stdout.write(self.style.SUCCESS(
            f"Catalog ready: {Product.objects.count()} products across {Category.objects.count()} categories (INR)."
        ))
