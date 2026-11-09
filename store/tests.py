from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from orders.models import Order, OrderItem
from .models import CartItem, Category, Product
from .money import format_inr


class ShopEaseFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Home")
        cls.product = Product.objects.create(
            name="Test Vase", slug="test-vase", description="A ceramic test vase.",
            price=Decimal("25.00"), image="https://images.unsplash.com/photo-test", category=cls.category, stock=5,
        )
        cls.user = User.objects.create_user(username="shopper", email="shopper@example.com", password="Valid!Passphrase947")

    def test_catalog_search_category_sort_and_detail(self):
        response = self.client.get(reverse("home"), {"q": "vase", "category": "home", "sort": "price_asc"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Vase")
        self.assertContains(response, "₹25.00")
        self.assertNotIn("X-Frame-Options", response.headers)
        detail = self.client.get(reverse("product_detail", kwargs={"slug": self.product.slug}))
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "A ceramic test vase.")

    def test_guest_cart_merges_into_database_cart_after_login(self):
        add = self.client.post(reverse("cart_add", kwargs={"product_id": self.product.pk}), {"quantity": 2})
        self.assertRedirects(add, reverse("cart_detail"))
        login = self.client.post(reverse("login"), {"username": "shopper", "password": "Valid!Passphrase947"})
        self.assertRedirects(login, reverse("profile"))
        self.assertEqual(CartItem.objects.get(user=self.user, product=self.product).quantity, 2)
        self.assertNotIn("guest_cart", self.client.session)

    def test_login_accepts_username_or_case_insensitive_email(self):
        for identifier in (self.user.username, self.user.email.upper()):
            client = Client()
            response = client.post(reverse("login"), {
                "username": identifier, "password": "Valid!Passphrase947",
            })
            self.assertRedirects(response, reverse("profile"))
            self.assertEqual(client.session.get("_auth_user_id"), str(self.user.pk))

    def test_inr_formatter_uses_indian_digit_grouping(self):
        self.assertEqual(format_inr(Decimal("123456.78")), "₹1,23,456.78")
        self.assertEqual(format_inr(Decimal("1799")), "₹1,799.00")

    def test_login_required_for_checkout_and_orders(self):
        response = self.client.get(reverse("checkout"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
        self.client.force_login(self.user)
        response = self.client.get(reverse("my_orders"))
        self.assertEqual(response.status_code, 200)

    def test_invalid_cart_quantity_and_out_of_stock_are_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("cart_add", kwargs={"product_id": self.product.pk}), {"quantity": "-3"})
        self.assertRedirects(response, reverse("product_detail", kwargs={"slug": self.product.slug}))
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())
        self.product.stock = 0
        self.product.save(update_fields=["stock"])
        self.client.post(reverse("cart_add", kwargs={"product_id": self.product.pk}), {"quantity": "1"})
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())

    def test_checkout_creates_order_snapshots_reduces_stock_and_clears_cart(self):
        self.client.force_login(self.user)
        CartItem.objects.create(user=self.user, product=self.product, quantity=2)
        response = self.client.post(reverse("checkout"), {
            "shipping_name": "Avery Shopper", "shipping_address": "10 Garden Lane",
            "shipping_city": "Pune", "shipping_pincode": "411001", "shipping_phone": "+91 98765 43210",
            "payment_method": "cod",
        })
        order = Order.objects.get(user=self.user)
        self.assertRedirects(response, reverse("order_confirmation", kwargs={"order_id": order.pk}))
        self.assertEqual(order.total_amount, Decimal("55.00"))
        self.assertEqual(OrderItem.objects.get(order=order).price, Decimal("25.00"))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())
        self.assertEqual(order.status, Order.Status.PENDING)

    def test_checkout_rejects_stale_stock_and_preserves_cart(self):
        self.client.force_login(self.user)
        CartItem.objects.create(user=self.user, product=self.product, quantity=6)
        response = self.client.post(reverse("checkout"), {
            "shipping_name": "Avery Shopper", "shipping_address": "10 Garden Lane",
            "shipping_city": "Pune", "shipping_pincode": "411001", "shipping_phone": "9876543210",
            "payment_method": "card",
        })
        self.assertRedirects(response, reverse("cart_detail"))
        self.assertFalse(Order.objects.exists())
        self.assertEqual(CartItem.objects.get(user=self.user).quantity, 6)
        self.assertEqual(Product.objects.get(pk=self.product.pk).stock, 5)

    def test_confirmation_is_private_to_order_owner(self):
        order = Order.objects.create(
            user=self.user, total_amount=Decimal("27.50"), status=Order.Status.PENDING,
            shipping_name="Avery Shopper", shipping_address="10 Garden Lane", shipping_city="Pune",
            shipping_pincode="411001", shipping_phone="9876543210", payment_method="cod",
        )
        other_user = User.objects.create_user(username="other", password="Other!Passphrase812")
        self.client.force_login(other_user)
        response = self.client.get(reverse("order_confirmation", kwargs={"order_id": order.pk}))
        self.assertEqual(response.status_code, 404)

    def test_full_registered_shopping_flow(self):
        response = self.client.post(reverse("register"), {
            "username": "newshopper", "email": "newshopper@example.com",
            "password1": "Strong!Password1049", "password2": "Strong!Password1049",
        })
        self.assertRedirects(response, reverse("home"))
        user = User.objects.get(username="newshopper")
        self.assertTrue(self.client.session.get("_auth_user_id"))
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
        self.client.post(reverse("cart_add", kwargs={"product_id": self.product.pk}), {"quantity": 1})
        self.assertEqual(self.client.get(reverse("checkout")).status_code, 200)
        response = self.client.post(reverse("checkout"), {
            "shipping_name": "New Shopper", "shipping_address": "42 Market Road",
            "shipping_city": "Mumbai", "shipping_pincode": "400001", "shipping_phone": "9876543210",
            "payment_method": "card",
        })
        order = Order.objects.get(user=user)
        self.assertRedirects(response, reverse("order_confirmation", kwargs={"order_id": order.pk}))
        confirmation = self.client.get(reverse("order_confirmation", kwargs={"order_id": order.pk}))
        self.assertEqual(confirmation.status_code, 200)
        self.assertContains(confirmation, f"#{order.pk}")
        self.assertEqual(self.client.get(reverse("my_orders")).status_code, 200)

    def test_csrf_required_for_state_changing_cart_action(self):
        csrf_client = Client(enforce_csrf_checks=True)
        response = csrf_client.post(reverse("cart_add", kwargs={"product_id": self.product.pk}), {"quantity": 1})
        self.assertEqual(response.status_code, 403)

    def test_preview_internal_origin_is_accepted_with_valid_csrf_token(self):
        from django.test import override_settings
        with override_settings(CSRF_TRUSTED_ORIGINS=["http://127.0.0.1:3000"]):
            csrf_client = Client(enforce_csrf_checks=True)
            csrf_client.get(reverse("login"))
            token = csrf_client.cookies["csrftoken"].value
            response = csrf_client.post(
                reverse("cart_add", kwargs={"product_id": self.product.pk}),
                {"quantity": 1},
                HTTP_ORIGIN="http://127.0.0.1:3000",
                HTTP_X_CSRFTOKEN=token,
            )
            self.assertEqual(response.status_code, 302)
            self.assertEqual(CartItem.objects.count(), 0)
            self.assertEqual(csrf_client.session["guest_cart"][str(self.product.pk)], 1)

    def test_registration_checks_email_uniqueness_and_password_confirmation(self):
        mismatch = self.client.post(reverse("register"), {
            "username": "newperson", "email": "newperson@example.com",
            "password1": "Strong!Password1049", "password2": "Different!Password318",
        })
        self.assertEqual(mismatch.status_code, 200)
        self.assertFalse(User.objects.filter(username="newperson").exists())
        duplicate = self.client.post(reverse("register"), {
            "username": "anotherperson", "email": self.user.email,
            "password1": "Strong!Password1049", "password2": "Strong!Password1049",
        })
        self.assertEqual(duplicate.status_code, 200)
        self.assertFalse(User.objects.filter(username="anotherperson").exists())
        self.assertTrue(duplicate.context["form"].errors.get("email"))

    def test_route_manifest_is_valid_json_and_preview_has_no_frame_header(self):
        response = self.client.get("/manus-routes.json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(len(response.json()["routes"]), 11)
        home = self.client.get(reverse("home"))
        self.assertNotIn("X-Frame-Options", home.headers)
