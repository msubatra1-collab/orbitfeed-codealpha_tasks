from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import CartItem, Category, Product


def _cart_lines(request):
    if request.user.is_authenticated:
        items = request.user.cart_items.select_related("product", "product__category").all()
        return [{"product": item.product, "quantity": item.quantity, "line_total": item.line_total} for item in items]
    cart = request.session.get("guest_cart", {})
    product_ids = [int(pid) for pid in cart if str(pid).isdigit()]
    products = {product.pk: product for product in Product.objects.filter(pk__in=product_ids).select_related("category")}
    lines = []
    for pid, raw_quantity in cart.items():
        if not str(pid).isdigit() or int(pid) not in products:
            continue
        try:
            quantity = int(raw_quantity)
        except (TypeError, ValueError):
            continue
        if quantity > 0:
            product = products[int(pid)]
            lines.append({"product": product, "quantity": quantity, "line_total": product.price * quantity})
    return lines


def _money(amount):
    return Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _cart_totals(lines):
    subtotal = _money(sum((line["line_total"] for line in lines), Decimal("0.00")))
    tax = _money(subtotal * Decimal("0.10"))
    return subtotal, tax, _money(subtotal + tax)


def home(request):
    products = Product.objects.select_related("category").all()
    query = request.GET.get("q", "").strip()[:100]
    category_slug = request.GET.get("category", "").strip()
    sort = request.GET.get("sort", "newest")
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query))
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if sort == "price_asc":
        products = products.order_by("price", "name")
    elif sort == "price_desc":
        products = products.order_by("-price", "name")
    else:
        sort = "newest"
    page_obj = Paginator(products, 9).get_page(request.GET.get("page"))
    return render(request, "store/home.html", {
        "page_obj": page_obj,
        "products": page_obj.object_list,
        "categories": Category.objects.all(),
        "active_category": category_slug,
        "query": query,
        "sort": sort,
        "result_count": products.count(),
    })


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug)
    related = Product.objects.filter(category=product.category).exclude(pk=product.pk).order_by("-created_at")[:4]
    return render(request, "store/product_detail.html", {"product": product, "related_products": related})


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except (TypeError, ValueError):
        quantity = 0
    if quantity < 1:
        messages.error(request, "Choose a quantity of at least one.")
        return redirect("product_detail", slug=product.slug)
    if product.stock < 1:
        messages.error(request, "That item is currently out of stock.")
        return redirect("product_detail", slug=product.slug)
    if request.user.is_authenticated:
        item = CartItem.objects.filter(user=request.user, product=product).first()
        requested = (item.quantity if item else 0) + quantity
        if requested > product.stock:
            messages.error(request, f"Only {product.stock} available. Your cart was not changed.")
        elif item:
            item.quantity = requested
            item.save(update_fields=["quantity"])
            messages.success(request, f"{product.name} added to your bag.")
        else:
            CartItem.objects.create(user=request.user, product=product, quantity=quantity)
            messages.success(request, f"{product.name} added to your bag.")
    else:
        cart = request.session.get("guest_cart", {})
        try:
            existing = int(cart.get(str(product.pk), 0))
        except (TypeError, ValueError):
            existing = 0
        requested = existing + quantity
        if requested > product.stock:
            messages.error(request, f"Only {product.stock} available. Your cart was not changed.")
        else:
            cart[str(product.pk)] = requested
            request.session["guest_cart"] = cart
            request.session.modified = True
            messages.success(request, f"{product.name} added to your bag.")
    return redirect("cart_detail")


def cart_detail(request):
    lines = _cart_lines(request)
    subtotal, tax, total = _cart_totals(lines)
    return render(request, "store/cart.html", {"lines": lines, "subtotal": subtotal, "tax": tax, "total": total})


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    try:
        quantity = int(request.POST.get("quantity", "0"))
    except (TypeError, ValueError):
        quantity = 0
    if quantity < 1:
        messages.error(request, "Enter a quantity of at least one, or remove the item.")
    elif quantity > product.stock:
        messages.error(request, f"Only {product.stock} available. Your cart was not changed.")
    elif request.user.is_authenticated:
        item = CartItem.objects.filter(user=request.user, product=product).first()
        if item:
            item.quantity = quantity
            item.save(update_fields=["quantity"])
            messages.success(request, "Your bag has been updated.")
        else:
            messages.error(request, "That item is no longer in your bag.")
    else:
        cart = request.session.get("guest_cart", {})
        if str(product.pk) in cart:
            cart[str(product.pk)] = quantity
            request.session["guest_cart"] = cart
            request.session.modified = True
            messages.success(request, "Your bag has been updated.")
        else:
            messages.error(request, "That item is no longer in your bag.")
    return redirect("cart_detail")


@require_POST
def cart_remove(request, product_id):
    if request.user.is_authenticated:
        CartItem.objects.filter(user=request.user, product_id=product_id).delete()
    else:
        cart = request.session.get("guest_cart", {})
        cart.pop(str(product_id), None)
        request.session["guest_cart"] = cart
        request.session.modified = True
    messages.info(request, "Item removed from your bag.")
    return redirect("cart_detail")
