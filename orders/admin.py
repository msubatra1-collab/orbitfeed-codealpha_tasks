from django.contrib import admin
from .models import Order, OrderItem
from store.money import format_inr


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product", "quantity", "price_inr")
    readonly_fields = ("product", "quantity", "price_inr")

    @admin.display(description="Unit price (INR)")
    def price_inr(self, obj):
        return format_inr(obj.price)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_inr", "status", "payment_method", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("id", "user__username", "shipping_name", "shipping_phone")
    list_editable = ("status",)
    fields = ("user", "total_inr", "status", "shipping_name", "shipping_address", "shipping_city",
              "shipping_pincode", "shipping_phone", "payment_method", "created_at")
    readonly_fields = ("user", "total_inr", "payment_method", "created_at")
    inlines = [OrderItemInline]

    @admin.display(description="Total (INR)", ordering="total_amount")
    def total_inr(self, obj):
        return format_inr(obj.total_amount)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price_inr")
    search_fields = ("order__id", "product__name")
    fields = ("order", "product", "quantity", "price_inr")
    readonly_fields = fields

    @admin.display(description="Unit price (INR)", ordering="price")
    def price_inr(self, obj):
        return format_inr(obj.price)
