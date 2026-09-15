"""Service catalogue, technicians, service requests and AMC plans/subscriptions."""

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.text import slugify

from core.models import TimeStampedModel
from products.models import Product


class Service(TimeStampedModel):
    """A service offered by AquaCare (installation, repair, maintenance...)."""

    name = models.CharField(max_length=140, unique=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    short_description = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=60, blank=True, default="bi-tools")
    image = models.ImageField(upload_to="services/", blank=True, null=True)
    starting_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:160]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("services:service_detail", kwargs={"slug": self.slug})


class Technician(TimeStampedModel):
    """Field technician who can be assigned to service requests."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="technician",
        help_text="Link a login account so the technician can use the dashboard.",
    )
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    photo = models.ImageField(upload_to="technicians/", blank=True, null=True)
    area = models.CharField(max_length=140, blank=True)
    specialization = models.CharField(max_length=160, blank=True)
    experience_years = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.area})" if self.area else self.name


class AMCPlan(TimeStampedModel):
    """Annual Maintenance Contract plan."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    duration_months = models.PositiveIntegerField(default=12)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_services = models.PositiveIntegerField(default=2)
    filter_replacement = models.BooleanField(default=False)
    emergency_service = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    features = models.TextField(
        blank=True, help_text="One benefit per line - shown as a bullet list."
    )
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "price"]
        verbose_name = "AMC plan"
        verbose_name_plural = "AMC plans"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)

    @property
    def feature_list(self):
        return [f.strip() for f in self.features.splitlines() if f.strip()]


class ServiceRequest(TimeStampedModel):
    """A single customer request: installation, repair, maintenance or AMC visit."""

    TYPE_INSTALLATION = "installation"
    TYPE_REPAIR = "repair"
    TYPE_MAINTENANCE = "maintenance"
    TYPE_AMC = "amc"
    TYPE_CHOICES = [
        (TYPE_INSTALLATION, "Installation"),
        (TYPE_REPAIR, "Repair / Service"),
        (TYPE_MAINTENANCE, "Maintenance"),
        (TYPE_AMC, "AMC Visit"),
    ]

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_ASSIGNED = "assigned"
    STATUS_ACCEPTED = "accepted"
    STATUS_ON_THE_WAY = "on_the_way"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_ASSIGNED, "Technician Assigned"),
        (STATUS_ACCEPTED, "Accepted by Technician"),
        (STATUS_ON_THE_WAY, "On the Way"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    reference = models.CharField(max_length=20, unique=True, blank=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_requests",
    )
    request_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default=TYPE_REPAIR
    )
    service = models.ForeignKey(
        Service, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="requests",
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="service_requests",
    )

    # Contact details (kept on the request so guests can also book)
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=80, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    problem_description = models.TextField(
        blank=True, help_text="Describe the problem or any additional notes."
    )
    attachment = models.FileField(
        upload_to="service_requests/", blank=True, null=True,
        help_text="Optional photo or short video of the issue.",
    )
    preferred_date = models.DateField(default=timezone.now)
    preferred_time = models.CharField(
        max_length=40, blank=True, default="10:00 AM - 1:00 PM"
    )

    technician = models.ForeignKey(
        Technician, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="jobs",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    admin_notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} - {self.get_request_type_display()}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"SR{timezone.now():%y%m}{get_random_string(5, '0123456789')}"
        if self.status == self.STATUS_COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def status_color(self):
        return {
            self.STATUS_PENDING: "secondary",
            self.STATUS_CONFIRMED: "info",
            self.STATUS_ASSIGNED: "primary",
            self.STATUS_ACCEPTED: "primary",
            self.STATUS_ON_THE_WAY: "warning",
            self.STATUS_IN_PROGRESS: "warning",
            self.STATUS_COMPLETED: "success",
            self.STATUS_CANCELLED: "danger",
        }.get(self.status, "secondary")


class AMCSubscription(TimeStampedModel):
    """A customer's subscription to an AMC plan."""

    STATUS_PENDING = "pending"
    STATUS_ACTIVE = "active"
    STATUS_EXPIRED = "expired"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending Activation"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_EXPIRED, "Expired"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    reference = models.CharField(max_length=20, unique=True, blank=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="amc_subscriptions"
    )
    plan = models.ForeignKey(AMCPlan, on_delete=models.PROTECT, related_name="subscriptions")
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="amc_subscriptions",
    )
    phone = models.CharField(max_length=20)
    address = models.TextField()
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "AMC subscription"
        verbose_name_plural = "AMC subscriptions"

    def __str__(self):
        return f"{self.reference} - {self.plan.name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"AMC{timezone.now():%y%m}{get_random_string(4, '0123456789')}"
        if not self.end_date:
            # Approximate month length is fine for a contract end date.
            self.end_date = self.start_date + timezone.timedelta(
                days=30 * self.plan.duration_months
            )
        super().save(*args, **kwargs)
