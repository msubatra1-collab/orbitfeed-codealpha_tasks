from django.contrib import admin
from .models import Category, CartItem, Product
from .money import format_inr


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price_inr", "stock", "created_at")
    list_filter = ("category",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("stock",)

    @admin.display(description="Price (INR)", ordering="price")
    def price_inr(self, obj):
        return format_inr(obj.price)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if field and db_field.name == "price":
            field.label = "Price (₹ INR)"
        return field


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity", "created_at")
    search_fields = ("user__username", "product__name")
