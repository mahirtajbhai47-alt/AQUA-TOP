"""Quotation request model."""

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

from core.models import TimeStampedModel
from products.models import Product
from services.models import Service


class Quotation(TimeStampedModel):
    STATUS_NEW = "new"
    STATUS_CONTACTED = "contacted"
    STATUS_QUOTED = "quoted"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_CONTACTED, "Contacted"),
        (STATUS_QUOTED, "Quoted"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_COMPLETED, "Completed"),
    ]

    reference = models.CharField(max_length=20, unique=True, blank=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="quotations",
    )
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="quotations"
    )
    service = models.ForeignKey(
        Service, on_delete=models.SET_NULL, null=True, blank=True, related_name="quotations"
    )
    quantity = models.PositiveIntegerField(default=1)
    location = models.CharField(max_length=160)
    requirements = models.TextField(blank=True)
    message = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    quoted_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"QT{timezone.now():%y%m}{get_random_string(5, '0123456789')}"
        super().save(*args, **kwargs)

    @property
    def status_color(self):
        return {
            self.STATUS_NEW: "secondary",
            self.STATUS_CONTACTED: "info",
            self.STATUS_QUOTED: "primary",
            self.STATUS_ACCEPTED: "success",
            self.STATUS_REJECTED: "danger",
            self.STATUS_COMPLETED: "success",
        }.get(self.status, "secondary")
