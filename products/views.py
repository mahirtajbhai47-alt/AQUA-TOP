"""Product catalogue views: listing with search/filters, and product detail."""

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def _filtered_products(request, base_qs=None):
    """Apply search + filter query parameters to the product queryset."""
    qs = base_qs if base_qs is not None else Product.objects.filter(is_active=True)
    qs = qs.select_related("category")

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(name__icontains=q)
            | Q(sku__icontains=q)
            | Q(short_description__icontains=q)
            | Q(description__icontains=q)
            | Q(category__name__icontains=q)
            | Q(technology__icontains=q)
        )

    category = request.GET.get("category", "").strip()
    if category:
        qs = qs.filter(category__slug=category)

    technology = request.GET.get("technology", "").strip()
    if technology:
        qs = qs.filter(technology=technology)

    capacity = request.GET.get("capacity", "").strip()
    if capacity:
        qs = qs.filter(capacity__icontains=capacity)

    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    if min_price.isdigit():
        qs = qs.filter(price__gte=int(min_price))
    if max_price.isdigit():
        qs = qs.filter(price__lte=int(max_price))

    sort = request.GET.get("sort", "")
    if sort == "price_low":
        qs = qs.order_by("price")
    elif sort == "price_high":
        qs = qs.order_by("-price")
    elif sort == "newest":
        qs = qs.order_by("-created_at")
    elif sort == "name":
        qs = qs.order_by("name")

    return qs


def product_list(request):
    products = _filtered_products(request)
    paginator = Paginator(products, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    # Preserve filters across pagination links.
    params = request.GET.copy()
    params.pop("page", None)

    context = {
        "page_obj": page_obj,
        "products": page_obj.object_list,
        "categories": Category.objects.filter(is_active=True),
        "technologies": Product.TECHNOLOGY_CHOICES,
        "querystring": params.urlencode(),
        "total_count": paginator.count,
        "page_title": "Water Purifiers & Purification Systems | AquaCare Products",
        "meta_description": "Browse AquaCare RO, UV, UF, alkaline, commercial and "
        "industrial water purification systems with full specifications and pricing.",
    }
    return render(request, "products/product_list.html", context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = _filtered_products(
        request, Product.objects.filter(is_active=True, category=category)
    )
    paginator = Paginator(products, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)

    context = {
        "category": category,
        "page_obj": page_obj,
        "products": page_obj.object_list,
        "categories": Category.objects.filter(is_active=True),
        "technologies": Product.TECHNOLOGY_CHOICES,
        "querystring": params.urlencode(),
        "total_count": paginator.count,
        "page_title": f"{category.name} | AquaCare",
        "meta_description": category.description[:300]
        or f"Explore AquaCare {category.name} with specifications and pricing.",
    }
    return render(request, "products/product_list.html", context)


def category_list(request):
    return render(
        request,
        "products/category_list.html",
        {
            "categories": Category.objects.filter(is_active=True),
            "page_title": "Product Categories | AquaCare",
            "meta_description": "Domestic, commercial and industrial water "
            "purification categories from AquaCare.",
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("images"),
        slug=slug,
        is_active=True,
    )
    related = (
        Product.objects.filter(is_active=True, category=product.category)
        .exclude(pk=product.pk)[:4]
    )
    context = {
        "product": product,
        "related_products": related,
        "page_title": product.meta_title or f"{product.name} | AquaCare",
        "meta_description": product.meta_description or product.short_description,
    }
    return render(request, "products/product_detail.html", context)
