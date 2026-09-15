from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "segment", "product_count", "is_active", "order")
    list_editable = ("is_active", "order")
    list_filter = ("segment", "is_active")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Products")
    def product_count(self, obj):
        return obj.products.count()


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "name", "sku", "category", "price",
                    "discount_price", "stock_quantity", "is_featured", "is_active")
    list_display_links = ("thumbnail", "name")
    list_editable = ("price", "discount_price", "stock_quantity",
                     "is_featured", "is_active")
    list_filter = ("category", "technology", "is_featured", "is_active")
    search_fields = ("name", "sku", "short_description", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
    fieldsets = (
        ("Basic information", {
            "fields": ("name", "slug", "category", "sku", "image",
                       "short_description", "description")}),
        ("Pricing & stock", {"fields": ("price", "discount_price", "stock_quantity")}),
        ("Specifications", {
            "fields": ("capacity", "technology", "storage_capacity", "dimensions",
                       "weight", "warranty", "features", "installation_info")}),
        ("Visibility", {"fields": ("is_featured", "is_active")}),
        ("SEO", {"classes": ("collapse",), "fields": ("meta_title", "meta_description")}),
    )
    actions = ["make_featured", "remove_featured", "activate", "deactivate"]

    @admin.display(description="Image")
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:44px;border-radius:6px;" />', obj.image.url
            )
        return "—"

    @admin.action(description="Mark selected products as featured")
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description="Remove featured flag")
    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)

    @admin.action(description="Activate selected products")
    def activate(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Deactivate selected products")
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "alt_text", "order")
    list_filter = ("product",)
