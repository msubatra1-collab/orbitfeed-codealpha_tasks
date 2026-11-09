from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from store.models import CartItem, Product
from .forms import CheckoutForm
from .models import Order, OrderItem


def _guest_or_user_cart(request):
    if request.user.is_authenticated:
        return list(request.user.cart_items.select_related("product").all())
    return []


@login_required
@require_http_methods(["GET", "POST"])
def checkout(request):
    cart_items = _guest_or_user_cart(request)
    if not cart_items:
        messages.info(request, "Your bag is empty — add something before checkout.")
        return redirect("cart_detail")
    subtotal = sum((item.product.price * item.quantity for item in cart_items), Decimal("0.00"))
    tax = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = subtotal + tax
    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                locked_items = list(CartItem.objects.select_for_update().filter(user=request.user).select_related("product"))
                if not locked_items:
                    messages.error(request, "Your bag is empty. Add an item before checkout.")
                    return redirect("cart_detail")
                locked_products = {}
                for item in locked_items:
                    product = Product.objects.select_for_update().get(pk=item.product_id)
                    if item.quantity > product.stock:
                        raise ValueError(f"Only {product.stock} of {product.name} remain. Update your bag and try again.")
                    locked_products[product.pk] = product
                current_subtotal = sum((locked_products[item.product_id].price * item.quantity for item in locked_items), Decimal("0.00"))
                current_tax = (current_subtotal * Decimal("0.10")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                order = form.save(commit=False)
                order.user = request.user
                order.total_amount = current_subtotal + current_tax
                order.save()
                for item in locked_items:
                    product = locked_products[item.product_id]
                    OrderItem.objects.create(order=order, product=product, quantity=item.quantity, price=product.price)
                    product.stock -= item.quantity
                    product.save(update_fields=["stock"])
                CartItem.objects.filter(user=request.user).delete()
        except ValueError as error:
            messages.error(request, str(error))
            return redirect("cart_detail")
        messages.success(request, f"Order #{order.pk} placed. Your confirmation is ready.")
        return redirect("order_confirmation", order_id=order.pk)
    return render(request, "orders/checkout.html", {
        "form": form, "cart_items": cart_items, "subtotal": subtotal, "tax": tax, "total": total,
    })


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), pk=order_id, user=request.user)
    return render(request, "orders/confirmation.html", {"order": order})


@login_required
def my_orders(request):
    orders = request.user.orders.prefetch_related("items__product").all()
    return render(request, "orders/my_orders.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), pk=order_id, user=request.user)
    return render(request, "orders/order_detail.html", {"order": order})
