from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        SHIPPED = "Shipped", "Shipped"
        DELIVERED = "Delivered", "Delivered"

    class PaymentMethod(models.TextChoices):
        COD = "cod", "Cash on Delivery"
        CARD = "card", "Card (demo only)"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING, db_index=True)
    shipping_name = models.CharField(max_length=120)
    shipping_address = models.CharField(max_length=240)
    shipping_city = models.CharField(max_length=100)
    shipping_pincode = models.CharField(max_length=10)
    shipping_phone = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=8, choices=PaymentMethod.choices)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} — {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("store.Product", on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])

    class Meta:
        ordering = ["pk"]
        constraints = [models.CheckConstraint(condition=models.Q(quantity__gte=1), name="order_item_quantity_at_least_one")]

    @property
    def line_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} × {self.product}"
