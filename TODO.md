# ShopEase delivery checklist

- [x] **Accounts, validation, and profile:** Register with username, email, password and confirm password. Support login by username or registered email (email case-insensitively), plus logout; require login for checkout and order pages. Validate forms in frontend JavaScript and in Django, show clear error and success messages, and provide a user profile page with order history. Use Django's built-in auth User model, password hashing, and CSRF protection.

- [x] **Catalog, discovery, and sample data:** Provide a Home/Shop product grid with image, name, price in INR, category, and Add to Cart button. Include search, category filter, low-to-high/high-to-low price sorting, and pagination. Seed the database with at least 15 realistic products across 4 categories, using free image URLs from Unsplash or placeholder images and INR-denominated demo prices.

- [x] **Product details:** Show a large image, name, description, INR price, stock availability, and category. Include a quantity selector and Add to Cart button, plus related products.

- [x] **Shopping cart:** Allow add, remove, and quantity updates. Show subtotal, 10% tax, and total in INR, updating live with JavaScript. Display a navbar cart badge with item count. Persist carts for logged-in users in the database.

- [x] **Checkout and order processing:** Require login. Collect shipping name, address, city, pincode, and phone. Offer Cash on Delivery and a dummy Card option with no real payment. Show all checkout and order amounts in INR. Placing an order creates Order and OrderItems, reduces product stock, and clears the cart. Show an order confirmation page with order ID and summary. Provide a My Orders page with Pending, Shipped, and Delivered statuses.

- [x] **Administration:** Use Django admin to manage Products, Categories, Users, and Orders; show product prices, order totals, and item prices in INR; allow admin to change the order status.

- [x] **Models and project organization:** Implement Category(name), Product(name, description, price, image, category, stock, created_at), CartItem(user, product, quantity), Order(user, total_amount, status, shipping details, payment_method, created_at), OrderItem(order, product, quantity, price), and users via Django's built-in auth User model. Organize a proper Django project with apps `store`, `users`, `orders`, `templates/`, `static/css`, `static/js`, and `media/`.

- [x] **Responsive storefront design:** Deliver a modern, clean, professional look with a consistent colour theme; sticky navbar with logo, search, cart and badge, and Login/Register or Profile/Logout; footer, hover effects, smooth transitions, and toast notifications. Keep CSS and JavaScript in separate static files and make the site responsive for mobile, tablet, and desktop.

- [x] **Dependencies, seed workflow, and documentation:** Provide `requirements.txt`, a repeatable seed script or fixture, and `README.md` with virtualenv, pip install, migrate, create superuser, load seed data, and runserver setup steps. Document that sample prices and all displayed totals use INR.

- [x] **Security and edge cases:** Apply CSRF protection, password hashing, and backend input validation. Handle empty cart, out-of-stock products, invalid quantities, and unauthorized access. Keep checkout totals and inventory operations server-validated.

- [x] **End-to-end quality and delivery:** Test the full flow: register, login by username or email, browse, add to cart, checkout, and view order; verify INR formatting and fix errors before delivery. Deliver complete source runnable with `python manage.py runserver`, deploy a live preview if possible, and include a short summary of what was built and how to run it.
