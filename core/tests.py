"""Smoke tests covering the critical customer journeys."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.models import ContactMessage
from orders.models import Order
from products.models import Category, Product
from quotations.models import Quotation
from services.models import ServiceRequest


class PublicPageTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Domestic RO")
        self.product = Product.objects.create(
            name="Test RO", category=self.category, sku="T-001",
            short_description="Short", description="Long", price=10000,
            stock_quantity=5, is_active=True, is_featured=True,
        )

    def test_public_pages_load(self):
        for url in [
            reverse("core:home"), reverse("core:about"), reverse("core:contact"),
            reverse("core:faq"), reverse("products:product_list"),
            reverse("products:category_list"), self.product.get_absolute_url(),
            reverse("services:service_list"), reverse("services:amc_plans"),
            reverse("quotations:request_quote"), reverse("orders:cart_detail"),
            "/sitemap.xml", "/robots.txt",
        ]:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_product_search_filters(self):
        response = self.client.get(reverse("products:product_list"), {"q": "T-001"})
        self.assertContains(response, "Test RO")

    def test_contact_form_saves_message(self):
        self.client.post(reverse("core:contact"), {
            "name": "Asha", "email": "a@example.com", "phone": "9876543210",
            "subject": "Enquiry", "message": "Need a purifier.",
        })
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_quotation_saves(self):
        self.client.post(reverse("quotations:request_quote"), {
            "name": "Asha", "phone": "9876543210", "email": "a@example.com",
            "product": self.product.pk, "quantity": 1, "location": "Pune",
            "requirements": "High TDS", "message": "",
        })
        self.assertEqual(Quotation.objects.count(), 1)

    def test_service_request_saves_with_reference(self):
        self.client.post(reverse("services:book_repair"), {
            "request_type": "repair", "product": self.product.pk, "name": "Asha",
            "phone": "9876543210", "email": "a@example.com", "address": "12 St",
            "city": "Pune", "pincode": "411001", "preferred_date": "2030-01-01",
            "preferred_time": "09:00 AM - 12:00 PM", "problem_description": "Leak",
        })
        sr = ServiceRequest.objects.get()
        self.assertTrue(sr.reference.startswith("SR"))

    def test_404_page(self):
        self.assertEqual(self.client.get("/does-not-exist/").status_code, 404)


class AccountTests(TestCase):
    def test_registration_saves_user_and_login_works(self):
        self.client.post(reverse("accounts:register"), {
            "first_name": "Asha", "last_name": "R", "username": "asha",
            "email": "asha@example.com", "phone": "9876543210", "city": "Pune",
            "password1": "AquaStrong!234", "password2": "AquaStrong!234",
        })
        user = User.objects.get(username="asha")
        self.assertEqual(user.profile.phone, "9876543210")
        self.client.logout()
        self.assertTrue(self.client.login(username="asha", password="AquaStrong!234"))
        self.assertEqual(self.client.get(reverse("accounts:dashboard")).status_code, 200)


class CartOrderTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Domestic RO")
        self.product = Product.objects.create(
            name="Test RO", category=category, sku="T-002",
            short_description="Short", description="Long", price=10000,
            stock_quantity=5, is_active=True,
        )

    def test_add_to_cart_and_checkout_creates_order(self):
        self.client.post(reverse("orders:cart_add", args=[self.product.id]), {"quantity": 2})
        self.assertContains(self.client.get(reverse("orders:cart_detail")), "Test RO")
        self.client.post(reverse("orders:checkout"), {
            "full_name": "Asha", "phone": "9876543210", "email": "a@example.com",
            "address": "12 St", "city": "Pune", "state": "MH", "pincode": "411001",
            "payment_method": "cod", "notes": "",
        })
        order = Order.objects.get()
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_amount, 20000)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 3)  # stock decremented

    def test_empty_cart_checkout_redirects(self):
        response = self.client.get(reverse("orders:checkout"))
        self.assertEqual(response.status_code, 302)
