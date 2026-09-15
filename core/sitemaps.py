"""Sitemap definitions for SEO."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from products.models import Category, Product
from services.models import Service


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "core:home", "core:about", "core:contact", "core:faq",
            "products:product_list", "services:service_list", "services:amc_plans",
            "quotations:request_quote",
        ]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    priority = 0.9
    changefreq = "weekly"

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return Category.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class ServiceSitemap(Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return Service.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at
