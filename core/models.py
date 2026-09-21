"""Site-wide content models: company info, testimonials, FAQs, contact messages."""

from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base adding created/updated timestamps to every model."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CompanyInfo(TimeStampedModel):
    """Singleton-style model holding the company details shown in the site."""

    name = models.CharField(max_length=120, default="AquaCare")
    tagline = models.CharField(max_length=200, default="Pure Water. Better Life.")
    about_short = models.TextField(blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    alternate_phone = models.CharField(max_length=30, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    business_hours = models.CharField(
        max_length=200, blank=True, default="Mon - Sat: 9:00 AM to 7:00 PM"
    )
    map_embed_url = models.URLField(
        blank=True,
        help_text="Google Maps embed URL (the src of the iframe).",
    )
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    youtube = models.URLField(blank=True)

    class Meta:
        verbose_name = "Company information"
        verbose_name_plural = "Company information"

    def __str__(self):
        return self.name

    @classmethod
    def get_solo(cls):
        """Return the single company record, creating it on first use."""
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create()
        return obj


class Testimonial(TimeStampedModel):
    name = models.CharField(max_length=120)
    designation = models.CharField(max_length=140, blank=True)
    city = models.CharField(max_length=80, blank=True)
    photo = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    rating = models.PositiveSmallIntegerField(default=5)
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return f"{self.name} ({self.rating}★)"

    @property
    def star_range(self):
        return range(self.rating)


class FAQ(TimeStampedModel):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class Statistic(TimeStampedModel):
    """Animated counters on the homepage (e.g. 25,000 happy customers)."""

    label = models.CharField(max_length=120)
    value = models.PositiveIntegerField(default=0)
    suffix = models.CharField(max_length=10, blank=True, help_text="e.g. + or %")
    icon = models.CharField(
        max_length=60, blank=True, help_text="Bootstrap icon name, e.g. bi-people"
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.label}: {self.value}"


class ContactMessage(TimeStampedModel):
    STATUS_NEW = "new"
    STATUS_READ = "read"
    STATUS_RESPONDED = "responded"
    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_READ, "Read"),
        (STATUS_RESPONDED, "Responded"),
    ]

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject}"
