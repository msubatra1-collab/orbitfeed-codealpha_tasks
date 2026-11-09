# ShopEase

ShopEase is a responsive Django storefront built with Django templates, vanilla JavaScript, and SQLite. It includes registration and sign-in (using either username or email), a searchable catalog, product detail pages, a persistent signed-in cart, checkout, order history, and Django admin. All catalog, cart, tax, and order amounts are displayed in Indian rupees (INR).

## Requirements

- Python 3.10 or newer
- `pip`

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_products
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. The `seed_products` command creates or refreshes 20 sample products across Home, Tech, Style, and Wellness, with INR-denominated demo prices and Unsplash image URLs. It is safe to rerun. Static product photography requires an internet connection.

## Shopping flow

Browse the catalog as a guest, search/filter/sort products, and add them to a session bag. Create an account or sign in with your username or registered email to merge the guest bag into your database-backed cart. Checkout requires an authenticated account. Prices and the 10% tax are in INR. Cash on Delivery is the usable demo payment option; selecting Card is intentionally a no-charge demonstration and does not connect to a payment processor. Stock is rechecked when placing an order and order creation, stock deduction, and cart clearing are handled together in a database transaction. Every order appears in the account's order history.

## Admin

Visit `/admin/` and sign in with the superuser created above. Manage categories, products, users, and orders; order status can be edited in the list or order page.

## Tests and maintenance

```bash
python manage.py check
python manage.py test
python manage.py seed_products
```

The database file is `db.sqlite3` by default. Set `DJANGO_DB_PATH` to use a different SQLite file. Set `DJANGO_SECRET_KEY` and `DJANGO_DEBUG=false` for a non-development deployment; set `DJANGO_ALLOWED_HOSTS` to a comma-separated host list. Local plain-HTTP runserver uses ordinary local session cookies. The managed HTTPS preview is detected through its injected project ID and uses `SameSite=None; Secure` session/CSRF cookies for embedded login. Production containers collect static assets and serve them with WhiteNoise.

## Hosted preview and production data

The live preview runs the full Django app, but this project deliberately keeps the requested SQLite engine. A container's local filesystem is not durable across rebuilds or redeployments, so do not treat the hosted preview as a production order database. For durable hosted commerce, storage would need to move to a persistent database through an explicitly approved change. This preview uses a demo catalog and no real card payment service.
