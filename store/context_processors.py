from .models import Category


def shop_context(request):
    count = 0
    if getattr(request, "user", None) and request.user.is_authenticated:
        count = sum(request.user.cart_items.values_list("quantity", flat=True))
    else:
        guest_cart = request.session.get("guest_cart", {})
        count = sum(int(quantity) for quantity in guest_cart.values() if str(quantity).isdigit())
    return {"cart_item_count": count, "nav_categories": Category.objects.all()}
