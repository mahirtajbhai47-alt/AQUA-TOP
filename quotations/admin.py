from django.contrib import admin

from .models import Quotation


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ("reference", "name", "phone", "email", "product", "service",
                    "quantity", "status", "quoted_amount", "created_at")
    list_editable = ("status", "quoted_amount")
    list_filter = ("status", "created_at")
    search_fields = ("reference", "name", "phone", "email", "location",
                     "requirements", "message")
    readonly_fields = ("reference", "created_at", "updated_at")
    autocomplete_fields = ("product",)
    fieldsets = (
        ("Request", {"fields": ("reference", "customer", "name", "phone", "email")}),
        ("Interest", {"fields": ("product", "service", "quantity", "location",
                                 "requirements", "message")}),
        ("Handling", {"fields": ("status", "quoted_amount", "admin_notes",
                                 "created_at", "updated_at")}),
    )
