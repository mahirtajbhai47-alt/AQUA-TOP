"""Order and order item models (Cash on Delivery / Pay on Service)."""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

from core.models import TimeStampedModel
from products.models import Product


class Order(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_PROCESSING = "processing"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_SHIPPED, "Shipped"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    PAYMENT_COD = "cod"
    PAYMENT_ONLINE = "online"
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_COD, "Cash on Delivery / Pay on Service"),
        (PAYMENT_ONLINE, "Online Payment"),
    ]

    PAYMENT_PENDING = "pending"
    PAYMENT_PAID = "paid"
    PAYMENT_FAILED = "failed"
    PAYMENT_REFUNDED = "refunded"
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, "Pending"),
        (PAYMENT_PAID, "Paid"),
        (PAYMENT_FAILED, "Failed"),
        (PAYMENT_REFUNDED, "Refunded"),
    ]

    order_id = models.CharField(max_length=20, unique=True, blank=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="orders",
    )
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80, blank=True)
    pincode = models.CharField(max_length=10)
    notes = models.TextField(blank=True)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default=PAYMENT_COD
    )
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_PENDING
    )
    # Placeholder fields so an online gateway (e.g. Razorpay) can be added later.
    payment_reference = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_id

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"AQ{timezone.now():%y%m%d}{get_random_string(4, '0123456789')}"
        super().save(*args, **kwargs)

    def recalculate_total(self, commit=True):
        total = sum((item.subtotal for item in self.items.all()), Decimal("0.00"))
        self.total_amount = total
        if commit:
            self.save(update_fields=["total_amount", "updated_at"])
        return total

    @property
    def status_color(self):
        return {
            self.STATUS_PENDING: "secondary",
            self.STATUS_CONFIRMED: "info",
            self.STATUS_PROCESSING: "primary",
            self.STATUS_SHIPPED: "warning",
            self.STATUS_DELIVERED: "success",
            self.STATUS_CANCELLED: "danger",
        }.get(self.status, "secondary")


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, related_name="order_items"
    )
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity
