from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST
from store.models import CartItem, Product
from .forms import EmailOrUsernameAuthenticationForm, RegistrationForm


def _merge_guest_cart(request, user):
    cart = request.session.get("guest_cart", {})
    for product_id, raw_quantity in cart.items():
        try:
            quantity = int(raw_quantity)
            product = Product.objects.get(pk=int(product_id))
        except (TypeError, ValueError, Product.DoesNotExist):
            continue
        if quantity < 1 or product.stock < 1:
            continue
        item = CartItem.objects.filter(user=user, product=product).first()
        requested = min(product.stock, (item.quantity if item else 0) + quantity)
        if item:
            item.quantity = requested
            item.save(update_fields=["quantity"])
        else:
            CartItem.objects.create(user=user, product=product, quantity=requested)
    request.session.pop("guest_cart", None)
    request.session.modified = True


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect("profile")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        _merge_guest_cart(request, user)
        messages.success(request, "Your ShopEase account is ready. Let’s find something good.")
        return redirect("home")
    return render(request, "registration/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("profile")
    form = EmailOrUsernameAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        _merge_guest_cart(request, request.user)
        messages.success(request, "You’re signed in. Your bag is right where you left it.")
        next_url = request.POST.get("next") or request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return redirect(next_url)
        return redirect("profile")
    return render(request, "registration/login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "You have been signed out.")
    return redirect("home")


@login_required
def profile(request):
    recent_orders = request.user.orders.prefetch_related("items__product")[:8]
    return render(request, "users/profile.html", {"recent_orders": recent_orders})
