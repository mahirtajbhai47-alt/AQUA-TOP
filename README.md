# AquaCare — Water Purifier Manufacturing, Sales & Maintenance

A complete, production-ready **Django 5** website for a water purification company:
product catalogue, e-commerce cart & orders, service booking with technician
assignment and live tracking, AMC plans, quotations, contact management and a
fully customised Django admin panel.

Built with **Django + Bootstrap 5 + vanilla JavaScript** — no React, no Node.js.
##Site live at:
-https://aqua-top.onrender.com/


---

## Table of contents

1. [Features](#features)
2. [Tech stack](#tech-stack)
3. [Project structure](#project-structure)
4. [Run locally](#run-locally)
5. [Admin panel guide](#admin-panel-guide)
6. [Push to GitHub](#push-to-github)
7. [Deploy on Render](#deploy-on-render)
8. [Environment variables](#environment-variables)
9. [Adding online payments later](#adding-online-payments-later)

---

## Features

### Customer facing
- **Home page** — hero with animated bubbles, company intro, why-choose-us,
  categories, featured products, services, animated statistics counters,
  AMC plans, testimonials, FAQ accordion and CTA. Every block is database-driven.
- **Product catalogue** — category browsing, keyword search (name, SKU, category,
  technology), filters (category, technology, capacity, price range), sorting and
  pagination.
- **Product detail** — image gallery, tabbed description / specifications /
  features / installation info, plus working **Buy Now**, **Add to Cart**,
  **Request Quote**, **Book Installation** and **Book Service** actions.
- **Cart & checkout** — session cart, quantity updates, removal, checkout with
  address capture, Cash on Delivery / Pay on Service, stock decremented on order.
- **Service booking** — installation, repair and maintenance requests with
  optional photo/video upload. Every request gets a reference number.
- **Service tracking** — public tracking by reference plus a visual status
  timeline in the customer dashboard.
- **AMC** — database-driven Basic/Standard/Premium plans with subscription flow.
- **Quotations** — "Get a Quote" form saved to the database with admin workflow.
- **Accounts** — register, login (username *or* email), logout, password reset,
  password change, profile editing with avatar.
- **Dashboard** — orders, service requests, installations, AMC, quotations, profile.
- **Contact page** — Google Maps embed, business hours, WhatsApp button and a
  contact form saved to the database.
- **SEO** — per-page titles and meta descriptions, semantic headings, image alt
  text, slug URLs, `robots.txt` and a generated `sitemap.xml`.
- **Custom 404 / 500 / 403 pages.**

### Staff facing
- **Technician dashboard** (`/services/technician/`) — assigned jobs with customer
  details, address, problem and a status updater (Accepted → On the way →
  In progress → Completed).
- **Django admin** — manage products (with inline image galleries and bulk
  actions), categories, orders and order items, service requests (assign
  technicians, change status inline), technicians, AMC plans and subscriptions,
  quotations (set quoted amount and status), contact messages, testimonials,
  FAQs, statistics and company information. All changes appear on the frontend
  immediately.

---

## Tech stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Framework | Django 5.0 |
| Frontend | HTML5, CSS3, Bootstrap 5.3, vanilla JavaScript, Bootstrap Icons |
| Database (local) | SQLite |
| Database (production) | PostgreSQL via `DATABASE_URL` |
| Static files | WhiteNoise (compressed manifest storage) |
| Images | Pillow |
| Config | django-environ + dj-database-url |
| WSGI server | Gunicorn |

---

## Project structure

```
AQUA-TOP/
├── manage.py
├── requirements.txt
├── runtime.txt              # Python version for Render
├── build.sh                 # Render build script
├── render.yaml              # optional Render Blueprint
├── .env.example
├── .gitignore
│
├── config/                  # project settings
│   ├── settings.py
│   ├── urls.py              # root URLs, sitemap, robots, error handlers
│   ├── wsgi.py
│   └── asgi.py
│
├── core/                    # company info, testimonials, FAQs, contact, home/about
│   ├── models.py  views.py  forms.py  admin.py  urls.py
│   ├── sitemaps.py  context_processors.py
│   └── management/commands/seed_data.py
│
├── products/                # categories, products, product images
├── services/                # services, technicians, service requests, AMC
├── orders/                  # session cart, orders, order items
├── quotations/              # quotation requests
├── accounts/                # customer profiles, auth, dashboard
│
├── templates/
│   ├── base.html  home.html  about.html  contact.html  faq.html
│   ├── partials/            # navbar, footer, product card
│   ├── products/  services/  accounts/  orders/  quotations/
│   ├── dashboard/           # customer dashboard pages
│   └── errors/              # 404 / 500 / 403
│
├── static/
│   ├── css/style.css        # complete water-themed design system
│   ├── js/main.js           # scroll reveal, counters, gallery, cart steppers
│   └── images/              # placeholder + sample product photos
│
└── media/                   # user/admin uploads (git-ignored)
```

---

## Run locally

### Windows

```bat
git clone YOUR_GITHUB_REPOSITORY_URL
cd AQUA-TOP

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env

python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser
python manage.py runserver
```

### macOS / Linux

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd AQUA-TOP

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser
python manage.py runserver
```

Then open:

| URL | Page |
|---|---|
| http://127.0.0.1:8000/ | Website home |
| http://127.0.0.1:8000/admin/ | Admin panel |
| http://127.0.0.1:8000/services/technician/ | Technician dashboard |

> `python manage.py seed_data` loads **7 categories, 12 products (with photos),
> 5 services, 3 AMC plans, 5 testimonials, 6 FAQs, 4 statistics and 3
> technicians**. It is safe to run more than once — it will not duplicate rows.

### Making the technician dashboard work

1. In the admin, create a user (e.g. `arun`) under **Authentication → Users**.
2. Open **Services → Technicians**, pick a technician and set the **User** field
   to that account.
3. Log in as that user and visit `/services/technician/`.

---

## Admin panel guide

| Task | Where |
|---|---|
| Add / edit / delete a product | Products → Products |
| Change a price or stock quickly | Products → Products (editable in the list view) |
| Upload extra gallery images | Products → Products → *Product images* inline |
| Add a category | Products → Categories |
| Assign a technician to a job | Services → Service requests (editable in the list) |
| Update service status | Services → Service requests |
| Create / edit AMC plans | Services → AMC plans |
| Quote an amount on an enquiry | Quotations → Quotations |
| Read contact form messages | Core → Contact messages |
| Edit phone, address, social links | Core → Company information |
| Add testimonials / FAQs / statistics | Core → Testimonials / FAQs / Statistics |
| See customer registrations | Authentication → Users (profile shown inline) |

Everything saved here renders on the public site immediately — nothing is
hard-coded in the templates.

---

## Push to GitHub

```bash
git init
git add .
git commit -m "Initial AquaCare website"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

`.gitignore` already excludes `.env`, `db.sqlite3`, `__pycache__/`, `venv/`,
`staticfiles/` and `media/`, so no secrets or generated files are committed.

---

## Deploy on Render

### Option A — Blueprint (fastest)

This repo includes `render.yaml`. In Render choose **New → Blueprint**, point it
at your GitHub repository and approve. Render creates the web service *and* a
free PostgreSQL database and wires `DATABASE_URL` automatically.

### Option B — Manual setup

**1. Create the database**

Render Dashboard → **New → PostgreSQL** → name it `aquacare-db` → Create.
Copy the **Internal Database URL**.

**2. Create the web service**

Render Dashboard → **New → Web Service** → connect your GitHub repo, then set:

| Field | Value |
|---|---|
| Runtime | Python 3 |
| Build Command | `./build.sh` |
| Start Command | `gunicorn config.wsgi:application` |

**3. Add environment variables** (Environment tab)

| Key | Value |
|---|---|
| `SECRET_KEY` | a long random string (use Render's *Generate* button) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://your-app.onrender.com` |
| `DATABASE_URL` | the Internal Database URL from step 1 |
| `DATABASE_SSL_REQUIRE` | `True` |
| `SECURE_SSL_REDIRECT` | `True` |
| `PYTHON_VERSION` | `3.11.9` |
| `TIME_ZONE` | `Asia/Kolkata` (optional) |

`RENDER_EXTERNAL_HOSTNAME` is injected by Render automatically and is appended to
`ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` by `settings.py`.

**4. Deploy.** `build.sh` installs dependencies, runs `collectstatic`, applies
migrations and seeds the sample data.

**5. Create your admin user.** Open the service **Shell** tab and run:

```bash
python manage.py createsuperuser
```

**Notes on media files:** Render's free disk is ephemeral, so admin-uploaded
images are lost on redeploy. The sample product photos ship inside `static/` and
survive deploys. For permanent uploads, attach a Render **Persistent Disk**
mounted at `/opt/render/project/src/media`, or switch to S3/Cloudinary via
`django-storages`.

---

## Environment variables

All configuration is read from the environment (see `.env.example`). Nothing
secret is committed.

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `SECRET_KEY` | production | insecure dev key | Django cryptographic signing |
| `DEBUG` | no | `False` | Debug mode — must be `False` in production |
| `ALLOWED_HOSTS` | production | `*` | Comma-separated allowed hostnames |
| `CSRF_TRUSTED_ORIGINS` | production | empty | Comma-separated `https://…` origins |
| `DATABASE_URL` | production | SQLite file | PostgreSQL connection string |
| `DATABASE_SSL_REQUIRE` | production | `False` | Require SSL to the database |
| `SECURE_SSL_REDIRECT` | no | `False` | Force HTTPS redirects |
| `TIME_ZONE` | no | `Asia/Kolkata` | Server timezone |
| `EMAIL_*` | no | console backend | SMTP settings for password-reset mail |

Security enabled automatically when `DEBUG=False`: HSTS, secure session and CSRF
cookies, content-type nosniff, clickjacking protection and proxy SSL header
handling. CSRF protection and Django's PBKDF2 password hashing are always on.

---

## Adding online payments later

The `Order` model already carries `payment_method`, `payment_status` and
`payment_reference`, and `PAYMENT_METHOD_CHOICES` includes an `online` option
(hidden in the checkout form for now). To add Razorpay:

1. `pip install razorpay` and add keys as environment variables.
2. Re-enable the `online` choice in `orders/forms.py` → `CheckoutForm.__init__`.
3. Create the gateway order after `order.save()` in `orders/views.py::checkout`,
   store the gateway id in `payment_reference`, and add a webhook view that sets
   `payment_status = Order.PAYMENT_PAID`.

No model migration is required.

---

## License & content

All copy, product descriptions, FAQs and testimonials in this project are
original sample content written for AquaCare. Product photographs are
AI-generated placeholders. No text, imagery, branding or source code from any
existing company has been used — replace the sample data with your own before
going live.

© 2026 AquaCare. All Rights Reserved.
