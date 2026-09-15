"""Catalogue models: categories, products and product image galleries."""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.models import TimeStampedModel


class Category(TimeStampedModel):
    """Product category, e.g. Domestic RO, Commercial RO, Water Dispensers."""

    SEGMENT_CHOICES = [
        ("domestic", "Domestic Water Purifiers"),
        ("commercial", "Commercial Water Purifiers"),
        ("industrial", "Industrial Water Purification"),
        ("dispenser", "Water Dispensers"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    segment = models.CharField(max_length=20, choices=SEGMENT_CHOICES, default="domestic")
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    icon = models.CharField(
        max_length=60, blank=True, help_text="Bootstrap icon name, e.g. bi-droplet"
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:category_detail", kwargs={"slug": self.slug})

    @property
    def active_product_count(self):
        return self.products.filter(is_active=True).count()


class Product(TimeStampedModel):
    """A water purifier or related product sold by AquaCare."""

    TECHNOLOGY_CHOICES = [
        ("RO", "RO"),
        ("UV", "UV"),
        ("UF", "UF"),
        ("RO+UV", "RO + UV"),
        ("RO+UV+UF", "RO + UV + UF"),
        ("ALKALINE", "Alkaline RO"),
        ("OTHER", "Other / Custom"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    sku = models.CharField("Product code / SKU", max_length=40, unique=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    short_description = models.CharField(max_length=300)
    description = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    # Specifications
    capacity = models.CharField(max_length=80, blank=True, help_text="e.g. 15 LPH")
    technology = models.CharField(
        max_length=20, choices=TECHNOLOGY_CHOICES, default="RO+UV"
    )
    storage_capacity = models.CharField(max_length=80, blank=True, help_text="e.g. 8 L")
    dimensions = models.CharField(max_length=120, blank=True)
    weight = models.CharField(max_length=60, blank=True)
    warranty = models.CharField(max_length=120, blank=True, default="1 Year Warranty")
    features = models.TextField(
        blank=True, help_text="One feature per line - shown as a bullet list."
    )
    installation_info = models.TextField(
        blank=True, default="Free professional installation within 48 hours of delivery."
    )

    stock_quantity = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:200]
            slug, counter = base, 2
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:product_detail", kwargs={"slug": self.slug})

    # -- helpers ----------------------------------------------------------
    @property
    def final_price(self):
        """Price actually charged (discount price when present)."""
        return self.discount_price if self.discount_price else self.price

    @property
    def has_discount(self):
        return bool(self.discount_price and self.discount_price < self.price)

    @property
    def discount_percent(self):
        if not self.has_discount:
            return 0
        return int(round((self.price - self.discount_price) / self.price * 100))

    @property
    def in_stock(self):
        return self.stock_quantity > 0

    @property
    def feature_list(self):
        return [f.strip() for f in self.features.splitlines() if f.strip()]


class ProductImage(TimeStampedModel):
    """Additional gallery images for a product."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=160, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Image for {self.product.name}"
