from django.contrib import admin

from .models import CompanyInfo, ContactMessage, FAQ, Statistic, Testimonial

admin.site.site_header = "AquaCare Administration"
admin.site.site_title = "AquaCare Admin"
admin.site.index_title = "Manage your water purifier business"


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "updated_at")
    fieldsets = (
        ("Identity", {"fields": ("name", "tagline", "about_short")}),
        ("Contact", {"fields": ("address", "phone", "alternate_phone", "whatsapp",
                                "email", "business_hours", "map_embed_url")}),
        ("Social", {"fields": ("facebook", "instagram", "twitter", "linkedin", "youtube")}),
    )

    def has_add_permission(self, request):
        # Only one company record is needed.
        return not CompanyInfo.objects.exists()


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "rating", "is_active", "order")
    list_editable = ("is_active", "order")
    list_filter = ("is_active", "rating")
    search_fields = ("name", "message", "city")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "is_active", "order")
    list_editable = ("is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("question", "answer")


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ("label", "value", "suffix", "is_active", "order")
    list_editable = ("value", "suffix", "is_active", "order")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "phone", "email", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "phone", "subject", "message")
    readonly_fields = ("name", "email", "phone", "subject", "message", "created_at")
    list_editable = ("status",)
