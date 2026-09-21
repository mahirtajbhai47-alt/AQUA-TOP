"""Root URL configuration for the AquaCare project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.views.static import serve
from django.urls import include, path, re_path

from core.sitemaps import (
    CategorySitemap,
    ProductSitemap,
    ServiceSitemap,
    StaticViewSitemap,
)
from core.views import robots_txt

sitemaps = {
    "static": StaticViewSitemap,
    "products": ProductSitemap,
    "categories": CategorySitemap,
    "services": ServiceSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("products/", include("products.urls")),
    path("services/", include("services.urls")),
    path("accounts/", include("accounts.urls")),
    path("shop/", include("orders.urls")),
    path("quote/", include("quotations.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps},
         name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
]

if settings.DEBUG:
    # Django's dev-only helper.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Single-server production (e.g. Render): serve admin-uploaded media through
    # Django's static file view. For high traffic, move media to S3/Cloudinary
    # with django-storages and delete this block.
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]

# Custom error pages
handler404 = "core.views.error_404"
handler500 = "core.views.error_500"
handler403 = "core.views.error_403"
