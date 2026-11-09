from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=140)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    image = models.URLField(max_length=500)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "name"]
        indexes = [models.Index(fields=["category", "price"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.name


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="unique_user_cart_product"),
            models.CheckConstraint(condition=models.Q(quantity__gte=1), name="cart_quantity_at_least_one"),
        ]

    @property
    def line_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} × {self.product} ({self.user})"
